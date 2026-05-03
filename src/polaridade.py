import re
import unicodedata


# Escala usada:
#  3  = sentimento muito forte
#  2  = sentimento forte
#  1  = sentimento leve
# -1  = problema leve
# -2  = problema forte
# -3  = problema muito forte
PESOS_PALAVRAS = {
    # Positivos fortes
    "excelente": 3,
    "excelentes": 3,
    "perfeito": 3,
    "perfeita": 3,
    "perfeitos": 3,
    "perfeitas": 3,
    "maravilhoso": 3,
    "maravilhosa": 3,
    "maravilhosos": 3,
    "maravilhosas": 3,
    "fantastico": 3,
    "fantastica": 3,
    "espetacular": 3,
    "impecavel": 3,
    "excepcional": 3,
    "incrivel": 3,
    "amei": 3,
    "amou": 3,
    "adorei": 3,
    # Positivos medios
    "otimo": 2,
    "otima": 2,
    "otimos": 2,
    "otimas": 2,
    "top": 2,
    "show": 2,
    "lindo": 2,
    "linda": 2,
    "satisfeito": 2,
    "satisfeita": 2,
    "recomendo": 2,
    "recomendaria": 2,
    "aprovado": 2,
    "aprovada": 2,
    "superou": 2,
    "eficiente": 2,
    # Positivos leves
    "bom": 1,
    "boa": 1,
    "bons": 1,
    "boas": 1,
    "bonito": 1,
    "bonita": 1,
    "facil": 1,
    "pratico": 1,
    "pratica": 1,
    "agradavel": 1,
    "barato": 1,
    "barata": 1,
    "rapido": 1,
    "rapida": 1,
    "macio": 1,
    "macia": 1,
    "cheiroso": 1,
    "cheirosa": 1,
    "silencioso": 1,
    "silenciosa": 1,
    "confortavel": 1,
    "funciona": 1,
    "funcionou": 1,
    "gostei": 1,
    # Negativos muito fortes
    "pessimo": -3,
    "pessima": -3,
    "pessimos": -3,
    "pessimas": -3,
    "horrivel": -3,
    "horriveis": -3,
    "lixo": -3,
    "porcaria": -3,
    "odiei": -3,
    # Negativos fortes
    "ruim": -2,
    "ruins": -2,
    "defeito": -2,
    "defeitos": -2,
    "quebrado": -2,
    "quebrada": -2,
    "danificado": -2,
    "danificada": -2,
    "falso": -2,
    "falsa": -2,
    "falsificado": -2,
    "falsificada": -2,
    "fragil": -2,
    "fraco": -2,
    "fraca": -2,
    "decepcao": -2,
    "decepcionado": -2,
    "decepcionada": -2,
    "decepcionante": -2,
    "arrependi": -2,
    "arrependido": -2,
    "arrependida": -2,
    "vazando": -2,
    "vaza": -2,
    "quebrou": -2,
    "pifou": -2,
    "falhou": -2,
    "sumiu": -2,
    # Negativos leves
    "lento": -1,
    "lenta": -1,
    "demorou": -1,
    "demora": -1,
    "demorado": -1,
    "demorada": -1,
    "atrasado": -1,
    "atrasada": -1,
    "amassado": -1,
    "amassada": -1,
    "faltando": -1,
    "errado": -1,
    "errada": -1,
    "caro": -1,
    "cara": -1,
    "dificil": -1,
    "inferior": -1,
    "regular": -1,
}

# expressoes valem antes das palavras isoladas, assim evitando 2 analises diferentes
# sobre uma mesma expressao, como "nao vale a pena" e "vale a pena"
PESOS_EXPRESSOES = {
    # Positivas
    "vale a pena": 2,
    "valeu a pena": 2,
    "valeu a espera": 2,
    "show de bola": 2,
    "de boa qualidade": 2,
    "boa qualidade": 2,
    "otima qualidade": 3,
    "otimo custo beneficio": 3,
    "custo beneficio": 1,
    "chegou antes": 1,
    "entrega rapida": 1,
    "funciona bem": 1,
    "funciona muito bem": 2,
    "funciona perfeitamente": 2,
    # Negativas
    "nao vale a pena": -2,
    "nao recomendo": -2,
    "nao gostei": -2,
    "nao presta": -2,
    "nao funciona": -2,
    "nao funciona direito": -3,
    "deixou a desejar": -2,
    "deixa a desejar": -2,
    "meia boca": -1,
    "mais ou menos": -1,
    "quebra galho": -1,
    "uma porcaria": -3,
    "um lixo": -3,
    "veio com defeito": -3,
    "veio quebrado": -3,
    "veio quebrada": -3,
    "propaganda enganosa": -2,
    "dinheiro fora": -2,
    "joguei dinheiro fora": -3,
    "nao compraria": -2,
    "nunca mais": -2,
}

INTENSIFICADORES = {"muito", "muita", "super", "bem", "bastante", "demais", "tao"}
NEGACOES = {"nao", "nunca", "nem"}


# etapa de normalizacao do texto
def normalizar_texto(texto):
    """Padroniza o texto para comparar com os pesos cadastrados."""
    if not isinstance(texto, str):
        return ""

    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def classificar_polaridade(nota):
    if nota > 0:
        return "Positivo"
    if nota < 0:
        return "Negativo"
    return "Neutro / Desconhecido"


def pontuar_expressoes(texto):
    nota = 0.0
    # ordena as expressoes por tamanho para evitar que expressões menores sejam contadas antes das maiores
    for expressao, peso in sorted(
        PESOS_EXPRESSOES.items(), key=lambda item: len(item[0]), reverse=True
    ):
        padrao = rf"\b{re.escape(expressao)}\b"

        ocorrencias = re.findall(padrao, texto)

        if ocorrencias:
            nota += peso * len(ocorrencias)
            texto = re.sub(padrao, " ", texto)

    return nota, re.sub(r"\s+", " ", texto).strip()


# pegas as palavras que sobram depois de retirar as expressões, e pontua elas individualmente, considerando o contexto de intensificadores e negações
def calcular_nota_sentimento(expressao):
    """
    recebe uma expressao extraida, como 'produto muito bom',
    e devolve uma nota simples de polaridade.
    """
    texto = normalizar_texto(expressao)
    nota_final, texto_restante = pontuar_expressoes(texto)
    palavras = texto_restante.split()

    for indice, palavra in enumerate(palavras):
        if palavra not in PESOS_PALAVRAS:
            continue

        peso = float(PESOS_PALAVRAS[palavra])
        janela_anterior = palavras[max(0, indice - 2) : indice]

        if any(termo in INTENSIFICADORES for termo in janela_anterior):
            peso *= 1.5

        if any(termo in NEGACOES for termo in janela_anterior):
            peso *= -1

        nota_final += peso

    return {
        "expressao": expressao,
        "nota": nota_final,
        "categoria": classificar_polaridade(nota_final),
    }


def calcular_polaridade_opinioes(opinioes):
    """
    Recebe a lista gerada por extrair_opnioes() e calcula um resumo.
    """
    resultados = []

    for opiniao in opinioes:
        expressao = opiniao.get("expressao", "")
        resultado = calcular_nota_sentimento(expressao)
        resultado["regra"] = opiniao.get("regra")
        resultados.append(resultado)

    nota_total = sum(item["nota"] for item in resultados)
    media = nota_total / len(resultados) if resultados else 0.0

    return {
        "nota_total": nota_total,
        "media": media,
        "categoria": classificar_polaridade(nota_total),
        "opinioes": resultados,
    }


def calcular_polaridade_texto(texto):
    """
    atalho para extrair opinioes de um texto e ja calcular a polaridade.
    """
    from src.extracao_opnioes import extrair_opnioes
    from src.formatacao import limpar_texto_simbolico

    texto_limpo = limpar_texto_simbolico(texto)
    opinioes = extrair_opnioes(texto_limpo)

    if not opinioes:
        resultado = calcular_nota_sentimento(texto_limpo)
        return {
            "nota_total": resultado["nota"],
            "media": resultado["nota"],
            "categoria": resultado["categoria"],
            "opinioes": [
                {
                    "regra": "TEXTO_COMPLETO",
                    **resultado,
                }
            ]
            if resultado["nota"] != 0
            else [],
        }

    return calcular_polaridade_opinioes(opinioes)
