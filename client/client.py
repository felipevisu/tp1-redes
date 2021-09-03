import os
import socket
import struct
import sys

HOST = '127.0.0.1'
PORT = 65431
BUFFER_SIZE = 1024


def ls():
    # Envia o comando 'ls' para o servidor
    try:
        sock.send(bytes('ls', 'utf-8'))
    except:
        print('Não foi possível estabelecer uma coneção com o servidor')
        return

    try:
        total_files = struct.unpack('i', sock.recv(4))[0] # Total de arquivos
        # Recebe o nome de cada arquivo separadamente
        for _ in range(total_files):
            item_size = struct.unpack('i', sock.recv(4))[0] # Tamanho do nome do arquivo
            item = sock.recv(item_size) # Nome do arquivo
            item = item.decode('utf-8')
            print(item)
    except:
        print('Erro ao obter a lista de arquivos')
        return


def put(file_name):
    # Abre o arquivo na máquina do usuário
    try:
        file = open(file_name, 'rb')
    except:
        print('Não foi possível encontrar o arquivo expecificado.')
        return

    # Envia o comando 'put' para o servidor
    try:
        sock.send(bytes('put', 'utf-8'))
    except:
        print('Não foi possível estabelecer uma coneção com o servidor')
        return

    # Envia os dados do arquivo para o servidor
    try:
        sock.send(struct.pack('i', len(file_name))) # Tamanho do nome do arquivo
        sock.send(bytes(file_name, 'utf-8')) # Nome do arquivo
        sock.send(struct.pack('i', os.path.getsize(file_name))) # Tamanho do arquivo
    except:
        print('Erro ao enviar os dados do arquivo')

    # Envia o arquivo para o servidor
    try:
        l = file.read(BUFFER_SIZE)
        while l:
            sock.send(l)
            l = file.read(BUFFER_SIZE)
        file.close()
    except:
        print('Erro ao enviar o arquivo')
        return


def get(file_name):
    # Envia o comando 'get' para o servidor
    try:
        sock.send(bytes('get', 'utf-8'))
    except:
        print('Não foi possível estabelecer uma coneção com o servidor')
        return

    # Envia os dados do arquivo para o servidor
    try:
        sock.send(struct.pack('i', len(file_name))) # Tamanho do nome do arquivo
        sock.send(bytes(file_name, 'utf-8')) # Nome do arquivo
    except:
        print('Erro ao enviar os dados do arquivo')

    # Aguarda o servidor verificar se o arquivo existe
    success = struct.unpack('?', sock.recv(1))[0]
    if not success:
        print('Arquivo não existe')
        return

    # Recebe o arquivo do servidor
    try:
        file_size = struct.unpack('i', sock.recv(4))[0] # Tamanho do arquivo
        output_file = open(file_name, 'wb')
        bytes_recieved = 0
        while bytes_recieved < file_size:
            l = sock.recv(BUFFER_SIZE)
            output_file.write(l)
            bytes_recieved += BUFFER_SIZE
        output_file.close()
    except:
        print('Erro ao receber o arquivo')
        return


def password():
   # Envia o comando 'passwd' para o servidor
    try:
        sock.send(bytes('passwd', 'utf-8'))
    except:
        print('Não foi possível estabelecer uma coneção com o servidor')
        return

    # Recebe a nova senha do usuário
    new_pass = input('Digite sua nova senha: ')

    # Envia a nova senha para o servidor
    try:
        sock.send(struct.pack('i', len(new_pass))) # Tamanho do senha
        sock.send(bytes(new_pass, 'utf-8')) # Senha
    except:
        print('Erro ao enviar a nova senha')

    # Recebe a resposta do servidor
    response = struct.unpack('?', sock.recv(1))[0]
    if response:
        print('Senha alterada com sucesso')
    else:
        print('Não foi possível alterar sua senha')


def adduser(username):
    # Envia o comando 'adduser' para o servidor
    try:
        sock.send(bytes('adduser', 'utf-8'))
    except:
        print('Não foi possível estabelecer uma coneção com o servidor')
        return

    # Envia o novo usuário para o servidor
    try:
        sock.send(struct.pack('i', len(username))) # Tamanho do username
        sock.send(bytes(username, 'utf-8')) # Username
    except:
        print('Erro ao enviar o novo usuário')

    # Recebe a resposta do servidor
    response = struct.unpack('?', sock.recv(1))[0]
    if response:
        print("Usuário '%s' criado com sucesso" % username)
    else:
        print('Não foi possível criar o novo usuário')


def removeuser(username):
    # Envia o comando 'removeuser' para o servidor
    try:
        sock.send(bytes('removeuser', 'utf-8'))
    except:
        print('Não foi possível estabelecer uma coneção com o servidor')
        return

    # Envia o username para o servidor
    try:
        sock.send(struct.pack('i', len(username))) # Tamanho do username
        sock.send(bytes(username, 'utf-8')) # Username
    except:
        print('Erro ao enviar o usuário a ser removido')

    # Recebe a resposta do servidor
    response = struct.unpack('?', sock.recv(1))[0]
    if response:
        print("Usuário '%s' removido com sucesso" % username)
    else:
        print("Não foi possível remover o usuário '%s' ou ele não existe" % username)


def login():
    response = False
    while not response:
        # Envia o username para o servidor
        username = input('Digite seu nome de usuário: ')
        sock.send(struct.pack('i', len(username)))
        sock.send(bytes(username, 'utf-8'))
        # Envia o password para o servidor
        password = input('Digite sua senha: ')
        sock.send(struct.pack('i', len(password)))
        sock.send(bytes(password, 'utf-8'))
        # Recebe a validação
        response = struct.unpack('?', sock.recv(1))[0]
        if not response:
            print('Usuário e/ou senha inválidos')
    print('Login realizado com sucesso')


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

response = struct.unpack('?', sock.recv(1))[0]
if response:
    print('Bem vindo ao MyFTP')
    login()
    try:
        while True:
            command = input('Digite uma instrução: ')
            if command == 'ls':
                ls()
            elif command == 'passwd':
                password()
            elif command[:7] == 'adduser':
                adduser(command[8:])
            elif command[:10] == 'removeuser':
                removeuser(command[11:])
            elif command[:3] == 'put':
                put(command[4:])
            elif command[:3] == 'get':
                get(command[4:])
            else:
                print('Instrução inválida')
    except KeyboardInterrupt:
        sys.exit(0)
else:
    print('Não possível se conectar ao servidor.')

sock.close()
