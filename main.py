import sys
import socket

if len(sys.argv) != 4:
    print("Uso correto: python3 <nome>.py <endereço>:<porta> <vizinhos.txt> <diretório_compartilhado>")
    sys.exit(1)

IP = sys.argv[1].split(":")[0]
PORTA = int(sys.argv[1].split(":")[1])
vizinhos = sys.argv[2]
diretorio_compartilhado = sys.argv[3]

#Criando o socket TCP conforme especificado em 2.3 EP: parte 1
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORTA))


