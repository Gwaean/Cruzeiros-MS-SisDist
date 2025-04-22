import pika
import sys
# Marketing envia promocoes do(s) destino(s) selecionado(s) pelo cliente p/ receber notificação quando o preço varia
# Ele envia SOMENTE para quem escolheu receber E SOMENTE p/ o(s) destino(s) escolhido(s) --> NAO PODE DAR FANOUT

# Emite log

connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()
severity = sys.argv[1] if len(sys.argv) > 2 else "info"
channel.exchange_declare(exchange="direct_logs", exchange_type="direct")

message = " ".join(sys.argv[1:]) or "info: Hello World!"
channel.basic_publish(exchange="direct_logs", routing_key=severity, body=message)
print(f" [x] Sent {severity}:{message}")


connection.close()
