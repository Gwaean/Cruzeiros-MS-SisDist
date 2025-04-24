import pika
import random
import json
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from chaves import carregar_chave_publica

# Bilhete escuta de pagamento, caso seja aprovado ele envia o bilhete gerado SOMENTE p/ Reserva
# Caso o pagamento seja NEGADO, nada acontece (o pagamento recusado envia notificacao direto p/ reserva)

chave_publica = carregar_chave_publica

def verificar_assinatura(mensagem, assinatura_hex):
    h = SHA256.new(mensagem.encode())
    assinatura = bytes.fromhex(assinatura_hex)
    try:
        pkcs1_15.new(chave_publica).verify(h, assinatura)
        return True
    except (ValueError, TypeError):
        return False
def gerar_bilhete(reserva_id):
    return {
        "reserva_id": reserva_id,
        "bilhete": f"BILHETE-{reserva_id[:5].upper()}-{random.randint(1000,9999)}"
    }

def enviar_bilhete(bilhete):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue="bilhete-gerado")

    channel.basic_publish(exchange="", routing_key="bilhete-gerado", body=json.dumps(bilhete))
    print(f"[Bilhete] Pagamento Processando...: {bilhete}")
    connection.close()

def callback(ch, method, props, body):
    pacote = json.loads(body)
    mensagem = pacote["mensagem"]
    assinatura = pacote["assinatura"]

    if verificar_assinatura(mensagem, assinatura):
        dados = dict(item.split(":") for item in mensagem.split(";"))
        bilhete = gerar_bilhete(dados["reserva_id"])
        enviar_bilhete(bilhete)


def escutar_pagamentos_aprovados():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue="pagamento-aprovado")

    channel.basic_consume(queue="pagamento-aprovado", on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    escutar_pagamentos_aprovados()