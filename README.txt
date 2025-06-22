🚀 HanLP Tokenizer REST Server

1. Installa Python 3.9+
2. Installa le dipendenze:
   pip3 install -r requirements.txt

3. Avvia il server:
   python3 hanlp_server.py

4. Fai una richiesta POST a:
   http://localhost:5005/tokenize

Body esempio:
{
  "text": "三体是一本非常著名的小说。"
}
