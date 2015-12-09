# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = "Trond Humborstad"

import socket, json, datetime
from MessageReceiver import MessageReceiver

class Client:
    """
    A simple client implementing the chat protocol.
    On initialization, the client creates a connection to the server. It then
    kicks off a background thread which listens for incoming messages. When a message
    is received from the server, the background thread calls receive_message with the 
    received message as an argument. receive_message formats the message nicely and displays it
    in the terminal. The client also loops for client input. When the user submits a message, 
    the dispatch() method is called which formats the message and sends it to the server.
    """

    def __init__(self, host, server_port):
        # Set up the socket connection to the server
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_host = host
        self.server_port = server_port
        self.username = "default_username"
        self.run()
        

    def run(self):
        # Initiate the connection to the server
        self.connection.connect((self.server_host, self.server_port))

        # We kick off a background thread which'll listen for incoming messages from
        # the server. Whenever a message from the server is received, the MessageReceiver
        # will call the receive_message method in this class.

        thread = MessageReceiver(self, self.connection)
        thread.start()

        # We listen for user input and send it to the dispatcher for formatting.
        while True:
            input_string = str(raw_input(""))
            self.dispatcher(input_string)

    def disconnect(self):
        self.connection.close()

    # receive_message is called whenever the MessageReceiver receives a message from the server.
    # The method will then represent the message in a visually pleasing way for the user.
    def receive_message(self, message):
        msg = json.loads(message)

        def print_message():
            # How do we handle name collisions?
            if msg["sender"] != self.username:
                print("%s -- %s" % (msg["sender"], msg["content"]))
        
        def print_history():
            for m in msg["content"]:
                print("%s -- %s" % (m["sender"], m["content"]))

        dictionary = {
            "info": lambda: print("[%s] - %s" % (msg["response"], msg["content"])),
            "error": lambda: print("[%s] - %s" % (msg["response"], msg["content"])),
            "names": lambda: print(msg["content"]),
            "message": print_message,
            "history": print_history,
            "logout": self.disconnect
        }
        return dictionary.get(msg["response"], lambda: print("Malformed message"))()

    def send_payload(self, data):
        self.connection.sendall(data)

    def dispatcher(self, data):
        message = {"request": "message", "content": data}
        
        if data.startswith("/login") and len(data.split()) == 2:
            self.username = data.split()[1]
            message["request"] = "login"
            message["content"] = self.username
        elif data == "/names":
            message["request"] = "names"
            message["content"] = ""
        elif data == "/logout":
            message["request"] = "logout"
            message["content"] = ""
        elif data == "/help":
            message["request"] = "help"
            message["content"] = ""
        
        self.send_payload(json.dumps(message))


if __name__ == "__main__":
    client = Client("localhost", 9998)
