#!/usr/bin/env python
import pika
import sys

print ("Menu Opções: \n" )
escolha = input('1- Consulta \n' \
'2-Reserva')
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