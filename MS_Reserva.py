import csv
import json
import uuid
from datetime import datetime
import pika
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from chaves import carregar_chave_publica


chave_publica = carregar_chave_publica 
def verificar_assinatura(mensagem,assinatura):
 h = SHA256.new(mensagem.encode())
 try:
    pkcs1_15.new(chave_publica).verify(h, assinatura)
    return True
 except (ValueError, TypeError):
   return False


def ler_itinerarios(itinerarios_csv):
    itinerarios = []
    
    with open(itinerarios_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')  
        for row in reader:
            itinerarios.append({
                'Destino': row['Destino'],
                'Data_Embarque': datetime.strptime(row['Data_Embarque'], '%d/%m').date(),
                'Porto Embarque': row['Porto_Embarque'],
                'Nome_Navio': row['Nome_Navio'],
                'Porto_Desemb': row['Porto_Desemb'],
                'Lugares_Visit': row['Lugares_Visit'],
                'Num_Noites': int(row['Num_Noites']),
                'Valor_Pacote': float(row['Valor_Pacote'])
            })
            
    return itinerarios

def consultar_itinerarios(itinerarios, porto_embarque, data_embarque):
    resultados = []
    
    for itinerario in itinerarios:
        if itinerario['Porto_Embarque'].lower() == porto_embarque.lower() and itinerario['Data_Embarque'] >= data_embarque:
            resultados.append(itinerario)
    
    return resultados

def listar_itinerarios(itinerarios):
    if not itinerarios:
        print("\nNenhum itinerário disponível para os critérios informados.")
    else:
        print("Itinerários Disponíveis:")
        for i, itinerario in enumerate(itinerarios, 1):
            print(f"\nItinerário {i}:")
            print(f"  Destino: {itinerario['Destino']}")
            print(f"  Navio: {itinerario['Nome_Navio']}")
            print(f"  Porto de Embarque: {itinerario['Porto_Embarque']}")
            print(f"  Porto de Desembarque: {itinerario['Porto_Desemb']}")
            print(f"  Data de Embarque: {itinerario['Data_Embarque']}")
            print(f"  Número de Noites: {itinerario['Num_Noites']}")
            print(f"  Lugares a Visitar: {itinerario['Lugares_Visit']}")
            print(f"  Valor por Pessoa: R${itinerario['Valor_Pacote']:.2f}")


    
def publicar_reserva(itinerario, numero_passageiros, numero_cabines):
    mensagem = "\nReserva criada com sucesso!"
    reserva_id = str(uuid.uuid4())
    valor_total = itinerario['Valor_Pacote'] * numero_passageiros

    dados_reserva = {
        "reserva_id": reserva_id,
        "valor": valor_total
    }

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='reserva-criada')

    channel.basic_publish(
        exchange='',
        routing_key='reserva-criada',
        body=json.dumps(dados_reserva)
    )

    print(f"\nReserva publicada: {mensagem}")
    
    connection.close()
def callback_pagamento(ch, method, properties, body):
    pacote = json.loads(body)
    mensagem = pacote['mensagem']
    assinatura = pacote['assinatura']

    if verificar_assinatura(mensagem, assinatura):
        if "aprovado" in mensagem:
            print(f"[Reserva] Uhuul! ✅ Seu pagamento foi aprovado: {mensagem}")
        elif "recusado" in mensagem:
            print(f"[Reserva] Ahhh...  Boa sorte na próxima, jovem gafanhoto \n Pagamento recusado ❌: {mensagem}")
    else:
        print("[Reserva] ⚠️ Assinatura inválida!")
        
def callback_bilhete(_ch, _method, _props, body):
    bilhete = json.loads(body)
    print(f"[Reserva] Tudo certo por aqui! Gerando reserva...: {bilhete}")    
    print(f"  ID da Reserva: {bilhete.get('reserva_id')}")
    print(bilhete)

def escutar_respostas():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='pagamento-aprovado')
    channel.queue_declare(queue='pagamento-recusado')
    channel.queue_declare(queue='bilhete-gerado')

    channel.basic_consume(queue='pagamento-aprovado', on_message_callback=callback_pagamento, auto_ack=True)
    channel.basic_consume(queue='pagamento-recusado', on_message_callback=callback_pagamento, auto_ack=True)
    channel.basic_consume(queue='bilhete-gerado', on_message_callback=callback_bilhete, auto_ack=True)
    
    channel.start_consuming()
    
if __name__ == "__main__":
    escutar_respostas()