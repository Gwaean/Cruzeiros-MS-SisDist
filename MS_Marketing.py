import pika
import csv
import time
import random

ARQUIVO_CSV = 'itinerários.csv'
ARQUIVO_HISTORICO = 'historico_precos.csv'
ARQUIVO_MARKETING = 'marketing_queue.csv'

def ler_precos_csv():
    precos = {}
    try:
        with open(ARQUIVO_CSV, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                precos[row['Destino']] = int(row['Valor_Pacote'])
    except FileNotFoundError:
        print(f"Arquivo {ARQUIVO_CSV} não encontrado. Criando novo...")
    return precos

def salvar_precos_csv(precos):
    with open(ARQUIVO_HISTORICO, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Verifica se o arquivo está vazio para escrever o cabeçalho
        if csvfile.tell() == 0:
            writer.writerow(['Data_Hora', 'Destino', 'Valor_Antigo', 'Valor_Novo', 'Variacao'])
        
        for destino, preco_novo in precos.items():
            preco_antigo = ler_precos_csv().get(destino, preco_novo)
            variacao = preco_novo - preco_antigo
            writer.writerow([
                time.strftime('%Y-%m-%d %H:%M:%S'),
                destino,
                preco_antigo,
                preco_novo,
                variacao
            ])

def subscribe_marketing(nome, email, destino):
    with open(ARQUIVO_MARKETING, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Verifica se o arquivo está vazio para escrever o cabeçalho
        if f.tell() == 0:
            writer.writerow(['Nome', 'Email', 'Destino'])
        writer.writerow([nome, email, destino])
    print(f"Inscrição realizada para {nome} em {destino}.")

def verificar_inscricoes(destino):
    inscritos = []
    try:
        with open(ARQUIVO_MARKETING, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)  
            for row in reader:
                if len(row) >= 3 and row[2] == destino:
                    inscritos.append(row[1])  # Email
    except FileNotFoundError:
        print(f"Arquivo {ARQUIVO_MARKETING} não encontrado.")
    return inscritos

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
    
    print(mensagem)
    inscritos = verificar_inscricoes(destino)

    for email in inscritos:
        channel.basic_publish(exchange="promocoes", routing_key=email, body=mensagem)
        print(f" [x] Enviado para {email}: {mensagem}")

    connection.close()

def simular_mudanca_preco():
    while True:
        precos = ler_precos_csv()
        if not precos:
            print("Nenhum destino encontrado. Adicione destinos ao arquivo CSV.")
            time.sleep(10)
            continue
            
        destino = random.choice(list(precos.keys()))
        preco_antigo = precos[destino]
        mudanca = random.randint(-300, 300)
        preco_novo = max(500, preco_antigo + mudanca)

        if preco_novo != preco_antigo:
            enviar_notificacao(destino, preco_antigo, preco_novo)
            precos[destino] = preco_novo
            salvar_precos_csv({destino: preco_novo})  # Salva apenas o destino alterado

        time.sleep(random.randint(5, 10))

if __name__ == "__main__":
    simular_mudanca_preco()