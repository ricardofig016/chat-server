# Chat Client
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter, sys


def append_message(msg):
    # Add the received message to the message list
    msg_list.insert(tkinter.END, msg)


def receive():
    # Handle message receiving.  May block, since it runs in a separate thread.
    while True:
        try:
            # Receive messages, calling append_message() to add them to the list
            msg = client_socket.recv(BUFSIZ).decode("utf-8")
            append_message(msg)
        except OSError:  # Possibly client has left the chat
            break


def send(event=None):  # event is passed by binders
    # Handle message sending
    msg = my_msg.get()  # Message to send
    my_msg.set("")  # Clear the input field after getting the message to send
    if msg:
        # Do the actual sending
        client_socket.send(bytes(msg, "utf-8"))
        if not check_commands(msg):
            append_message("[you] " + msg)


def check_commands(msg) -> bool:
    if msg[0] != "/":
        return False
    msg = msg[1:]
    if msg.startswith("nick"):
        pass
    elif msg.startswith("join"):
        join_room(msg[5:].strip())
    elif msg.startswith("leave"):
        leave_room()
    elif msg.startswith("bye"):
        exit_socket()
    elif msg.startswith("priv"):
        _, recipient, private_msg = msg.split(" ", 2)
        send_private_message(recipient, private_msg)
    else:
        return False
    return True

def send_private_message(recipient, private_msg):
    client_socket.send(bytes(f"/priv {recipient} {private_msg}", "utf-8"))

def join_room(room_name):
    client_socket.send(bytes(f"/join {room_name}", "utf-8"))
    append_message(f"Joined room '{room_name}'")

def leave_room():
    client_socket.send(bytes("/leave", "utf-8"))
    append_message("Left the room")


def exit_socket():
    client_socket.close()
    top.quit()
    sys.exit()


# GUI initialization
top = tkinter.Tk()
top.title("ChatClient")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(
    messages_frame, height=15, width=60, yscrollcommand=scrollbar.set
)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
# msg_list.pack() # Redundant
messages_frame.pack()

entry_field = tkinter.Entry(top, width=60, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
entry_field.focus_set()


# Other initializations
if len(sys.argv) == 3:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
elif len(sys.argv) == 2:
    HOST = "localhost"
    PORT = int(sys.argv[1])
else:
    print("Usage: python chat_client.py [<host>] <port>")
    sys.exit(1)

BUFSIZ = 1024
ADDR = (HOST, PORT)

# Establish the connection
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

top.protocol("WM_DELETE_WINDOW", exit_socket)

# Create the receive thread and start the GUI
receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()
