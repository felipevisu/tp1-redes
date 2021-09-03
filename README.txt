# tp1redes - Parte 2 (Pontos extras)

Alunos: Felipe Faria, Matheus Melo


########################################################


Linguagem de programação utilizada: Python3
Bando de dados utilizado: SQLite


########################################################


COMO EXECUTAR

Com python3 instalado na máquina ou em um ambiente virtual seguir 
o seguinte processo:

1) Instalar biblioteca sqlalchemy
   pip install sqlalchemy

2) Utilizando python3, executar o arquivo ./server/database.py
   Este comando irá criar o banco de dados.

3) Utilizando python3, executar o arquivo ./server/server.py

4) Utilizando python3, executar em um terminal separado 
   o arquivo ./client/client.py

O arquivo client.py pode ser executado em em várias instâncias. 
A rede suporta conexão de multiplos usuários.

5) Para executar a opção com interface gráfica, instalar o 'tkinter'
   para python3 e executar o arquivo ./client/client_tkinter.py
   https://tkdocs.com/tutorial/install.html


########################################################


LOGIN

Com 'client.py' em execução realize seu login.
Opções disponíveis para login:
======================
username  ||  password
======================
felipe    ||   123456
matheus   ||   123456
guidoni   ||   123456


########################################################


COMANDOS POSSÍVEIS

ls
get <file>
put <file>
passwd
adduser <username>
removeuser <username>
