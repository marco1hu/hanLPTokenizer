TRANSLATION_MESSAGES = {
    "en": [
        {"role": "system", "content": "You are a precise Chinese-English translator. Return only plain text. No markdown, no commentary."},
        {"role": "user", "content": (
            "Sentence: {sentence}\n"
            "Tokens: {tokens}\n\n"
            "Your task:\n"
            "1. Translate the sentence into natural English.\n"
            "2. Then, write each token followed by a colon and its literal translation, one per line.\n\n"
            "Example format:\n"
            "Natural English translation here.\n"
            "token1: translation1\n"
            "token2: translation2\n"
        )}
    ],

    "it": [
        {"role": "system", "content": "Sei un traduttore cinese-italiano preciso. Rispondi solo con testo semplice. Niente markdown, niente commenti."},
        {"role": "user", "content": (
            "Frase: {sentence}\n"
            "Token: {tokens}\n\n"
            "Il tuo compito:\n"
            "1. Traduci la frase in italiano naturale.\n"
            "2. Poi scrivi ogni token seguito dai due punti e dalla sua traduzione letterale, uno per riga.\n\n"
            "Formato esempio:\n"
            "Traduzione italiana naturale qui.\n"
            "token1: traduzione1\n"
            "token2: traduzione2\n"
        )}
    ],

    "fr": [
        {"role": "system", "content": "Tu es un traducteur chinois-français précis. Réponds uniquement avec du texte brut. Pas de markdown, pas de commentaires."},
        {"role": "user", "content": (
            "Phrase : {sentence}\n"
            "Tokens : {tokens}\n\n"
            "Ta tâche :\n"
            "1. Traduis la phrase en français naturel.\n"
            "2. Ensuite, écris chaque token suivi de deux-points et de sa traduction littérale, un par ligne.\n\n"
            "Format exemple :\n"
            "Traduction naturelle ici.\n"
            "token1: traduction1\n"
            "token2: traduction2\n"
        )}
    ],

    "es": [
        {"role": "system", "content": "Eres un traductor chino-español preciso. Responde solo con texto plano. Sin markdown ni comentarios."},
        {"role": "user", "content": (
            "Frase: {sentence}\n"
            "Tokens: {tokens}\n\n"
            "Tu tarea:\n"
            "1. Traduce la frase al español natural.\n"
            "2. Luego escribe cada token seguido de dos puntos y su traducción literal, una por línea.\n\n"
            "Formato de ejemplo:\n"
            "Traducción natural aquí.\n"
            "token1: traducción1\n"
            "token2: traducción2\n"
        )}
    ],

    "ja": [
        {"role": "system", "content": "あなたは正確な中国語-日本語の翻訳者です。プレーンテキストのみを返してください。マークダウンやコメントは禁止です。"},
        {"role": "user", "content": (
            "文: {sentence}\n"
            "トークン: {tokens}\n\n"
            "あなたのタスク：\n"
            "1. 文を自然な日本語に翻訳してください。\n"
            "2. 各トークンとその直訳を「トークン: 翻訳」の形式で1行ずつ書いてください。\n\n"
            "例:\n"
            "自然な日本語訳はこちら。\n"
            "token1: 翻訳1\n"
            "token2: 翻訳2\n"
        )}
    ],

    "ko": [
        {"role": "system", "content": "당신은 정확한 중국어-한국어 번역가입니다. 일반 텍스트만 반환하세요. 마크다운이나 해설은 하지 마세요."},
        {"role": "user", "content": (
            "문장: {sentence}\n"
            "토큰: {tokens}\n\n"
            "작업:\n"
            "1. 문장을 자연스러운 한국어로 번역하세요.\n"
            "2. 그런 다음 각 토큰을 ‘토큰: 번역’ 형식으로 한 줄씩 작성하세요.\n\n"
            "예시 형식:\n"
            "자연스러운 한국어 번역 여기.\n"
            "token1: 번역1\n"
            "token2: 번역2\n"
        )}
    ]
}



def get_translation_messages(lang: str, sentence: str, tokens: list[str]) -> list[dict]:
    messages = TRANSLATION_MESSAGES.get(lang)
    if messages is None:
        messages = TRANSLATION_MESSAGES["en"]

    # Deep copy to avoid mutating global state
    formatted = [msg.copy() for msg in messages]

    if len(formatted) > 1 and "{sentence}" in formatted[1]["content"]:
        formatted[1]["content"] = formatted[1]["content"].format(
            sentence=sentence,
            tokens=", ".join(tokens)
        )

    return formatted
