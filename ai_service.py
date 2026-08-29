import os
from openai import OpenAI
from dotenv import load_dotenv
from database import buscar_produtos, listar_lojas

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


SYSTEM_PROMPT = """Tu és o assistente oficial do VIP Supermercado (VIP SPAR) em Moçambique.
Responde SEMPRE em português de Moçambique, de forma NATURAL, CURTA e AMIGÁVEL.
Máximo 2-3 frases. Nunca uses listas longas nem respostas robóticas.

Regras:
- Seja direto e útil.
- Usa linguagem do dia-a-dia (ex: "temos", "está a", "pode passar").
- Quando falar de preço, diz o valor em MT.
- Se tiver promoção, menciona.
- Se stock for baixo (<10), avisa.
- Se não souberes, diz honestamente e oferece ajuda alternativa.
- Nunca inventes preços ou stock. Usa só os dados fornecidos.
- Cumprimenta de forma breve só na primeira mensagem ou quando fizer sentido.
"""


def gerar_resposta(mensagem_cliente: str, contexto_db: str = "") -> str:
    """Gera resposta natural usando os dados da base."""
    
    prompt_usuario = f"""Mensagem do cliente: "{mensagem_cliente}"

Dados da base de dados (usa só isto):
{contexto_db if contexto_db else "Nenhum produto específico encontrado."}

Responde de forma natural e curta:"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.6,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erro na IA: {e}")
        return "Desculpa, estou com um problema técnico agora. Tenta novamente daqui a pouco ou liga para a loja."


def processar_mensagem(texto: str) -> str:
    """Lógica principal: decide o que buscar na BD e gera resposta."""
    texto_lower = texto.lower().strip()

    # Comandos rápidos sem IA
    if any(p in texto_lower for p in ["loja", "lojas", "onde fica", "endereço", "localização", "horario", "horário", "aberto"]):
        lojas = listar_lojas()
        if not lojas:
            return "Ainda não tenho a lista de lojas atualizada."
        
        # Resposta curta com as principais
        principais = [f"{l['nome']} ({l['cidade']}) - {l['horario']}" for l in lojas[:4]]
        return "Temos várias lojas VIP:\n" + "\n".join(principais) + "\n\nDiz a cidade que queres mais detalhes."

    if any(p in texto_lower for p in ["olá", "ola", "oi", "bom dia", "boa tarde", "boa noite", "hey", "hi"]):
        return "Olá! Bem-vindo ao VIP Supermercado 😊\nComo posso ajudar? Pode perguntar preço, stock ou lojas."

    if any(p in texto_lower for p in ["obrigado", "obrigada", "valeu", "thanks", "tks"]):
        return "De nada! Qualquer coisa é só chamar. Sinta-se VIP! 🛒"

    # Busca produtos na base
    # Extrai possíveis palavras-chave simples
    palavras = [w for w in texto_lower.replace("?", "").replace("!", "").split() if len(w) > 2]
    resultados = []
    
    for palavra in palavras:
        encontrados = buscar_produtos(palavra, limite=3)
        for r in encontrados:
            if r not in resultados:
                resultados.append(r)
        if len(resultados) >= 4:
            break

    # Monta contexto para a IA
    if resultados:
        linhas = []
        for r in resultados:
            promo = f" | Promoção: {r['promocao']}" if r['promocao'] else ""
            stock_info = f"Stock: {r['stock']}" if r['stock'] > 0 else "Sem stock no momento"
            linhas.append(f"- {r['nome']}: {r['preco']:.0f} MT ({r['unidade']}) | {stock_info}{promo}")
        contexto = "Produtos encontrados:\n" + "\n".join(linhas)
    else:
        contexto = "Nenhum produto correspondente encontrado na base de dados."

    return gerar_resposta(texto, contexto)