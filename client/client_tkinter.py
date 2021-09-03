import os
import socket
import struct
from tkinter import *
from tkinter.filedialog import askopenfilename

HOST = '127.0.0.1'
PORT = 65432
BUFFER_SIZE = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

global userIsAdmin
userIsAdmin = False

def fechar():
    sock.close()
    exit(1)


class LoginWindow(Toplevel):

    def __init__(self,master=None):
        Toplevel.__init__(self)
        self.title('Login')
        self.geometry('295x180')
        labelUserName = Label(self , text='Username')
        boxUserName = Entry(self)

        labelUserName.place(x=20 , y=20)
        boxUserName.place(x=100 , y=20)

        labelPassword = Label(self, text='Password')
        boxPassword = Entry(self , show='*')

        labelPassword.place(x=20 , y=70)
        boxPassword.place(x=100 , y=70)
        labelStatus = Label(self,text='')
        labelStatus.place(x=50 , y=100)
        def login():
            global username
            username = boxUserName.get()
            sock.send(struct.pack('i' , len(username)))
            sock.send(bytes(username , 'utf-8'))
            # Envia o password para o servidor
            password = boxPassword.get()
            sock.send(struct.pack('i' , len(password)))
            sock.send(bytes(password , 'utf-8'))
            # Recebe a validação
            response = struct.unpack('?' , sock.recv(1))[0]
            if not response:
                labelStatus.config(text="Usuario ou senha invalido",foreground='red')

            else:
                labelStatus.config(text='OK' , foreground='green')
                if username=="admin":
                    global userIsAdmin
                    userIsAdmin=True
                self.destroy()

        botaoFechar = Button(self , text='Fechar' , command=fechar)
        botaoFechar.place(x=40 , y=140)

        botaoEntrar = Button(self , text='Entrar' , command=login)
        botaoEntrar.place(x=170 , y=140)

class UserWindow(Toplevel):
    def __init__(self, master = None):
        Toplevel.__init__(self)
        self.title('Gerenciar usuário')

        boxStatus = Entry(self,width=24)
        boxStatus.place(x=0 , y=175)

        def remover():
            # Envia o comando 'removeuser' para o servidor
            try:
                sock.send(bytes('removeuser' , 'utf-8'))
            except:
                print('Não foi possível estabelecer uma conexão com o servidor')
                return

            # Envia o username para o servidor
            try:
                sock.send(struct.pack('i' , len(username)))  # Tamanho do username
                sock.send(bytes(username , 'utf-8'))  # Username
            except:
                print('Erro ao enviar o usuário a ser removido')

            # Recebe a resposta do servidor
            response = struct.unpack('?' , sock.recv(1))[0]
            if response:
                print("Usuário '%s' removido com sucesso" % username)
            else:
                print("Não foi possível remover o usuário '%s' ou ele não existe" % username)
        botaoRemover = Button(self, text="Excluir Conta", command=remover)
        botaoRemover.place(x=40,y=20)

        def altSenha():



        botaoSenha = Button(self,text="Alterar Senha",command=altSenha)
        botaoSenha.place(x=40,y=75)

        botaoCadastrar = Button(self , text="Cadastrar Usuário")
        botaoCadastrar.pack(anchor=CENTER)
        botaoCadastrar.place(x=25,y=130)



mainWindow = Tk()
mainWindow.title("MyFTP")
mainWindow.lift()

mainWindow.geometry('447x230')

botaoSair=Button(mainWindow,text='Sair',command=fechar)
botaoSair.place(x=370,y=170)

tabelaArquivos = Listbox(mainWindow,height=6)
tabelaArquivos.place(x=20,y=40)

boxStatus = Entry(mainWindow,width=55)
boxStatus.place(x=0,y=206)

def ls():
    # Envia o comando 'ls' para o servidor
    try:
        sock.send(bytes('ls', 'utf-8'))
    except:
        boxStatus.delete(0,'end')
        boxStatus.config(fg='red')
        boxStatus.insert(0,'Não foi possível estabelecer uma coneção com o servidor')
        return

    try:
        total_files = struct.unpack('i', sock.recv(4))[0]  # Total de arquivos
        # Recebe o nome de cada arquivo separadamente
        tabelaArquivos.delete(0,tabelaArquivos.size()-1)
        for _ in range(total_files):
            item_size = struct.unpack('i', sock.recv(4))[0]  # Tamanho do nome do arquivo
            item = sock.recv(item_size)  # Nome do arquivo
            item = item.decode('utf-8')
            tabelaArquivos.insert(tabelaArquivos.size(),item)
    except:
        boxStatus.delete(0,'end')
        boxStatus.config(fg='red')
        boxStatus.insert(0,'Erro ao obter a lista de arquivos')

def get():
    file_name = tabelaArquivos.get(tabelaArquivos.curselection())
    if not file_name:
        boxStatus.delete(0,'end')
        boxStatus.config(fg='red')
        boxStatus.insert(0 , 'Nenhum arquivo selecionado')
        return
    # Envia o comando 'get' para o servidor
    try:
        sock.send(bytes('get', 'utf-8'))
    except:
        boxStatus.delete(0,'end')
        boxStatus.config(fg='red')
        boxStatus.insert('Não foi possível estabelecer uma coneção com o servidor')
        return

    # Envia os dados do arquivo para o servidor
    try:
        sock.send(struct.pack('i', len(file_name)))  # Tamanho do nome do arquivo
        sock.send(bytes(file_name, 'utf-8'))  # Nome do arquivo
    except:
        boxStatus.delete(0,'end')
        boxStatus.config(fg='red')
        boxStatus.insert(0,'Erro ao enviar os dados do arquivo')

    # Aguarda o servidor verificar se o arquivo existe
    success = struct.unpack('?', sock.recv(1))[0]
    if not success:
        boxStatus.delete(0,'end')
        boxStatus.config(fg='red')
        boxStatus.insert(0,'Arquivo não existe')
        return

    # Recebe o arquivo do servidor
    try:
        file_size = struct.unpack('i', sock.recv(4))[0]  # Tamanho do arquivo
        output_file = open(file_name, 'wb')
        bytes_recieved = 0
        while bytes_recieved < file_size:
            l = sock.recv(BUFFER_SIZE)
            output_file.write(l)
            bytes_recieved += BUFFER_SIZE
        boxStatus.delete(0,'end')
        boxStatus.config(fg='green')
        boxStatus.insert(0,'Arquivo recebido com sucesso!')
        output_file.close()
    except:
        boxStatus.delete(0,'end')
        boxStatus.config(fg='red')
        boxStatus.insert(0,'Erro ao receber o arquivo')
        return


boxPath = Entry(mainWindow)
boxPath.place(x=260,y=60)

def selecionaArquivo():
    path = askopenfilename(title="Escolha um arquivo")
    boxPath.insert(0,path)

def put():
    file_name = boxPath.get()

    file_name_send = boxPath.get().split('/')[len(boxPath.get().split('/'))-1]
    # Abre o arquivo na máquina do usuário
    try:
        file = open(file_name, 'rb')
    except:
        boxStatus.delete(0,'end')
        boxStatus.config(fg='red')
        boxStatus.insert('Não foi possível encontrar o arquivo expecificado.')
        return

    # Envia o comando 'put' para o servidor
    try:
        sock.send(bytes('put', 'utf-8'))
    except:
        boxStatus.delete(0,'end')
        boxStatus.config(fg='red')
        boxStatus.insert('Não foi possível estabelecer uma coneção com o servidor')
        return

    # Envia os dados do arquivo para o servidor
    try:
        sock.send(struct.pack('i', len(file_name_send)))  # Tamanho do nome do arquivo
        sock.send(bytes(file_name_send, 'utf-8'))  # Nome do arquivo
        sock.send(struct.pack('i', os.path.getsize(file_name)))  # Tamanho do arquivo
    except:
        boxStatus.delete(0,'end')
        boxStatus.config(fg='red')
        boxStatus.insert('Erro ao enviar os dados do arquivo')

    # Envia o arquivo para o servidor
    try:
        l = file.read(BUFFER_SIZE)
        while l:
            sock.send(l)
            l = file.read(BUFFER_SIZE)
        boxStatus.delete(0,'end')
        boxStatus.config(fg='green')
        boxStatus.insert(0,"Arquivo enviado com sucesso!")
        file.close()
    except:
        boxStatus.delete(0,'end')
        boxStatus.config(fg='red')
        boxStatus.insert('Erro ao enviar o arquivo')
        return

botaoAtualizarLista = Button(mainWindow,text='Atualizar',command=ls)
botaoAtualizarLista.place(x=25,y=170)

botaoGet = Button(mainWindow,text='Get',command=get)
botaoGet.place(x=125,y=170)

labelGet = Label(mainWindow,text='Get:')
labelGet.place(x=20,y=18)

labelPut = Label(mainWindow,text='Put:')
labelPut.place(x=200,y=20)

labelPath = Label(mainWindow,text='Path:')
labelPath.place(x=220, y=60)

botaoPut = Button(mainWindow,text='Put',command=put)
botaoPut.place(x=370,y=110)

botaoEscolherArquivo = Button(mainWindow,text='Escolher Arquivo', command=selecionaArquivo)
botaoEscolherArquivo.place(x=225,y=110)

def gerenciar():
    userWindow = UserWindow(mainWindow)
    userWindow.mainloop()

botaoUser = Button(mainWindow,text='Gerenciar Usuários', command=gerenciar)
botaoUser.place(x=210,y=170)

loginWindow = LoginWindow(mainWindow)
loginWindow.mainloop()

mainWindow.mainloop()



