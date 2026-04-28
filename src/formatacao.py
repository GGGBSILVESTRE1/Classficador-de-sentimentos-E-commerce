import re
import emoji
import unicodedata


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

    # pega qualque caracter que não seja palavra ou espaço, ou seja, pontuação, emojis, etc
    tokens_brutos = re.findall(r"\w+|[^\w\s]", texto)

    tokens_processados = []

    for token in tokens_brutos:
        # extração da feature de sentimento quando o token é totalmente maiusculo
        e_maiusculo = token.isupper() and len(token) > 1

        # remove caracteres repetidos mais de 2 vezes
        token_limpo = re.sub(r"(.)\1{2,}", r"\1\1", token)
        token_limpo = token_limpo.lower()  # transforma todos os tokens em minúsculo

        tokens_processados.append({"palavra": token_limpo, "e_maiusculo": e_maiusculo})

    return tokens_processados
