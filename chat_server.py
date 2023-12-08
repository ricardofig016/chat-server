# Tcp chat server in Python 3

import socket, select, sys


# Function to broadcast chat messages to all connected clients
def broadcast_message(data, sender_socket, connection_list, sender_name) -> None:
    for sock in connection_list:
        if sock != server_socket and sock != sender_socket:
            try:
                # Include the sender's nickname in the message
                full_data = "[" + sender_name + "] " + data.decode()
                sock.send(full_data.encode())
            except:
                sock.close()
                connection_list.remove(sock)


def check_commands(addr, sock, connection_list, nicknames, msg) -> bool:
    if msg[0] != "/":
        return False
    msg = msg[1:]
    if msg.startswith("nick"):
        if change_nickname(sock, msg, nicknames):
            print("OK")
        else:
            print("ERROR")
    elif msg.startswith("join"):
        pass
    elif msg.startswith("leave"):
        pass
    elif msg.startswith("bye"):
        exit_sock(addr, sock, connection_list)
    else:
        return False
    return True


def exit_sock(addr, sock, connection_list) -> None:
    print("Closing connection to (%s, %s)" % addr)
    sock.close()
    connection_list.remove(sock)


def change_nickname(sock, msg, nicknames) -> bool:
    candidate = msg[5:]  # tudo depois de "/nick "
    if candidate == "you":  # nick nao pode ser [you]
        return False
    for s, nick in nicknames.items():  # nick nao pode repetir
        if candidate == nick:
            return False
    nicknames[sock] = candidate
    # print(nicknames)
    return True


def processInput(addr, sock, connection_list, nicknames) -> bool:
    try:
        data = sock.recv(RECV_BUFFER)
        if data:
            message = data.decode("utf-8").strip()
            if not check_commands(addr, sock, connection_list, nicknames, message):
                if not sock in nicknames:
                    nicknames[sock] = "guest"
                nickname = nicknames[sock]
                print(f"[{nickname}] {message}")
                broadcast_message(data, sock, connection_list, nickname)
        else:
            return False
    except:
        return False
    return True


if __name__ == "__main__":
    # List to keep track of socket descriptors
    connection_list = []
    nicknames = {}
    RECV_BUFFER = 4096  # Advisable to keep it as an exponent of 2

    #Check if port is provided as an argument 
    if len(sys.argv) != 2:
        print("Usage: python chat_server.py <port>")
        sys.exit(1)
        
    PORT = int(sys.argv[1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)

    # Add server socket to the list of readable connections
    connection_list.append(server_socket)

    print("Listening on port " + str(PORT))

    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets, write_sockets, error_sockets = select.select(
            connection_list, [], []
        )

        for sock in read_sockets:
            # New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                connection_list.append(sockfd)
                sockfd.setblocking(False)
                print("Got connection from (%s, %s)" % addr)

            # Some incoming message from a client
            else:
                # Data recieved from client, process it
                if not processInput(addr, sock, connection_list, nicknames):
                    exit_sock(addr, sock, connection_list)

    server_socket.close()
