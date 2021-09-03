import os
import socket
import struct
import sys
import traceback

from threading import Thread
from sqlalchemy.orm import sessionmaker

from database import authenticated, change_password, create_user, delete_user, engine

Session = sessionmaker(bind=engine)
Session.configure(bind=engine)

HOST = '127.0.0.1'
PORT = 65431
BUFFER_SIZE = 1024


def ls(conn):
    listing = os.listdir(os.getcwd()) # Lita de arquivos
    conn.send(struct.pack('i', len(listing))) # Envia a quantidade de arquivos para o cliente
    # Envia o nome de cada arquivo separadamente
    for item in listing:
        conn.send(struct.pack('i', len(item)))
        conn.send(bytes(item, 'utf-8'))


def put(conn):
    # Recebe os dados do arquivo do cliente
    file_name_size = struct.unpack('i', conn.recv(4))[0]
    file_name = conn.recv(file_name_size)
    file_name = file_name.decode('utf-8')
    file_size = struct.unpack('i', conn.recv(4))[0]
    # Abre o arquivo
    output_file = open(file_name, 'wb')
    bytes_recieved = 0
    # Recebe o arquivo do cliente
    while bytes_recieved < file_size:
        l = conn.recv(BUFFER_SIZE)
        output_file.write(l)
        bytes_recieved += BUFFER_SIZE
    output_file.close()


def get(conn):
    # Recebe os dados do arquivo do cliente
    file_name_size = struct.unpack('i', conn.recv(4))[0]
    file_name = conn.recv(file_name_size)
    file_name = file_name.decode('utf-8')

    # Verifica se o arquivo existe
    try:
        file = open(file_name, 'rb')
        conn.send(struct.pack('?', True))
    except:
        conn.send(struct.pack('?', False))
        return

    # Envia o arquivo para o cliente
    try:
        conn.send(struct.pack('i', os.path.getsize(file_name)))
        l = file.read(BUFFER_SIZE)
        while l:
            conn.send(l)
            l = file.read(BUFFER_SIZE)
        file.close()
    except:
        print('Erro ao enviar o arquivo')
        return


def password(session, conn, user):
    # Recebe os dados de senha do cliente
    new_pass_size = struct.unpack('i', conn.recv(4))[0]
    new_pass = conn.recv(new_pass_size)
    new_pass = new_pass.decode('utf-8')
    # Altera a informação no banco de dados
    response = change_password(session, user, new_pass)
    # Envia para o cliente a resposta
    conn.send(struct.pack('?', response))


def adduser(session, conn):
    # Recebe os dados de usuário do cliente
    new_user_size = struct.unpack('i', conn.recv(4))[0]
    new_user = conn.recv(new_user_size)
    new_user = new_user.decode('utf-8')
    # Cria o novo usuário no banco de dados
    response = create_user(session, new_user)
    # Envia para o cliente a resposta
    conn.send(struct.pack('?', response))


def removeuser(session, conn):
    # Recebe os dados de usuário do cliente
    del_user_size = struct.unpack('i', conn.recv(4))[0]
    del_user = conn.recv(del_user_size)
    del_user = del_user.decode('utf-8')
    # Cria o novo usuário no banco de dados
    response = delete_user(session, del_user)
    # Envia para o cliente a resposta
    conn.send(struct.pack('?', response))


def login(session, conn):
    response = False
    while not response:
        # Recebe o username do cliente
        username_size = struct.unpack('i', conn.recv(4))[0]
        username = conn.recv(username_size)
        username = username.decode('utf-8')
        # Recebe o password do cliente
        password_size = struct.unpack('i', conn.recv(4))[0]
        password = conn.recv(password_size)
        password = password.decode('utf-8')
        # Autentica o usuário
        user = authenticated(session, username, password)
        if user:
            conn.send(struct.pack('?', True))
            print("Usuário conectado:", user)
            response = True
        else:
            conn.send(struct.pack('?', False))
    return user


# Função executada dentro da thread do cliente
def client_thread(conn):
    conn.send(struct.pack('?', True))
    session = Session()
    user = login(session, conn)
    while True:
        data = conn.recv(BUFFER_SIZE)
        if not data:
            break
        data = data.decode('utf-8')
        if data == 'ls':
            ls(conn)
        elif data == 'put':
            put(conn)
        elif data == 'get':
            get(conn)
        elif data == 'passwd':
            password(session, conn, user)
        elif data == 'adduser':
            adduser(session, conn)
        elif data == 'removeuser':
            removeuser(session, conn)
    conn.close()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen()

print('O servidor está em execução.')

try:
    while True:
        conn, addr = sock.accept()
        print('Nova conexão:', addr[0], ':', addr[1])
        # Cria uma nova thread para o cliente
        try:
            Thread(target=client_thread, args=[conn]).start()
        except:
            print("Thread did not start.")
            traceback.print_exc()
except KeyboardInterrupt:
    sys.exit(0)

sock.close()
