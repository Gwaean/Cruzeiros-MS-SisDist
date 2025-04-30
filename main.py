from datetime import datetime
from MS_Reserva import ler_itinerarios, consultar_itinerarios, publicar_reserva, listar_itinerarios
from MS_Marketing import subscribe_marketing

def main():
    itinerarios = ler_itinerarios('itinerários.csv')
    
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
            email = input("Digite seu e-mail: ")
            interesse = input("Digite o porto de interesse para marketing: ")

            
            # Função para adicionar usuário à fila de marketing
            subscribe_marketing(nome, email, interesse)
        else:
            print("\nOpção inválida. Tente novamente.")

if __name__ == '__main__':
    main()