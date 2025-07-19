EXPLAIN_MESSAGES = {
    "en": [
        {
            "role": "system",
            "content": (
                "You are a helpful and precise Chinese assistant. "
                "Respond only in plain English text. No markdown, no JSON, no Chinese commentary."
            )
        },
        {
            "role": "user",
            "content": """
Explain the Chinese word “{word}” in the sentence: “{sentence}”.

All fields below are required.
Respond with exactly these fields, in plain English, one per line:
meaning: ... (list multiple meanings if applicable)
synonyms: ... (comma-separated Chinese words)
explanation: ... (in English)
example: ... (short Chinese sentence)

Plain text only. One field per line. Use English field names. No Chinese explanation.
"""
        }
    ],
    "it": [
        {
            "role": "system",
            "content": (
                "Sei un assistente cinese preciso e utile. "
                "Rispondi solo in testo semplice in italiano. Niente markdown, niente JSON, niente commenti in cinese."
            )
        },
        {
            "role": "user",
            "content": """
Spiega la parola cinese “{word}” nella frase: “{sentence}”.

Tutti i campi seguenti sono obbligatori.
Usa esattamente questi campi (in inglese), uno per riga:
meaning: ... (elenca più significati se ci sono)
synonyms: ... (parole cinesi separate da virgole)
explanation: ... (in italiano)
example: ... (frase breve in cinese)

Solo testo semplice. Nomi dei campi in inglese. Nessuna spiegazione in cinese.
"""
        }
    ],
    "fr": [
        {
            "role": "system",
            "content": (
                "Tu es un assistant chinois précis et utile. "
                "Réponds uniquement en texte brut en français. Pas de markdown, pas de JSON, pas de commentaires en chinois."
            )
        },
        {
            "role": "user",
            "content": """
Explique le mot chinois “{word}” dans la phrase : “{sentence}”.

Tous les champs suivants sont obligatoires.
Utilise exactement ces champs (en anglais), un par ligne :
meaning: ... (donne plusieurs sens s'il y en a)
synonyms: ... (mots chinois séparés par des virgules)
explanation: ... (en français)
example: ... (phrase courte en chinois)

Texte brut uniquement. Noms de champs en anglais. Pas d’explication en chinois.
"""
        }
    ],
    "es": [
        {
            "role": "system",
            "content": (
                "Eres un asistente chino útil y preciso. "
                "Responde solo en texto plano en español. Sin markdown, sin JSON, sin comentarios en chino."
            )
        },
        {
            "role": "user",
            "content": """
Explica la palabra china “{word}” en la frase: “{sentence}”.

Todos los siguientes campos son obligatorios.
Utiliza exactamente estos campos (en inglés), uno por línea:
meaning: ... (incluye varios significados si aplica)
synonyms: ... (palabras chinas separadas por comas)
explanation: ... (en español)
example: ... (frase corta en chino)

Solo texto plano. Nombres de campos en inglés. Sin explicación en chino.
"""
        }
    ],
    "ko": [
        {
            "role": "system",
            "content": (
                "당신은 유용하고 정확한 중국어 도우미입니다. "
                "한국어로 된 일반 텍스트만 응답하세요. 마크다운, JSON, 중국어 설명은 하지 마세요."
            )
        },
        {
            "role": "user",
            "content": """
문장 “{sentence}”에서 중국어 단어 “{word}”를 설명하세요.

다음 모든 항목은 필수이며 영어 필드명을 사용하세요:
meaning: ... (두 개 이상의 의미가 있다면 모두 제시)
synonyms: ... (쉼표로 구분된 중국어 단어들)
explanation: ... (한국어로)
example: ... (짧은 중국어 문장)

일반 텍스트만. 필드 이름은 영어로. 중국어 설명은 금지.
"""
        }
    ],
    "ja": [
        {
            "role": "system",
            "content": (
                "あなたは正確で役に立つ中国語アシスタントです。 "
                "日本語でプレーンテキストのみで回答してください。マークダウン、JSON、中国語の解説は禁止です。"
            )
        },
        {
            "role": "user",
            "content": """
文「{sentence}」の中の中国語の単語「{word}」を説明してください。

すべての項目は必須です。フィールド名は英語で書いてください:
meaning: ...（複数の意味があればすべて記載してください）
synonyms: ...（中国語の単語をカンマで区切る）
explanation: ...（日本語で）
example: ...（短い中国語の文）

プレーンテキストのみ。1行につき1項目。フィールド名は英語。中国語の解説は禁止。
"""
        }
    ]
}


def get_explain_messages(lang: str, word: str, sentence: str) -> list[dict]:
    messages = EXPLAIN_MESSAGES.get(lang)
    if messages is None:
        messages = EXPLAIN_MESSAGES["en"]

    formatted = [msg.copy() for msg in messages]
    if len(formatted) > 1 and "{word}" in formatted[1]["content"]:
        formatted[1]["content"] = formatted[1]["content"].format(
            word=word,
            sentence=sentence
        )
    return formatted

