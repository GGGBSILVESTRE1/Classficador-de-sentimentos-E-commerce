import kagglehub
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests

from config import RAW_DIR, PROCESSED_DIR, DATASET_SPECS, STANDARD_COLUMNS, ColumnSpec, 


# Funções de download para cada tipo de fonte (GitHub, Kaggle, Octaprice)


def download_github_file(url: str, output_path: Path) -> Path:

    output_path.parent.mkdir(parents=True, exist_ok=True)
    response = requests.get(url, timeout=60)
    response.raise_for_status()  # Levanta erro se download falhar (status 404, 500, etc)
    output_path.write_bytes(response.content)  # Escreve o arquivo em disco
    return output_path


def download_kaggle_file(dataset: str, filename: str, output_path: Path) -> Path:
    """
    Faz download de um arquivo especifico de um dataset do Kaggle usando kagglehub.
    """
    dataset_path = Path(kagglehub.dataset_download(dataset))
    source_path = dataset_path / filename

    if not source_path.exists():
        # Fallback: procura em qualquer subpasta se arquivo nao esta no root
        matches = list(dataset_path.rglob(filename))
        if not matches:
            raise FileNotFoundError(
                f"Arquivo {filename!r} nao encontrado no dataset Kaggle {dataset!r}."
            )
        source_path = matches[0]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def download_octaprice_files(output_dir: Path) -> list[Path]:
    """
    Faz download de multiplos arquivos do Octaprice.

    O codigo faz uma request para a API do GitHub listando todos os arquivos,
    depois faz download apenas dos CSVs e JSONs (ignora outros tipos).
    """
    api_url = (
        "https://api.github.com/repos/octaprice/ecommerce-product-dataset/"
        "git/trees/main?recursive=1"
    )
    response = requests.get(api_url, timeout=60)
    response.raise_for_status()

    files = response.json().get("tree", [])
    # Filtra apenas arquivos (type=="blob") que sao CSV ou JSON
    dataset_paths = [
        item["path"]
        for item in files
        if item.get("type") == "blob"
        and item.get("path", "").lower().endswith((".csv", ".json"))
    ]

    # Faz download de cada arquivo
    downloaded_files = []
    for dataset_path in dataset_paths:
        raw_url = (
            "https://raw.githubusercontent.com/octaprice/ecommerce-product-dataset/"
            f"main/{dataset_path}"
        )
        downloaded_files.append(
            download_github_file(raw_url, output_dir / Path(dataset_path).name)
        )

    return downloaded_files


# Funções para encontrar colunas existentes com base nas opcoes definidas em ColumnSpec


def first_existing_column(
    columns: Iterable[str], candidates: Iterable[str]
) -> str | None:
    """
    Procura a primeira coluna que existe entre as opcoes.
    transforma columns em um dict com letras minusculas para facilitar comparação
    """
    column_lookup = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate.lower() in column_lookup:
            return column_lookup[candidate.lower()]
    return None


def existing_columns(columns: Iterable[str], candidates: Iterable[str]) -> list[str]:
    """
    Procura todas as colunas que existem entre as opcoes.

    """
    column_lookup = {column.lower(): column for column in columns}
    return [
        column_lookup[candidate.lower()]
        for candidate in candidates
        if candidate.lower() in column_lookup
    ]


# Funções para transformação e padronização dos dados


def build_review_column(df: pd.DataFrame, review_columns: list[str]) -> pd.Series:
    """
    Junta multiplas colunas de texto em uma so

    Etapa de normalização:
    - fillna(""): substitui valores vazios por string vazia (nao pode concatenar NaN)
    - astype(str): converte tudo para texto (alguns sao numeros)
    - str.strip(): remove espacos no inicio/fim
    """
    if len(review_columns) == 1:
        return df[review_columns[0]]

    text_parts = [
        df[column].fillna("").astype(str).str.strip() for column in review_columns
    ]
    review = text_parts[0]
    for part in text_parts[1:]:
        review = review.str.cat(part, sep=" ").str.strip()
    return review


def standardize_frame(
    df: pd.DataFrame,
    source_name: str,
    spec: ColumnSpec,
    available_columns: Iterable[str] | None = None,
) -> pd.DataFrame:
    """
    Etapas:
    1. Procura as colunas certas (review, score, product_name)
    2. Combina multiplas colunas se necessario
    3. Converte score para numero
    4. Remove linhas vazias ou invalidas
    5. Retorna SEMPRE com 4 colunas: review, score, product_name, source

    """
    columns = list(available_columns or df.columns)
    review_columns = existing_columns(columns, spec.review_parts) or existing_columns(
        columns, spec.review
    )
    score_column = first_existing_column(columns, spec.score)
    product_column = first_existing_column(columns, spec.product_name)

    if not review_columns or score_column is None:
        raise ValueError(
            f"Nao encontrei colunas de review e score para {source_name}. "
            f"Colunas disponiveis: {list(columns)}"
        )

    # Cria novo DataFrame com apenas as 4 colunas padrao
    filtered = pd.DataFrame(
        {
            "review": build_review_column(df, review_columns),
            "score": pd.to_numeric(df[score_column], errors="coerce"),
            "product_name": df[product_column] if product_column else pd.NA,
            "source": source_name,
        }
    )

    # Limpeza de dados: remove espacos extras, valores vazios, etc
    filtered["review"] = filtered["review"].astype("string").str.strip()
    filtered["product_name"] = filtered["product_name"].astype("string").str.strip()
    filtered = filtered.dropna(subset=["review", "score"])
    filtered = filtered[filtered["review"] != ""]
    return filtered[STANDARD_COLUMNS]


# Funções para leitura de arquivos e padronização (CSV, JSON)
# permite a leitura apenas das colunas necessarias, economizando memoria e tempo


def read_filtered_csv(
    path_or_url: str | Path, source_name: str, spec: ColumnSpec
) -> pd.DataFrame:
    """
    Le arquivo CSV e retorna apenas as colunas necessarias.

    """
    header = pd.read_csv(path_or_url, nrows=0)
    columns = header.columns

    review_columns = existing_columns(columns, spec.review_parts) or existing_columns(
        columns, spec.review
    )
    score_column = first_existing_column(columns, spec.score)
    product_column = first_existing_column(columns, spec.product_name)

    if not review_columns or score_column is None:
        raise ValueError(
            f"Nao encontrei colunas de review e score para {source_name}. "
            f"Colunas disponiveis: {list(columns)}"
        )

    # Remove duplicatas mantendo ordem: dict.fromkeys() e depois filtra None
    selected_columns = list(
        dict.fromkeys([*review_columns, score_column, product_column])
    )
    selected_columns = [column for column in selected_columns if column is not None]

    # Carrega apenas essas colunas
    df = pd.read_csv(path_or_url, usecols=selected_columns)
    return standardize_frame(df, source_name, spec, selected_columns)


def read_filtered_json(path: Path, source_name: str, spec: ColumnSpec) -> pd.DataFrame:
    """
    Le arquivo JSON e padroniza.

    """
    df = pd.read_json(path)
    return standardize_frame(df, source_name, spec)


def save_dataset(df: pd.DataFrame, source_name: str) -> Path:
    """
    Salva DataFrame padronizado como Parquet em data/processed/
    """
    output_path = PROCESSED_DIR / f"{source_name}_reviews.parquet"
    df.to_parquet(output_path, index=False)
    return output_path


def prepare_b2w() -> pd.DataFrame:
    """Prepara dados do B2W (GitHub)"""
    raw_path = RAW_DIR / "b2w_reviews.csv"
    download_github_file(
        "https://raw.githubusercontent.com/americanas-tech/b2w-reviews01/main/"
        "B2W-Reviews01.csv",
        raw_path,
    )
    return read_filtered_csv(raw_path, "b2w", DATASET_SPECS["b2w"])


def prepare_olist() -> pd.DataFrame:
    """Prepara dados do Olist (Kaggle)"""
    raw_path = RAW_DIR / "olist_order_reviews_dataset.csv"
    download_kaggle_file(
        "olistbr/brazilian-ecommerce",
        "olist_order_reviews_dataset.csv",
        raw_path,
    )
    return read_filtered_csv(raw_path, "olist", DATASET_SPECS["olist"])


def prepare_buscape() -> pd.DataFrame:
    """Prepara dados do Buscape (Kaggle)"""
    raw_path = RAW_DIR / "buscape.csv"
    download_kaggle_file(
        "fredericods/ptbr-sentiment-analysis-datasets",
        "buscape.csv",
        raw_path,
    )
    return read_filtered_csv(raw_path, "buscape", DATASET_SPECS["buscape"])


def prepare_octaprice() -> pd.DataFrame:
    """
    Prepara dados do Octaprice (multiplos JSONs).
    """
    raw_paths = download_octaprice_files(RAW_DIR / "octaprice")
    frames = []

    for raw_path in raw_paths:
        try:
            if raw_path.suffix.lower() == ".csv":
                frames.append(
                    read_filtered_csv(raw_path, "octaprice", DATASET_SPECS["octaprice"])
                )
            elif raw_path.suffix.lower() == ".json":
                frames.append(
                    read_filtered_json(
                        raw_path, "octaprice", DATASET_SPECS["octaprice"]
                    )
                )
        except ValueError as exc:
            # Se um arquivo nao tem as colunas certas, ignora e continua com os proximos
            print(f"Ignorando {raw_path.name}: {exc}")

    if not frames:
        print("Nenhum CSV compativel foi encontrado na base Octaprice.")
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    return pd.concat(frames, ignore_index=True)


# Função para baixar, preparar e salvar os dados de todas as fontes


def fetch_all_data() -> dict[str, Path]:
    """
    O que faz:
    1. Cria pastas necessarias
    2. Executa prepare_*() para cada fonte
    3. Salva cada dataset em data/processed/
    4. Opcionalmente combina tudo em um arquivo

    """

    preparers = {
        "b2w": prepare_b2w,
        "olist": prepare_olist,
        "buscape": prepare_buscape,
        "octaprice": prepare_octaprice,
    }

    saved_files = {}
    prepared_frames = []
    for source_name, prepare in preparers.items():
        print(f"Preparando {source_name}...")
        df = prepare()
        saved_files[source_name] = save_dataset(df, source_name)
        prepared_frames.append(df)
        print(f"{source_name}: {len(df)} linhas salvas em {saved_files[source_name]}")

    # Se combine=True, junta TODOS os DataFrames em um so

    return saved_files


if __name__ == "__main__":
    fetch_all_data()
