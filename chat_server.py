# Tcp chat server in Python 3

import socket, select, sys

rooms = {}

def send_private_message(sender_sock, recipient_name, message):
    # Check if the recipient exists in the nicknames dictionary
    for sock, (nick, room) in nicknames.items():
        if nick == recipient_name:
            try:
                # Send a private message to the recipient
                private_msg = f"PRIVATE {nicknames[sender_sock][0]} {message}"
                sock.send(private_msg.encode())
                return "OK"
            except:
                return "ERROR"
    
    # If the recipient does not exist, return ERROR
    return "ERROR"

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

# Function to broadcast chat messages to all connected clients in a specific room
def broadcast_message_in_room(data, sender_socket, connection_list, sender_name, room_name) -> None:
    for sock in connection_list:
        if sock != server_socket and sock != sender_socket and nicknames[sock][1] == room_name:
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
        room_name = msg
        join_room(sock, room_name)
        print(f"{nicknames[sock][0]} joined room '{room_name}'")
    elif msg.startswith("leave"):
        leave_room(sock)
        print(f"{nicknames[sock][0]} left the room")
    elif msg.startswith("bye"):
        exit_sock(addr, sock, connection_list)
    elif msg.startswith("priv"):
        _, recipient, private_msg = msg.split(" ", 2)
        result = send_private_message(sock, recipient, private_msg)
        print(result)
        sock.send(result.encode())
    else:
        return False
    return True

def join_room(sock, room_name):
    nicknames[sock] = (nicknames[sock][0], room_name)
    if room_name not in rooms:
        rooms[room_name] = []
    rooms[room_name].append(sock)

def leave_room(sock):
    room_name = nicknames[sock][1]
    if room_name in rooms:
        rooms[room_name].remove(sock)
    nicknames[sock] = (nicknames[sock][0], "")

def exit_sock(addr, sock, connection_list) -> None:
    print("Closing connection to (%s, %s)" % addr)
    sock.close()
    connection_list.remove(sock)


def change_nickname(sock, msg, nicknames) -> bool:
    candidate = msg[5:].strip()  # everything after "/nick "
    if candidate == "you":
        return False

    for s, (nick, room) in nicknames.items():
        if candidate == nick:
            return False

    # Update the nickname and keep the room information
    nicknames[sock] = (candidate, nicknames.get(sock, ("", ""))[1])
    return True


def processInput(addr, sock, connection_list, nicknames) -> bool:
    try:
        data = sock.recv(RECV_BUFFER)
        if data:
            message = data.decode("utf-8").strip()
            if not check_commands(addr, sock, connection_list, nicknames, message):
                if not sock in nicknames:
                    nicknames[sock] = ("guest", "")  # Default room is an empty string
                nickname, room_name = nicknames[sock]
                
                # Check if the user is in a room before broadcasting the message
                if room_name:
                    print(f"[{nickname}@{room_name}] {message}")
                    broadcast_message_in_room(data, sock, connection_list, nickname, room_name)
                else:
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
