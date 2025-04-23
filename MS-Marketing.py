import pika
import csv
import time
import random

ARQUIVO_CSV = 'itinerários_csv'
# Marketing envia promocoes do(s) destino(s) selecionado(s) pelo cliente p/ receber notificação quando o preço varia
# Ele envia SOMENTE para quem escolheu receber E SOMENTE p/ o(s) destino(s) escolhido(s) --> NAO PODE DAR FANOUT
def ler_precos_csv():
    precos = {}
    with open(ARQUIVO_CSV, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            precos[row['Destino']] = int(row['Valor_Pacote'])
    return precos

def salvar_precos_csv(precos):
    with open(ARQUIVO_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Destino', 'Valor_Pacote'])  # cabeçalho
        for destino, preco in precos.items():
            writer.writerow({'Destino': destino, 'Valor_Pacote': preco})

# Emite log
def enviar_notificacao(destino, preco_antigo, preco_novo):
 connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
 channel = connection.channel()
 channel.exchange_declare(exchange="promocoes", exchange_type="direct")
 if preco_novo < preco_antigo:
        variacao = preco_antigo - preco_novo
        mensagem = f"🔥 Aproveite! Baixa de preço para {destino}! Agora R${preco_novo} (↓ R${variacao})"
 else:
        variacao = preco_novo - preco_antigo
        mensagem = f"📈 Aumento de preço em {destino}: Agora R${preco_novo} (↑ R${variacao})"
 
 channel.basic_publish(exchange="promocoes", routing_key=destino, body=mensagem)
 print(f" [x] Sent {destino}:{mensagem}")

 connection.close()
def simular_mudanca_preco():
    while True:
        precos = ler_precos_csv()
        destino = random.choice(list(precos.keys()))
        preco_antigo = precos[destino]
        mudanca = random.randint(-300, 300)
        preco_novo = max(500, preco_antigo + mudanca)

        if preco_novo != preco_antigo:
            enviar_notificacao(destino, preco_antigo, preco_novo)
            precos[destino] = preco_novo
            salvar_precos_csv(precos)

        time.sleep(random.randint(5, 10))

if __name__ == "__main__":
    simular_mudanca_preco()