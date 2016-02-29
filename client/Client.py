# -*- coding: utf-8 -*-

from __future__ import print_function
from builtins import input

__author__ = "Trond Humborstad"

import socket, json, datetime, os
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

    def __init__(self, host, port):
        # Set up the socket connection to the server
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_host = host
        self.server_port = port
        self.username = None
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
            input_string = str(input(""))
            self.dispatcher(input_string)

    def disconnect(self):
        #self.connection.shutdown(socket.SHUT_RDWR)
        self.connection.close()
        os._exit(0)

    # receive_message is called whenever the MessageReceiver receives a message from the server.
    # The method will then represent the message in a visually pleasing way for the user.
    def receive_message(self, message):
        try:
            message = json.loads(message)
        except ValueError:
            return print("Malformed message. Not valid JSON.")

        def print_message():
            # How do we handle name collisions?
            if message["sender"] != self.username:
                print("%s -- %s" % (message["sender"], message["content"]))
        
        def print_history():
            for m in message["content"]:
                print("%s -- %s" % (m["sender"], m["content"]))

        dictionary = {
            "info": lambda: print("[%s] - %s" % (message["response"], message["content"])),
            "error": lambda: print("[%s] - %s" % (message["response"], message["content"])),
            "names": lambda: print(message["content"]),
            "message": print_message,
            "history": print_history,
            "logout": self.disconnect
        }
        return dictionary.get(message["response"], lambda: print("Unsupported method"))()

    def dispatcher(self, data):
        message = {}

        if data.startswith("login") and len(data.split()) == 2:
            self.username = data.split()[1]
            message["request"] = "login"
            message["content"] = self.username
        
        elif data.startswith("msg"):
            message["request"] = "message"
            message["content"] = data[len("msg "):]
        
        elif data == "names":
            message["request"] = "names"
            message["content"] = ""
        
        elif data == "logout":
            message["request"] = "logout"
            message["content"] = ""
        
        elif data == "help":
            message["request"] = "help"
            message["content"] = ""
        
        else:
            return
        
        self.connection.sendall(json.dumps(message).encode("utf-8"))


if __name__ == "__main__":
    client = Client("localhost", 9998)
