import spacy


nlp = spacy.load("pt_core_news_sm", disable=["ner", "parser"])


def aplicar_pos_tagging(texto):
    """
    recebe um texto limpo e devolve cada palavra com sua classe gramatical.
    """
    if not isinstance(texto, str) or not texto.strip():
        return []

    doc = nlp(texto)

    tokens_etiquetados = []

    for token in doc:
        tokens_etiquetados.append({"palavra": token.text.lower(), "classe": token.pos_})

    return tokens_etiquetados
