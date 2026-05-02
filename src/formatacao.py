import re
import emoji
import unicodedata
from collections import Counter
import pandas as pd

# Lista de stopwords que não entregam muito valor semântico para a análise
STOPWORDS = set(
    [
        "o",
        "a",
        "e",
        "do",
        "da",
        "de",
        "que",
        "em",
        "um",
        "uma",
        "para",
        "com",
        "na",
        "no",
        "os",
        "as",
        "é",
        "mas",
        "se",
        "produto",
        "eu",
        "por",
        "ja",
        "meu",
        "como",
        "esta",
        "ele",
        "ate",
        "pra",
        "pois",
        "minha",
        "mesmo",
        "foi",
        "ser",
        "ainda",
        "estou",
        "dia",
        "ao",
        "me",
        "ao",
        "esse",
        "ou",
        "pelo",
        "quando",
        "isso",
        "sao",
        "ter",
        "tenho",
        "fica",
        "antes",
        "ela",
        "usar",
        "dos",
        "das",
        "este",
        "tem",
        "sem",
        "uso",
        "quem",
        "essa",
        "agora",
    ]
)


def limpar_texto_simbolico(texto):
    # verifica se o texto é uma string, caso não seja, retornar uma string vazia
    if not isinstance(texto, str):
        return ""

    # remove os : para não confundir o
    texto = emoji.demojize(texto, language="pt").replace(
        ":", ""
    )  # converte emojis para texto

    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")

    texto = re.sub(r"\s+", " ", texto).strip()  # remove espaços extras

    return texto


def tokenizar_texto(texto):
    # verifica se o texto é uma string, caso não seja, retornar uma lista vazia
    if not isinstance(texto, str):
        return []

    tem_exclamacao = "!" in texto

    # pega qualque caracter que não seja palavra ou espaço, ou seja, pontuação, emojis, etc
    tokens_brutos = re.findall(r"\b\w+\b", texto)
    tokens_processados = []

    for token in tokens_brutos:
        # extração da feature de sentimento quando o token é totalmente maiusculo
        e_maiusculo = token.isupper() and len(token) > 1

        token_lower = token.lower()  # transforma todos os tokens em minúsculo

        if token_lower in STOPWORDS or len(token_lower) <= 1:
            continue

        # remove caracteres repetidos mais de 2 vezes
        token_limpo = re.sub(r"(.)\1{2,}", r"\1\1", token_lower)

        tokens_processados.append(
            {
                "palavra": token_limpo,
                "e_maiusculo": e_maiusculo,
                "tem_exclamacao": tem_exclamacao,
            }
        )

    return tokens_processados


# Função para extrair a frequência de palavras a partir da coluna de tokens
def extrair_frequencia(df_coluna_tokens):
    todas_as_palavras = []

    for lista_tokens in df_coluna_tokens:
        # verifica se a lista de tokens é uma lista, caso contrário ignora
        if isinstance(lista_tokens, list):
            for token_dict in lista_tokens:
                todas_as_palavras.append(token_dict["palavra"])

    contagem = Counter(todas_as_palavras)

    df_frequencia = pd.DataFrame(contagem.items(), columns=["palavra", "frequencia"])

    df_frequencia = df_frequencia.sort_values(
        by="frequencia", ascending=False
    ).reset_index(drop=True)

    return df_frequencia


def limpeza_texto_com_acento(texto):
    if not isinstance(texto, str):
        return ""

    texto = emoji.demojize(texto, language="pt").replace(":", " ")

    texto = re.sub(r"\s+", " ", texto).strip()  # remove espaços extras

    return texto
