import spacy
from spacy.matcher import Matcher


nlp = spacy.load("pt_core_news_sm", disable=["ner", "parser"])
matcher = Matcher(nlp.vocab)

# adjetivos de opniao comuns em reviews
ADJETIVOS_OPINIAO = [
    "bom",
    "boa",
    "bons",
    "boas",
    "otimo",
    "otima",
    "otimos",
    "otimas",
    "excelente",
    "excelentes",
    "perfeito",
    "perfeita",
    "perfeitos",
    "perfeitas",
    "ruim",
    "ruins",
    "pessimo",
    "pessima",
    "pessimos",
    "pessimas",
    "horrivel",
    "horriveis",
    "fraco",
    "fraca",
    "fracos",
    "fracas",
    "rapido",
    "rapida",
    "rapidos",
    "rapidas",
    "lento",
    "lenta",
    "lentos",
    "lentas",
    "lindo",
    "linda",
    "lindos",
    "lindas",
    "satisfeito",
    "satisfeita",
    "caro",
    "cara",
    "caros",
    "caras",
    "barato",
    "barata",
    "baratos",
    "baratas",
    "original",
    "lixo",
]
# alguns produtos em comum em reviews para ajudar a identificar opniões
SUBSTANTIVOS_AVALIADOS = [
    "produto",
    "entrega",
    "qualidade",
    "preco",
    "atendimento",
    "compra",
    "material",
    "imagem",
    "som",
    "bateria",
    "tela",
    "loja",
    "embalagem",
    "design",
    "designer",
]
# adverbios intensificadores comuns
INTENSIFICADORES = ["muito", "muita", "bem", "super", "bastante", "tao"]
NEGACOES = ["nao", "nunca", "nem"]
# verbos comuns em opnioes de reviews
VERBOS_AVALIACAO = [
    "gostei",
    "recomendo",
    "funciona",
    "funcionou",
    "vale",
    "presta",
    "compraria",
    "atendeu",
    "serviu",
    "chegou",
    "veio",
    "compensa",
]
# verbos comuns em opnioes positivas
VERBOS_POSITIVOS = [
    "gostei",
    "adorei",
    "amei",
    "amou",
    "recomendo",
    "recomendaria",
    "aprovado",
    "aprovada",
]
# palavras que indicam problemas no recebimento do produto
PROBLEMAS_RECEBIMENTO = [
    "defeito",
    "quebrado",
    "quebrada",
    "danificado",
    "danificada",
    "amassado",
    "amassada",
    "errado",
    "errada",
    "faltando",
    "vazando",
]
# verbos que indicam problemas de funcionamento ou qualidade do produto
VERBOS_PROBLEMA = ["vaza", "vazando", "quebrou", "pifou", "sumiu", "falhou"]
# avaliações de funcionamento comuns em reviews
AVALIACOES_FUNCIONAMENTO = ["bem", "perfeitamente", "direito", "normalmente"]
# adjetivos comuns para falar sobre a entrega do produto, tanto negativos quanto positivos
ADJETIVOS_ENTREGA = [
    "rapido",
    "rapida",
    "atrasado",
    "atrasada",
    "demorado",
    "demorada",
]

# regras de opnioes coloquiais positivas, como 'show de bola' ou 'top' e alguns regionalismos como 'arretado'
matcher.add(
    "OPINIAO_COLOQUIAL_POSITIVA",
    [
        [{"LOWER": "show"}, {"LOWER": "de"}, {"LOWER": "bola"}],
        [{"LOWER": {"IN": SUBSTANTIVOS_AVALIADOS}}, {"LOWER": "top"}],
        [
            {"LOWER": {"IN": ["muito", "bem"]}},
            {"LOWER": {"IN": ["top", "massa", "bacana", "legal"]}},
        ],
        [{"LOWER": "baita"}, {"LOWER": {"IN": SUBSTANTIVOS_AVALIADOS}}],
        [{"LOWER": {"IN": ["arretado", "arretada", "arretados", "arretadas"]}}],
    ],
)

# regras de opnioes coloquiais negativas, como 'meia boca' ou 'quebra galho'
matcher.add(
    "OPINIAO_COLOQUIAL_NEGATIVA",
    [
        [{"LOWER": "meia"}, {"LOWER": "boca"}],
        [{"LOWER": "quebra"}, {"LOWER": "galho"}],
        [{"LOWER": {"IN": NEGACOES}}, {"LOWER": "presta"}],
        [{"LOWER": {"IN": ["uma", "um"]}}, {"LOWER": "porcaria"}],
        [{"LOWER": "lixo"}],
        [{"LOWER": {"IN": ["furada"]}}],
        [
            {
                "LOWER": {
                    "IN": [
                        "arrependi",
                        "arrependido",
                        "arrependida",
                        "decepcionado",
                        "decepcionada",
                        "decepcionante",
                    ]
                }
            }
        ],
    ],
)

# regra direta de opinião, como 'produto ruim' ou 'entrega rápida'
matcher.add(
    "OPINIAO_DIRETA_POS",
    [
        [
            {"LOWER": {"IN": SUBSTANTIVOS_AVALIADOS}},
            {"POS": "ADJ", "LOWER": {"NOT_IN": INTENSIFICADORES}},
        ],
        [
            {"POS": "ADJ", "LOWER": {"NOT_IN": INTENSIFICADORES}},
            {"LOWER": {"IN": SUBSTANTIVOS_AVALIADOS}},
        ],
    ],
)


# regra de opnião onde o adjetivo de opnião vem antes como  'otimo produto'
matcher.add(
    "OPINIAO_ADJETIVO_SUBSTANTIVO",
    [
        [
            {"LOWER": {"IN": ADJETIVOS_OPINIAO}},
            {"LOWER": {"IN": SUBSTANTIVOS_AVALIADOS}},
        ],
    ],
)

# regra de opnião onde o adjetivo de opnião vem depois como 'entrega rápida'
matcher.add(
    "OPINIAO_QUALIDADE",
    [
        [
            {"LOWER": {"IN": ["de", "com"]}},
            {"LOWER": {"IN": ADJETIVOS_OPINIAO}},
            {"LOWER": {"IN": ["qualidade", "acabamento"]}},
        ],
    ],
)
# regra de opniãoonde o adjetivo é intensificado por um advérbio, como 'muito bom'
matcher.add(
    "OPINIAO_INTENSIFICADA",
    [
        [
            {
                "LOWER": {"IN": SUBSTANTIVOS_AVALIADOS}
            },  # 1. Trava na sua lista de produtos
            {
                "LOWER": {"IN": INTENSIFICADORES},
                "OP": "+",
            },  # 2. Exige 1 ou mais intensificadores
            {
                "POS": "ADJ"
            },  # 3. A MÁGICA: Pega literalmente qualquer adjetivo que existir!
        ],
        [
            {"LOWER": {"IN": INTENSIFICADORES}, "OP": "+"},
            {"POS": "ADJ"},
            {"LOWER": {"IN": SUBSTANTIVOS_AVALIADOS}},
        ],
    ],
)
# regra de opnião onde um verbo de avaliação é negado, como 'não funciona'
matcher.add(
    "OPINIAO_VERBO_NEGADO",
    [
        [
            {"LOWER": {"IN": NEGACOES}},
            {"LOWER": {"IN": VERBOS_AVALIACAO}},
        ],
        [
            {"LOWER": {"IN": NEGACOES}},
            {"LOWER": {"IN": ["funciona", "funcionou", "funcionando"]}},
            {"LOWER": {"IN": AVALIACOES_FUNCIONAMENTO}},
        ],
        [
            {"LOWER": {"IN": NEGACOES}},
            {"LOWER": {"IN": ["e", "eh", "esta", "estava", "foi"]}, "OP": "?"},
            {"LOWER": {"IN": ADJETIVOS_OPINIAO}},
        ],
    ],
)
# regra de opnião ironica como 'parabens pessimo produto'
matcher.add(
    "OPINIAO_IRONIA_PARABENS",
    [
        [
            {"LOWER": "parabens"},
            {"LOWER": {"IN": ["pelo", "pela", "por"]}, "OP": "?"},
            {
                "LOWER": {
                    "IN": [
                        "pessimo",
                        "pessima",
                        "horrivel",
                        "ruim",
                        "insatisfeitos",
                        "demora",
                        "atraso",
                    ]
                }
            },
        ],
    ],
)

# regra de opnião onde um aspecto positivo é seguido por uma conjunção de contraste e um aspecto negativo, como 'otimo produto mas chegou atrasado'
matcher.add(
    "OPINIAO_CONTRASTE_NEGATIVO",
    [
        [
            {
                "LOWER": {
                    "IN": [
                        "otimo",
                        "otima",
                        "excelente",
                        "perfeito",
                        "perfeita",
                        "adorei",
                        "amei",
                    ]
                }
            },
            {"LOWER": {"IN": ["mas", "porem"]}},
            {
                "LOWER": {
                    "IN": [
                        "nao",
                        "ruim",
                        "defeito",
                        "quebrado",
                        "quebrada",
                        "demorou",
                        "faltando",
                        "vazando",
                    ]
                }
            },
        ],
        [
            {
                "LOWER": {
                    "IN": [
                        "otimo",
                        "otima",
                        "excelente",
                        "perfeito",
                        "perfeita",
                        "adorei",
                        "amei",
                    ]
                }
            },
            {"LOWER": "so"},
            {"LOWER": "que"},
            {"LOWER": {"IN": ["nao", "veio", "demorou", "faltando"]}},
        ],
    ],
)

# regra de opnião onde o cliente expressa uma avaliação intermediária
matcher.add(
    "OPINIAO_MAIS_OU_MENOS",
    [
        [
            {"LOWER": "mais"},
            {"LOWER": "ou"},
            {"LOWER": "menos"},
        ],
        [
            {"LOWER": {"IN": INTENSIFICADORES}},
            {"LOWER": "mais"},
            {"LOWER": "ou"},
            {"LOWER": "menos"},
        ],
    ],
)
# regra de opnião onde um verbo de avaliação positivo é usado expressar satisfação
matcher.add(
    "OPINIAO_VERBO_POSITIVO",
    [
        [{"LOWER": {"IN": VERBOS_POSITIVOS}}],
        [
            {"LOWER": {"IN": ["fiquei", "estou"]}},
            {"LOWER": {"IN": ["satisfeito", "satisfeita"]}},
        ],
    ],
)
# regra de opnião onde o cliente fala sobre o funcionamento do produto positivamente
matcher.add(
    "OPINIAO_FUNCIONAMENTO",
    [
        [
            {"LOWER": {"IN": ["funciona", "funcionou", "funcionando"]}},
            {"LOWER": {"IN": AVALIACOES_FUNCIONAMENTO}},
        ],
        [
            {"LOWER": {"IN": ["funciona", "funcionou", "funcionando"]}},
            {"LOWER": "muito"},
            {"LOWER": {"IN": AVALIACOES_FUNCIONAMENTO}},
        ],
    ],
)
# regra de opnião onde o cliente expressa um problema no recebimento do produto
matcher.add(
    "OPINIAO_PROBLEMA_RECEBIMENTO",
    [
        [
            {"LOWER": {"IN": ["veio", "chegou"]}},
            {"LOWER": {"IN": ["com", "sem"]}, "OP": "?"},
            {"LOWER": {"IN": PROBLEMAS_RECEBIMENTO}},
        ],
        [{"LOWER": {"IN": VERBOS_PROBLEMA}}],
    ],
)
# regra de opnião onde o cliente expressa um problema de funcionamento ou qualidade do produto
matcher.add(
    "OPINIAO_DEIXOU_A_DESEJAR",
    [
        [
            {"LOWER": {"IN": ["deixou", "deixa", "deixaram"]}},
            {"LOWER": "a"},
            {"LOWER": "desejar"},
        ],
    ],
)
# regra de opnião onde o cliente expressa que o produto não vale a pena
matcher.add(
    "OPINIAO_VALE_A_PENA",
    [
        [
            {"LOWER": {"IN": ["vale", "valeu"]}},
            {"LOWER": "a"},
            {"LOWER": {"IN": ["pena", "espera"]}},
        ],
        [
            {"LOWER": {"IN": NEGACOES}},
            {"LOWER": "vale"},
            {"LOWER": "a"},
            {"LOWER": "pena"},
        ],
    ],
)
# regra de opnião onde o cliente expressa que a entrega demorou muito ou demorou um pouco
matcher.add(
    "OPINIAO_DEMORA",
    [
        [
            {"LOWER": {"IN": ["demorou", "demora", "demorado", "demorada"]}},
            {"LOWER": {"IN": ["muito", "bastante"]}},
        ],
        [
            {"LOWER": {"IN": ["demorou", "demora"]}},
            {"LOWER": "um"},
            {"LOWER": "pouco"},
        ],
    ],
)
# regra de opnião onde o cliente expressa que a entrega foi rápida ou chegou antes do esperado
matcher.add(
    "OPINIAO_ENTREGA_PRAZO",
    [
        [
            {"LOWER": "entrega"},
            {"LOWER": {"IN": ["foi", "e", "esta", "estava"]}, "OP": "?"},
            {"LOWER": {"IN": ADJETIVOS_ENTREGA}},
        ],
        [
            {"LOWER": {"IN": ["chegou", "chegaram"]}},
            {"LOWER": {"IN": ["antes", "rapido", "rapida", "atrasado", "atrasada"]}},
        ],
    ],
)


# função para filtrar matches sobrepostos, mantendo apenas o mais longo, para evitar repetição de expressões
def _filtrar_matches_sobrepostos(matches):
    matches_ordenados = sorted(
        matches, key=lambda item: item[2] - item[1], reverse=True
    )
    tokens_ocupados = set()
    matches_filtrados = []

    for match in matches_ordenados:
        _, inicio, fim = match
        intervalo = range(inicio, fim)

        if any(posicao in tokens_ocupados for posicao in intervalo):
            continue

        tokens_ocupados.update(intervalo)
        matches_filtrados.append(match)

    return sorted(matches_filtrados, key=lambda item: item[1])


def extrair_opnioes(texto):
    """Recebe um texto limpo e retorna expressoes que indicam opinioes."""

    if not isinstance(texto, str) or not texto.strip():
        return []

    doc = nlp(texto.lower())
    matches = _filtrar_matches_sobrepostos(matcher(doc))

    opinioes_extraidas = []

    for match_id, inicio, fim in matches:
        nome_da_regra = nlp.vocab.strings[match_id]
        expressao = doc[inicio:fim].text

        opinioes_extraidas.append(
            {
                "regra": nome_da_regra,
                "expressao": expressao,
            }
        )

    return opinioes_extraidas
