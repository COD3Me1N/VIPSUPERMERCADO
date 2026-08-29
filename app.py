import os
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from ai_service import processar_mensagem
from database import init_db

load_dotenv()

app = Flask(__name__)

# Configuração Ultramsg
INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")
TOKEN = os.getenv("ULTRAMSG_TOKEN")
ULTRA_URL = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat"


def enviar_mensagem(para: str, texto: str):
    """Envia mensagem via Ultramsg."""
    if not INSTANCE_ID or not TOKEN:
        print("⚠️  Ultramsg não configurado. Mensagem que seria enviada:")
        print(f"Para: {para}\nTexto: {texto}\n")
        return {"sent": False, "message": "credentials missing"}

    payload = {
        "token": TOKEN,
        "to": para,
        "body": texto
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        resp = requests.post(ULTRA_URL, data=payload, headers=headers, timeout=15)
        print(f"Enviado para {para}: {resp.status_code} - {resp.text}")
        return resp.json()
    except Exception as e:
        print(f"Erro ao enviar: {e}")
        return {"error": str(e)}


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "bot": "VIP Supermercado WhatsApp Bot",
        "mensagem": "Webhook pronto. Configure o URL no Ultramsg."
    })


@app.route("/webhook", methods=["POST"])
def webhook():
    """Recebe mensagens do Ultramsg."""
    try:
        data = request.json
        print("Webhook recebido:", json.dumps(data, indent=2, ensure_ascii=False))

        # Estrutura típica do Ultramsg
        if not data or "data" not in data:
            return jsonify({"status": "ignored"}), 200

        msg = data["data"]

        # Ignora mensagens enviadas por nós
        if msg.get("fromMe", False):
            return jsonify({"status": "ignored_from_me"}), 200

        # Só processa mensagens de texto
        if msg.get("type") != "chat":
            return jsonify({"status": "ignored_not_text"}), 200

        from_number = msg.get("from")  # formato: 25884xxxxxxx@c.us
        body = msg.get("body", "").strip()

        if not body or not from_number:
            return jsonify({"status": "empty"}), 200

        print(f"Mensagem de {from_number}: {body}")

        # Processa com IA + base de dados
        resposta = processar_mensagem(body)

        # Envia resposta
        enviar_mensagem(from_number, resposta)

        return jsonify({"status": "ok", "resposta": resposta}), 200

    except Exception as e:
        print(f"Erro no webhook: {e}")
        return jsonify({"status": "error", "detail": str(e)}), 200


@app.route("/test", methods=["POST"])
def test_local():
    """Endpoint para testar localmente sem WhatsApp."""
    data = request.json or {}
    mensagem = data.get("mensagem", "")
    if not mensagem:
        return jsonify({"erro": "Envie {'mensagem': 'sua pergunta'}"}), 400

    resposta = processar_mensagem(mensagem)
    return jsonify({
        "cliente": mensagem,
        "bot": resposta
    })


# Cria a base de dados se não existir (útil no primeiro deploy no Render)
if not os.path.exists("vip_stock.db"):
    print("A criar base de dados de teste...")
    init_db()

if __name__ == "__main__":
    print("🚀 Bot VIP Supermercado a arrancar...")
    print("Webhook: POST /webhook")
    print("Teste local: POST /test  com {'mensagem': 'tem arroz?'}")
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)