# -*- coding: utf-8 -*-
__author__ = "Trond Humborstad"

import socket, json, datetime
from MessageReceiver import MessageReceiver

class Client:
    """
    This is the chat client class
    """

    def __init__(self, host, server_port):
        """
        This method is run when creating a new Client object
        """

        # Set up the socket connection to the server
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.server_port = server_port
        self.username = "default_username"
        self.run()
        

    def run(self):
        # Initiate the connection to the server
        self.connection.connect((self.host, self.server_port))
        thread = MessageReceiver(self, self.connection)
        thread.start()
        while True:
            input_string = str(raw_input(""))
            self.dispatcher(input_string)

    def disconnect(self):
        self.connection.close()

    def receive_message(self, message):
        message = json.loads(message)
        if message["response"] in ["info", "error"]:
            print "[%s] - %s" % (message["response"], message["content"])
        
        elif message["response"] == "message":
            if message["sender"] != self.username :
                print "%s -- %s" % (message["sender"], message["content"])
        
        elif message["response"] == "history":
            for msg in message["content"]:
                print "%s -- %s" % (msg["sender"], msg["content"])
        
        elif message["response"] == "names":
            print message["content"]

        elif message["response"] == "logout":
            self.disconnect()

    def send_payload(self, data):
        self.connection.sendall(data)

    def dispatcher(self, data):
        message = {"request":"message", "content":data}
        
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
    """
    This is the main method and is executed when you type "python Client.py"
    in your terminal.

    No alterations is necessary
    """
    client = Client("localhost", 9998)
