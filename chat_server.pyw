import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

# Configure server address and port
HOST = '192.168.1.103'  # Use local address for listening (can use public IP)
PORT = 12345  # Choose an unoccupied port number

# Save connected clients and usernames
clients = []
usernames = {}

class ChatServer:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Server")

        self.frame = tk.Frame(root)
        self.scrollbar = scrolledtext.ScrolledText(self.frame, state='disabled', wrap=tk.WORD)
        self.scrollbar.pack(expand=True, fill='both', padx=10, pady=10)
        self.frame.pack(expand=True, fill='both')

        self.user_list_label = tk.Label(root, text="Currently Online Users")
        self.user_list_label.pack(padx=10, pady=1, side='top')

        self.user_list = tk.Listbox(root, height=10, width=100)  # Adjust height and width as needed
        self.user_list.pack(padx=10, pady=10, side='right', fill='y')

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen()
        self.display_message(f'Server started on {HOST}:{PORT}\n')

        self.accept_thread = threading.Thread(target=self.accept_clients)
        self.accept_thread.daemon = True
        self.accept_thread.start()

    def display_message(self, message):
        """Display message in the GUI"""
        self.scrollbar.config(state='normal')
        self.scrollbar.insert(tk.END, message)
        self.scrollbar.yview(tk.END)
        self.scrollbar.config(state='disabled')

    def update_user_list(self):
        """Update user list"""
        self.user_list.delete(0, tk.END)
        for username, addr in usernames.items():
            self.user_list.insert(tk.END, f"User: {username} , IP: {addr[0]}")

    def broadcast(self, message, _client):
        """Broadcast message to all connected clients"""
        for client in clients:
            if client != _client:
                try:
                    client.send(message)
                except:
                    client.close()
                    clients.remove(client)

    def handle_client(self, client, addr):
        """Handle connection from a single client"""
        try:
            username = client.recv(1024).decode('utf-8')
            clients.append(client)
            usernames[username] = addr
            self.display_message(f"New connection {username} from {addr}\n")
            self.update_user_list()
            self.broadcast(f"User {username} joined the chatroom".encode('utf-8'), client)
        except:
            self.remove_client(client)
            return

        while True:
            try:
                message = client.recv(1024)
                if not message:
                    break
                self.display_message(f"{username}: {message.decode('utf-8')}\n")
                self.broadcast(message, client)
            except:
                self.remove_client(client)
                break

    def accept_clients(self):
        """Accept new client connections"""
        while True:
            client, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(client, addr))
            thread.daemon = True
            thread.start()

    def remove_client(self, client):
        """Remove client"""
        if client in clients:
            clients.remove(client)
            username = usernames[client]
            del usernames[client]
            self.broadcast(f"User {username} left the chatroom.".encode('utf-8'), client)
            self.display_message(f"User {username} disconnected.\n")
            self.update_user_list()

def start_server():
    root = tk.Tk()
    server = ChatServer(root)
    root.mainloop()

if __name__ == "__main__":
    start_server()
