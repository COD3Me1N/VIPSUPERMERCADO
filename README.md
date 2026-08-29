# VIP Supermercado WhatsApp Bot

Bot de atendimento inteligente para o **VIP Supermercado (VIP SPAR)** em Moçambique.

- Canal: WhatsApp via **Ultramsg**
- IA: OpenAI (gpt-4o-mini) para respostas naturais e curtas
- Base de dados: SQLite (só consulta nesta versão de teste)
- Linguagem: Português de Moçambique

---

## 1. Instalação

```bash
cd vip_bot
python -m venv venv
source venv/bin/activate   # Linux/Mac
# ou venv\Scripts\activate  no Windows

pip install -r requirements.txt
```

## 2. Configuração

Copia o ficheiro de exemplo e preenche as chaves:

```bash
cp .env.example .env
```

Edita o `.env`:

```env
ULTRAMSG_INSTANCE_ID=instanceXXXX
ULTRAMSG_TOKEN=teu_token_aqui
OPENAI_API_KEY=sk-xxxxxxxx
OPENAI_MODEL=gpt-4o-mini
```

### Como obter as credenciais Ultramsg:
1. Cria conta em https://ultramsg.com
2. Cria uma Instance e faz scan do QR Code com o número WhatsApp
3. Copia o `instance_id` e o `token`

## 3. Criar a base de dados de teste

```bash
python database.py
```

Isto cria o ficheiro `vip_stock.db` com:
- 8 lojas VIP reais (Maputo, Nampula, Beira, etc.)
- ~20 produtos típicos (arroz, óleo, leite, fraldas, etc.) com preços e stock

## 4. Correr o bot localmente

```bash
python app.py
```

O servidor fica em `http://localhost:5000`

### Testar sem WhatsApp (recomendado primeiro):

```bash
curl -X POST http://localhost:5000/test \
  -H "Content-Type: application/json" \
  -d '{"mensagem": "tem arroz 5kg?"}'
```

Exemplos de perguntas:
- "olá"
- "tem arroz?"
- "quanto custa o leite nido?"
- "onde fica a loja de Nampula?"
- "horário das lojas"
- "tem promoção?"

## 5. Ligar ao WhatsApp (Ultramsg)

1. Expõe o teu servidor com **ngrok** (ou Cloudflare Tunnel):

```bash
ngrok http 5000
```

2. Copia o URL HTTPS que o ngrok dá (ex: `https://abc123.ngrok.io`)

3. No painel do Ultramsg → Instance → Settings → Webhook:
   - Webhook URL: `https://abc123.ngrok.io/webhook`
   - Ativa **webhook_message_received**

4. Envia uma mensagem para o número ligado ao Ultramsg e vê a magia acontecer.

---

## Estrutura do projeto

```
vip_bot/
├── app.py              # Servidor Flask + webhook Ultramsg
├── ai_service.py       # Lógica de IA + respostas naturais
├── database.py         # SQLite + dados de teste
├── vip_stock.db        # Base de dados (criada automaticamente)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Próximos passos possíveis

- [ ] Atualização de stock por funcionários (comandos admin)
- [ ] Múltiplas lojas com stock separado
- [ ] Integração com site vipspar.com
- [ ] Envio de imagens de produtos
- [ ] Pedidos / reservas
- [ ] Usar Grok (xAI) em vez de OpenAI

---

Feito com ❤️ para o VIP Supermercado – Moçambique  
Sinta-se VIP! 🛒
---

## 6. Deploy no Render.com (recomendado)

### Passo a passo:

1. Cria conta em https://render.com (gratuito)

2. **New + → Web Service**

3. Liga o teu repositório GitHub (ou faz upload do ZIP)

4. Configurações:
   - **Name:** vip-supermercado-bot
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Instance Type:** Free

5. **Environment Variables** (Add Environment Variable):
   ```
   ULTRAMSG_INSTANCE_ID = instanceXXXX
   ULTRAMSG_TOKEN = teu_token
   OPENAI_API_KEY = sk-xxxxxxxx
   OPENAI_MODEL = gpt-4o-mini
   ```

6. Clica **Create Web Service**

7. Depois do deploy, copia o URL do serviço (ex: `https://vip-supermercado-bot.onrender.com`)

8. No Ultramsg → Instance → Settings → Webhook URL:
   ```
   https://vip-supermercado-bot.onrender.com/webhook
   ```
   Ativa **webhook_message_received**

9. Pronto! Envia mensagem para o número WhatsApp e testa.

> **Nota:** No plano Free do Render o serviço "dorme" após 15 min de inatividade. A primeira mensagem depois de dormir pode demorar ~30-50 segundos.

### Ficheiros incluídos para Render:
- `Procfile`
- `render.yaml`
- `requirements.txt` (com gunicorn)
