# -*- coding: utf-8 -*-
__author__ = "Trond Humborstad"

import socket, json, datetime
from MessageReceiver import MessageReceiver

class Client:
    """
    This is the chat client class.
    """

    def __init__(self, host, server_port):
        """
        This method is run when creating a new Client object.
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

    # The dispatch method makes sure the message conforms with
    # the protocol as outlined by the assignment.
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
    client = Client("localhost", 9998)
