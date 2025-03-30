import os
import sys
import socket
import threading
from pathlib import Path

IP: str
PORTA: int
VIZINHOS: str
DIRETORIO: str
CLOCK: int
lista_vizinhos = []
encerrar = False

#----------Funções especificas dos tipos de requisição---------------------------
def hello_req(new_peer):
    ip, porta = new_peer.split(":")
    porta = int(porta)

    for peer in lista_vizinhos:
        if peer.ip == ip and peer.porta == porta:
            peer.att_status("ONLINE")
            return
    lista_vizinhos.append(Peer(ip, porta, "ONLINE"))

def bye_req(origem):
    ip, porta = origem.split(":")
    porta = int(porta)

    for peer in lista_vizinhos:
        if peer.ip == ip and peer.porta == porta:
            peer.att_status("OFFLINE")
            break

def get_peers_req(origem):
    argumentos = f"{len(lista_vizinhos)} "
    peer: Peer
    exists = True

    ip, porta = origem.split(":")
    porta = int(porta)

    for vizinho in lista_vizinhos:
        if vizinho.ip == ip and vizinho.porta == porta:
            peer = vizinho
            exists = False
            continue
        argumentos += f"{vizinho.ip}:{vizinho.porta}:{vizinho.status}:0 "

    if exists:
        peer = Peer(ip, porta, "ONLINE")
        lista_vizinhos.append(peer)

    envia_mensagem(peer, "PEER_LIST", argumentos)

def peer_list_req(origem, args):
    for peer in args:
        ip, porta, status, x = peer.split(":")
        porta = int(porta)
        exists = False

        for vizinho in lista_vizinhos:
            if vizinho.ip == ip and vizinho.porta == porta:
                vizinho.att_status(status)
                exists = True
                break

        if exists: continue
        lista_vizinhos.append(Peer(ip, int(porta), status))

#-------------------------------------------------------------

#Função que inicia o servidor
def inicia_server():
    server.listen()
    server.settimeout(1)
    print(f"Servidor iniciado em {IP}:{PORTA}")

    while not encerrar:
        try:
            req, addr = server.accept()
            cliente_thread = threading.Thread(target=tratar_req, args=(req,), daemon=True)
            cliente_thread.start()
        except socket.timeout:
            continue
        except OSError:
            break

# Função de enviar mensagem para os peers como especificado em 2.1 - EP: Parte 1
def envia_mensagem(peer, tipo, args = None):
    global IP, PORTA, CLOCK
    msg_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        msg_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        msg_socket.connect((peer.ip, int(peer.porta)))
        # <ORIGEM> <CLOCK> <TIPO> [ARGUMENTO 1 ARGUMENTO 2]
        CLOCK = CLOCK + 1

        if args is not None:
            mensagem = f"{IP}:{PORTA} {CLOCK} {tipo} {args}"
        else:
            mensagem = f"{IP}:{PORTA} {CLOCK} {tipo}"

        msg_socket.send(f"{mensagem + '\n'}".encode())

        print(f"=> Atualizando relogio para {CLOCK}")
        print(f"Encaminhando mensagem \"{mensagem}\" para {peer.ip}:{peer.porta}")
    except Exception as e:
        print(f"Erro ao enviar mensagem {e}")
        peer.status = "OFFLINE"
    else:
        peer.status = "ONLINE"

    msg_socket.close()

# Função que lida com a requisição do cliente
def tratar_req(req):
    global CLOCK
    while True:
        try:
            data = req.recv(1024).decode()
            if not data:
                break

            CLOCK = CLOCK + 1

            args = data.split("\n")

            args = args[0].strip().split(" ")

            origem = args.pop(0)
            tipo = args.pop(1)

            if tipo == "PEER_LIST":
                print(f"\nResposta recebida: \"{data}\"")
            else: print("\nMensagem recebida: ", data)
            print("=> Atualizando relogio para ", CLOCK)

            if tipo == "HELLO":
                hello_req(origem)
            elif tipo == "BYE":
                bye_req(origem)
            elif tipo == "GET_PEERS":
                get_peers_req(origem)
            elif tipo == "PEER_LIST":
                args.pop(0)  # remove o clock da mensagem
                args.pop(0)  # remove a quantidade de peers
                peer_list_req(origem, args)
        except:
            break
    req.close()

#------------------ Funções do Menu --------------------------
# Função de listar peers
def listar_peers():
    print("[0] voltar para o menu anterior")
    i = 1
    for peer in lista_vizinhos:
        print(f"[{i}] {peer.ip}:{peer.porta} {peer.status}")
        i = i + 1

    opt = int(input("> "))

    if opt == 0: return
    elif opt <= len(lista_vizinhos): envia_mensagem(lista_vizinhos[opt - 1], "HELLO")
    else:
        print("Opção invalida")
        return

def obter_peers():
    for peer in lista_vizinhos:
        envia_mensagem(peer, "GET_PEERS")

def listar_arquivos_locais():

    with os.scandir(DIRETORIO) as conteudos:
        for conteudo in conteudos:
            print(conteudo.name)

def buscar_arquivos():
    pass
def exibir_estatisticas():
    pass
def alterar_tamanho_chunk():
    pass

def sair():
    global encerrar
    encerrar = True

    for peer in lista_vizinhos:
        if peer.status == "ONLINE": envia_mensagem(peer, "BYE")

    server.close()
    sys.exit(0)

#-----------------------------------------------------------------------------
if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Uso correto: python3 <nome>.py <endereço>:<porta> <vizinhos.txt> <diretório_compartilhado>")
        sys.exit(1)

    IP = sys.argv[1].split(":")[0]
    PORTA = int(sys.argv[1].split(":")[1])
    VIZINHOS = sys.argv[2]
    DIRETORIO = sys.argv[3]
    CLOCK = 0

    # Verifica se o diretório de compartilhamento é um diretório válido e pode ser lido.
    caminho_diretorio = Path(DIRETORIO)

    if not caminho_diretorio.is_dir() or not os.access(caminho_diretorio, os.R_OK):
        print(f"Erro: '{DIRETORIO}' não é um diretório válido ou não pode ser lido.")
        sys.exit(1)

    # Parte que adiciona os peers do arquivo vizinhos.txt e apresenta saída solicitada conforme 2.3 EP: parte 1
    class Peer:
        def __init__(self, ip, porta, status):
            print(f"Adicionando novo peer {ip}:{porta} status {status}")
            self.ip = ip
            self.porta = porta
            self.status = status

        def att_status(self, status):
            self.status = status
            print(f"Atualizando peer {self.ip}:{self.porta} status {self.status}")

    with open(VIZINHOS, "r") as arquivo:
        for linha in arquivo:
            ip, porta = linha.split(":")
            lista_vizinhos.append(Peer(ip, int(porta), "OFFLINE"))

    # Criando o socket TCP conforme especificado em 2.3 EP: parte 1
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORTA))

    #Inicia o servidor
    server_thread = threading.Thread(target=inicia_server)
    server_thread.daemon = True
    server_thread.start()

    threading.Event().wait(1)


funcoes = [listar_peers, obter_peers, listar_arquivos_locais, buscar_arquivos, exibir_estatisticas, alterar_tamanho_chunk, sair]
while True:
    opcao = int(input("Escolha um comando:\n [1] Listar peers \n [2] Obter peers \n [3] Listar arquivos locais \n [4] Buscar arquivos \n [5] Exibir estatísticas \n [6] Alterar tamanho de chunk \n [7] Sair \n > "))
    if opcao in [1, 2, 3, 4, 5, 6, 7]:
        funcoes[opcao - 1]()
    else: print("Opção invalida")





