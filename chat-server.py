# Tcp chat server in Python 3

import socket, select, sys


# Function to broadcast chat messages to all connected clients
def broadcast_message(data, sender_socket, CONNECTION_LIST, sender_name):
    for sock in CONNECTION_LIST:
        if sock != server_socket and sock != sender_socket:
            try:
                # Include the sender's nickname in the message
                full_data = "[" + sender_name + "] " + data.decode()
                sock.send(full_data.encode())
            except:
                sock.close()
                CONNECTION_LIST.remove(sock)


# Function to receive the sender's nickname
def receive_nickname(sock):
    nickname_data = sock.recv(RECV_BUFFER)
    nickname = nickname_data.decode("utf-8").strip()
    return nickname


# Function to broadcast chat messages to all connected clients
def processInput(sock, CONNECTION_LIST) -> bool:
    try:
        data = sock.recv(RECV_BUFFER)
        message = data.decode("utf-8").strip()
        if data:
            print(f"[nickname] {message}")
            broadcast_message(data, sock, CONNECTION_LIST, "nickname")
        else:
            return False
    except:
        return False

    return True


if __name__ == "__main__":
    # List to keep track of socket descriptors
    CONNECTION_LIST = []
    RECV_BUFFER = 4096  # Advisable to keep it as an exponent of 2
    PORT = int(sys.argv[1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", PORT))
    server_socket.listen(10)

    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)

    print("Listening on port " + str(PORT))

    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets, write_sockets, error_sockets = select.select(
            CONNECTION_LIST, [], []
        )

        for sock in read_sockets:
            # New connection
            if sock == server_socket:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                sockfd.setblocking(False)
                print("Got connection from (%s, %s)" % addr)

            # Some incoming message from a client
            else:
                # Data recieved from client, process it
                if not processInput(sock, CONNECTION_LIST):
                    print("Closing connection to (%s, %s)" % addr)
                    sock.close()
                    CONNECTION_LIST.remove(sock)

    server_socket.close()
