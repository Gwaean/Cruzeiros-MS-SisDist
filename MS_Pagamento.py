import pika
import json
import random
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA


chave = RSA.generate(2048)

with open("private_key.pem", "wb") as f:
    f.write(chave.export_key())

with open("public_key.der", "wb") as f:
    f.write(chave.publickey().export_key(format="DER"))
    
def assinar_mensagem(mensagem):
    h = SHA256.new(mensagem.encode())
    assinatura = pkcs1_15.new(chave).sign(h)
    return assinatura.hex()
    
def enviar(destino, mensagem, assinatura):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=destino)

    pacote = {
        "mensagem": mensagem,
        "assinatura": assinatura
    }

    channel.basic_publish(exchange="direct_logs", routing_key=destino, body=json.dumps(pacote))
    print(f"[Pagamento] Situação: {destino} {mensagem}")
    connection.close()

def simular_pagamento():
    pagamento = random.randint(0, 9)
    if pagamento % 2 == 0:
        return True  
    else:
        return False  
def processar(ch, method, props, body):
    dados = json.loads(body)
    reserva_id = dados.get("reserva_id", "desconhecida")
    valor = dados.get("valor", 0)

    print(f"/**Processando pagamento da reserva ID = {reserva_id} no valor de R${valor}")
    aprovado = simular_pagamento()

    status = "aprovado" if aprovado else "recusado"
    mensagem = f"Reserva ID = {reserva_id}; Status: {status}"
    assinatura = assinar_mensagem(mensagem)

    if aprovado:
        enviar("pagamento-aprovado;", mensagem, assinatura)
    else:
        enviar("pagamento-recusado;", mensagem, assinatura)

def escutar():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue="reserva-criada")

    channel.basic_consume(queue="reserva-criada", on_message_callback=processar, auto_ack=True)
    print("[Pagamento] Aguardando reservas...")
    channel.start_consuming()

if __name__ == "__main__":
    escutar()