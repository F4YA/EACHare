import os
import sys
import socket
import threading
from pathlib import Path

if len(sys.argv) != 4:
    print("Uso correto: python3 <nome>.py <endereço>:<porta> <vizinhos.txt> <diretório_compartilhado>")
    sys.exit(1)

IP = sys.argv[1].split(":")[0]
PORTA = int(sys.argv[1].split(":")[1])
vizinhos = sys.argv[2]
diretorio_compartilhado = sys.argv[3]
clock = 0

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

#Verifica se o diretório de compartilhamento é um diretório válido e pode ser lido.
caminho_diretorio = Path(diretorio_compartilhado)

if not caminho_diretorio.is_dir() or not os.access(caminho_diretorio, os.R_OK):
    print(f"Erro: '{diretorio_compartilhado}' não é um diretório válido ou não pode ser lido.")
    sys.exit(1)

#Função que lida com a requisição do cliente
def tratar_req(req):
    while True:
        try:
            data = req.recv(1024)
            if not data:
                break
            print("Mensagem recebida: ", data)
        except:
            break
    req.close()

#Função que inicia o servidor
def inicia_server():
    server.listen()
    print(f"Servidor iniciado {IP}:{PORTA}")

    while True:
        req, addr = server.accept()
        cliente_thread = threading.Thread(target=tratar_req, args=(req,))
        cliente_thread.start()


server_thread = threading.Thread(target=inicia_server)
server_thread.daemon = True
server_thread.start()

threading.Event().wait(1)

opcao = int(input("Escolha um comando:\n [1] Listar peers \n [2] Obter peers \n [3] Listar arquivos locais \n [4] Buscar arquivos \n [5] Exibir estatísticas \n [6] Alterar tamanho de chunk \n [7] Sair \n opcao: "))

# Função de enviar mensagem para os peers como especificado em 2.1 - EP: Parte 1
def envia_mensagem(peer, tipo):
    try:
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((peer.IP, int(peer.PORTA)))
        # <ORIGEM> <CLOCK> <TIPO> [ARGUMENTO 1 ARGUMENTO 2]
        mensagem = f"{IP}:{PORTA} {clock} {tipo}"
        peer_socket.send(mensagem.encode())
        print(f"Encaminhando mensagem {mensagem} para {peer.IP}:{peer.PORTA}")
    except Exception as e:
        print(f"Erro ao enviar mensagem {e}")
        peer_socket.close()
        peer.STATUS = "OFFLINE"
        print(f"Atualizando peer {peer.IP}:{peer.PORTA} status {peer.STATUS}")
    else:
        peer.STATUS = "ONLINE"
        print(f"Atualizando peer {peer.IP}:{peer.PORTA} status {peer.STATUS}")

    peer_socket.close()

# Função de listar peers
def listar_peers():
    print("[0] voltar para o menu anterior")
    i = 1
    for peer in lista_vizinhos:
        print(f"[{i}] {peer.IP}:{peer.PORTA} {peer.STATUS}")
        i = i + 1

    opt = int(input("> "))

    if opt == 0: return
    elif opt < len(lista_vizinhos): envia_mensagem(lista_vizinhos[opt - 1], "HELLO")
    else:
        print("Opção invalida")
        return

if opcao == 1:
    listar_peers()
elif opcao == 7:
    sys.exit()






