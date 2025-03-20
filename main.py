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

#Parte que adiciona os peers do arquivo vizinhos.txt e apresenta saída solicitada conforme 2.3 EP: parte 1
class Peer:
    def __init__(self, IP, PORTA, status):
        self.IP = IP
        self.PORTA = PORTA
        self.STATUS = status

lista_vizinhos = []

with open(vizinhos, "r") as arquivo:
    for linha in arquivo:
        print(f"Adicionando novo peer {linha} status OFFLINE")
        lista_vizinhos.append(Peer(linha.split(":")[0], linha.split(":")[1], "OFFLINE"))

