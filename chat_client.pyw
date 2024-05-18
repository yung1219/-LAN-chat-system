import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox

# Configure server address and port
HOST = '192.168.1.103'  # Use local address for listening
PORT = 12345  # Choose an unoccupied port number

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")

        self.username = simpledialog.askstring("Username", "Enter your username:", parent=root)
        if not self.username:
            messagebox.showerror("Error", "Username cannot be empty")
            root.quit()
            return

        self.setup_ui()

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((HOST, PORT))
            self.client.send(self.username.encode('utf-8'))
            self.display_message("Connected to server\n")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.root.destroy()

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill='both')

        # Message display area
        self.scrollbar = scrolledtext.ScrolledText(self.frame, state='disabled', wrap=tk.WORD)
        self.scrollbar.pack(expand=True, fill='both', padx=10, pady=10)

        # User list
        self.user_list = tk.Listbox(self.frame, width=20)
        self.user_list.pack(padx=10, pady=10, side='right', fill='y')

        # Input field and send button
        self.entry_frame = tk.Frame(self.frame)
        self.entry_frame.pack(padx=10, pady=5, fill='x')

        self.entry = tk.Entry(self.entry_frame, width=50, bg="white")
        self.entry.pack(side='left', fill='x', expand=True)
        self.entry.bind("<Return>", self.send_message)

        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.send_message, bg="green", fg="white")
        self.send_button.pack(side='left', padx=5)

    def display_message(self, message):
        """Display message in the GUI"""
        self.scrollbar.config(state='normal')
        self.scrollbar.insert(tk.END, message)
        self.scrollbar.yview(tk.END)
        self.scrollbar.config(state='disabled')

    def update_user_list(self, user_list):
        """Update user list"""
        self.user_list.delete(0, tk.END)
        for user in user_list:
            self.user_list.insert(tk.END, user)

    def receive_messages(self):
        """Receive messages from the server"""
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message.startswith("USERLIST:"):
                    user_list = message[len("USERLIST:"):].split(',')
                    self.update_user_list(user_list)
                else:
                    self.display_message(message + "\n")
            except:
                self.display_message("An error occurred.\n")
                self.client.close()
                break

    def send_message(self, event=None):
        """Send message to the server"""
        message = self.entry.get()
        self.entry.delete(0, tk.END)
        if message:
            try:
                full_message = f"{self.username}: {message}"
                self.client.send(full_message.encode('utf-8'))
                self.display_message(f"You: {message}\n")
            except:
                self.display_message("Failed to send message\n")

def start_client():
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()

if __name__ == "__main__":
    start_client()
