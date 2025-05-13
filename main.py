from datetime import datetime
from MS_Reserva import ler_itinerarios, consultar_itinerarios, publicar_reserva, listar_itinerarios
from MS_Marketing import subscribe_marketing
import pika


def consumir_notificacoes(interesse):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()

    channel.exchange_declare(exchange="promocoes", exchange_type="direct")
    
   
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    print("\n🎯 Aguardando promoções... (CTRL+C para sair)\n")

    destino_formatado = interesse.lower().replace(" ", "_")
    channel.queue_bind(exchange="promocoes", queue=queue_name, routing_key=destino_formatado)


    def callback(ch, method, properties, body):
        print(f"\n📢 Notificação recebida: {body.decode()}")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()

def main():
    itinerarios = ler_itinerarios("itinerarios.csv")
    
    while True:
        print("\nEscolha uma opção:")
        print("1. Listar Itinerários")
        print("2. Fazer Reserva")
        print("3. Sair")
        print("4. Inscrever-se na fila de marketing")
        escolha = input("\nDigite o número da opção: ")

        if escolha == '1':            
            listar_itinerarios(itinerarios)
        
        elif escolha == '2':
            porto_embarque = input("\nDigite o porto de embarque: ")
            data_embarque = input("Digite a data de embarque (DD/MM): ")
            data_embarque = datetime.strptime(data_embarque, '%d/%m').date()
            
            itinerarios_disponiveis = consultar_itinerarios(itinerarios, porto_embarque, data_embarque)
            
            if itinerarios_disponiveis:
                listar_itinerarios(itinerarios_disponiveis)
                
                reservar = int(input("\nEscolha o número do itinerário para reserva: "))
                numero_passageiros = int(input("Quantidade de passageiros: "))
                numero_cabines = int(input("Quantidade de cabines: "))
                
                itinerario_escolhido = itinerarios_disponiveis[reservar - 1]
                publicar_reserva(itinerario_escolhido, numero_passageiros, numero_cabines)
            else:
                print("\nNenhum itinerário disponível para esta opção.")
        
        elif escolha == '3':
            print("\nVolte sempre!\n")
            break
        elif escolha == '4':
            nome = input("Digite seu nome: ")
            interesse = input("Digite o porto de interesse para marketing: ")
            subscribe_marketing(nome, interesse)
            consumir_notificacoes(interesse)
        else:
            print("\nOpção inválida. Tente novamente.")

if __name__ == '__main__':
    main()