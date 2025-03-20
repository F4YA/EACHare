import sys

if len(sys.argv) != 4:
    print("Uso correto: python3 <nome>.py <endereço>:<porta> <vizinhos.txt> <diretório_compartilhado>")
    sys.exit(1)

IP = sys.argv[1].split(":")[0]
PORTA = sys.argv[1].split(":")[1]
vizinhos = sys.argv[2]
diretorio_compartilhado = sys.argv[3]



