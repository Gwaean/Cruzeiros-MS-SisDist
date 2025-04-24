import csv
from datetime import datetime
import pika

def ler_itinerarios(itinerarios_csv):
    itinerarios = []
    
    with open(itinerarios_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')  # Altere o delimitador se necessário
        for row in reader:
            itinerarios.append({
                'Destino': row['Destino'],
                'Data Embarque': datetime.strptime(row['Data Embarque'], '%d/%m').date(),
                'Porto Embarque': row['Porto Embarque'],
                'Nome Navio': row['Nome Navio'],
                'Porto Desemb': row['Porto Desemb'],
                'Lugares Visit': row['Lugares Visit'],
                'Num Noites': int(row['Num Noites']),
                'Valor p/ pessoa': float(row['Valor p/ pessoa'])
            })
            
    return itinerarios

def consultar_itinerarios(itinerarios, porto_embarque, data_embarque):
    resultados = []
    
    for itinerario in itinerarios:
        if itinerario['Porto Embarque'].lower() == porto_embarque.lower() and itinerario['Data Embarque'] >= data_embarque:
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
            print(f"  Navio: {itinerario['Nome Navio']}")
            print(f"  Porto de Embarque: {itinerario['Porto Embarque']}")
            print(f"  Porto de Desembarque: {itinerario['Porto Desemb']}")
            print(f"  Data de Embarque: {itinerario['Data Embarque']}")
            print(f"  Número de Noites: {itinerario['Num Noites']}")
            print(f"  Lugares a Visitar: {itinerario['Lugares Visit']}")
            print(f"  Valor por Pessoa: R${itinerario['Valor p/ pessoa']:.2f}")


def publicar_reserva(itinerario, numero_passageiros, numero_cabines):
    mensagem = "\nReserva criada com sucesso!"
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='direct_logs', exchange_type='direct')
    
    channel.basic_publish(exchange='direct_logs', routing_key='reserva-criada', body=mensagem)
    
    print(f"\nReserva publicada: {mensagem}")
    
    connection.close()