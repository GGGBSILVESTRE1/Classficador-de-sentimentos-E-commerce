import pandas as pd
from collections import Counter


def extrair_ngramas(coluna_tokens, n=2):
    # lista gigante que vai guardar todos os n-gramas de todos os reviews
    todos_ngramas = []

    # passa por cada review da sua coluna
    for lista_tokens in coluna_tokens:
        # garante que a linha não é vazia ou nula
        if isinstance(lista_tokens, list):
            #  extrai apenas os textos limpos dos seus dicionários
            palavras = []
            for t in lista_tokens:
                if isinstance(t, dict) and "palavra" in t:
                    palavras.append(t["palavra"])

            #  monta os N-gramas dessa frase específica
            for i in range(len(palavras) - n + 1):
                # junta as palavras com um espaço no meio
                ngrama = " ".join(palavras[i : i + n])
                todos_ngramas.append(ngrama)

    # conta  quantas vezes cada n-grama apareceu
    contagem = Counter(todos_ngramas)

    df_ngramas = pd.DataFrame(contagem.items(), columns=["expressao", "frequencia"])

    # 5. Ordena do mais frequente para o menos frequente
    df_ngramas = df_ngramas.sort_values(by="frequencia", ascending=False).reset_index(
        drop=True
    )

    return df_ngramas
