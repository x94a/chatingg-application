
import socket, select, os, sys, time, base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

if len(sys.argv) < 4:
    print('Usage: python server.py enter host port password')
    print("challenge accepted dr :) ")
    sys.exit(1)

def encrypt(key, source, encode=True):
    key = SHA256.new(key).digest()  
    IV = Random.new().read(AES.block_size)  
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(source) % AES.block_size 
    source += bytes([padding]) * padding
    data = IV + encryptor.encrypt(source) 
    return base64.b64encode(data).decode("latin-1") if encode else data

def decrypt(key, source, decode=True):
    if decode:
        source = base64.b64decode(source.encode("latin-1"))
    key = SHA256.new(key).digest()  
    IV = source[:AES.block_size]
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:]) 
    padding = data[-1]  
    if data[-padding:] != bytes([padding]) * padding:  
        raise ValueError("Invalid padding...")
    return data[:-padding]  

host = sys.argv[1]
port = sys.argv[2]
key = sys.argv[3].encode('utf-8')

SOCKET_LIST = [] 

def server(host, port):
    running = True
    online_users = []

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, int(port)))
    server_socket.listen(10)

    SOCKET_LIST.append(server_socket)

    #try:
    print('[%s] Server started on [%s:%i]' % (u'\u2139', host, int(port)))
    while running:
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],0)

        for sock in ready_to_read:
           
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)

                
                foo = '[SERVER] Welcome, you connected from %s:%s. The following users are online: %s' % (addr[0], addr[1], online_users)
                print("told you i can doo itt 2 weeks didn't sleep well untik finish it as you want <3  <3  ")
                foo = foo.encode('utf-8')
                foo = encrypt(key, foo)
                sockfd.send(foo.encode('utf-8'))


            else:
                try:
                    data = sock.recv(1024)

                    f = data

                    try:
                        data = decrypt(key, data.decode('utf-8'))
                    except Exception as e:
                        print(e)
                        pass

                    data = data.decode('utf-8')
                    print('%s [%s] %s (decrypted from: %s)' % (u'\u2705',addr[0], data, f.decode('utf-8')))

                    if '$' in data:
                        # i'am sorry but i copy this idea and put it in my project <3
                        if data.split('$')[0] == 'USER':
                            username = data.split('$')[1]
                            online_users.append(username) # Append to Online users
                            print(online_users)
                            message = '[SERVER] %s entered the server with id %s' % (username, addr[1])
                            message = message.encode('utf-8')
                            message = encrypt(key, message)
                            broadcast(server_socket, sockfd, message.encode('utf-8'))
                            #print(message)
                        # This targets the poked user
                        elif data.split('$')[0] == 'POKE':
                            message = '%s' % (data)
                            message = message.encode('utf-8')
                            message = encrypt(key, message)
                            broadcast(server_socket, sock, message.encode('utf-8'))
                        # Poke response to see if someone's online, report to poker
                        elif data.split('$')[0] == 'ONLINE':
                            message = '%s' % (data)
                            message = message.encode('utf-8')
                            message = encrypt(key, message)
                            broadcast(server_socket, sock, message.encode('utf-8'))
                        # Event when someone leaves the server
                        elif data.split('$')[0] == 'LEFT':
                            username = data.split('$')[1]
                            online_users.remove(username) # Remove from Online Users
                            message = '[SERVER] User %s left the server' % username
                            message = message.encode('utf-8')
                            message = encrypt(key, message)
                            broadcast(server_socket, sock, message.encode('utf-8'))


                    elif data:
                        data = data.strip()
                        # Send data to all clients
                        message = '\r[%s] %s' % (addr[1], data)
                        message = message.encode('utf-8')
                        message = encrypt(key, message)
                        broadcast(server_socket, sock, message.encode('utf-8'))


                    else:
                        # remove the socket that's broken
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                except:
                    message = "[SERVER] A Client left"
                    message = message.encode('utf-8')
                    message = encrypt(key, message)
                    broadcast(server_socket, sock, message.encode('utf-8'))
                    #if someone leave chat write  "Client left") BLINK
                    continue

    server_socket.close()

# send message to all clients
def broadcast(server_socket, sock, message):
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock :
            try:
                socket.send(message)
            except:
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)

# Start server
server(host, int(port))
