#!/usr/bin/env python
import pika
import sys
import csv
import time
import random
# Marketing envia promocoes do(s) destino(s) selecionado(s) pelo cliente p/ receber notificação quando o preço varia
# Ele envia SOMENTE para quem escolheu receber E SOMENTE p/ o(s) destino(s) escolhido(s) --> NAO PODE DAR FANOUT

ARQUIVO_CSV = "itinerários.csv"
def ler_precos_csv():
    precos = {}
    with open(ARQUIVO_CSV, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            precos[row['Porto_Desemb']] = int(row['Valor_Pacote'])
    return precos

print ("Gostaria de receber promoções? \n Digite N caso queira sair\n" )
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs',
                         exchange_type='direct')

message = ' '.join(sys.argv[1:]) or "info: Hello World!"
channel.basic_publish(exchange='logs', routing_key='severity', body=message)
print(f" [x] Sent {message}")
connection.close()
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue


severities = sys.argv[1:]
if not severities:
    sys.stderr.write("Usage: %s [info] [warning] [error]\n" % sys.argv[0])
    sys.exit(1)

for severity in severities:
    channel.queue_bind(exchange='direct_logs',
                       queue=queue_name,
                       routing_key=severity)