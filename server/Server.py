# -*- coding: utf-8 -*-
__author__ = "Trond Humborstad"

try:
    import SocketServer
except ImportError:
    import socketserver as SocketServer

import json, time

class StateKeeper(object):
    """
    This class keeps track of the state of the server.
    More specifically, which clients are connected and 
    a log over previously sent messages. Whenever a client
    connects/disconnects from the server or sends a message,
    the variables holding the state are updated.
    """
    def __init__(self):
        self.connectedClients = []
        self.chatlog = []

    def addClient(self, client):
        self.connectedClients.append(client)

    def removeClient(self, client):
        self.connectedClients.remove(client)

    def getClients(self):
        return self.connectedClients

    def getClientNames(self):
        return [client.username for client in self.connectedClients]

    def getMessageHistory(self):
        return self.chatlog

    def logMessage(self, msg):
        self.chatlog.append(msg)

class ClientHandler(SocketServer.BaseRequestHandler):
    
    """
    This class handles the connection between a client and the server.
    This class is instantiated once for each client.
    The handle()-function is run automatically when a client connects.
    """

    def handle(self):
        # By default, the client isn't logged in.
        self.loggedin = False
        self.username = None

        # Listen for incoming messages from the client.
        while True:
            received_string = self.request.recv(4096).decode("utf-8")
            self.dispatch(received_string)

    def login(self, message):
        if self.loggedin:
            return self.error("Already logged in.")

        if not message["content"] or not message["content"].isalnum():
            return self.error("Illegal username. Only alphanumeric chars are allowed.")

        if message["content"] in self.server.statekeeper.getClientNames():
            return self.error("Username is already taken.")

        self.username = message["content"]
        self.loggedin = True
        self.server.statekeeper.addClient(self)
        response = {
            "timestamp": str(int(time.time())),
            "sender": self.username,
            "response": "history",
            "content": self.server.statekeeper.getMessageHistory()
        }
        self.request.sendall(json.dumps(response).encode("utf-8"))

    def logout(self):
        if not self.loggedin:
            return self.error("You must be logged in to access this function")

        response = {
            "timestamp": str(int(time.time())),
            "sender": self.username,
            "response": "logout",
            "content": "You've been logged out"
        }
        self.request.sendall(json.dumps(response).encode("utf-8"))
        self.loggedin = False
        self.username = None
        self.server.statekeeper.removeClient(self)

    def msg(self, message):
        if not self.loggedin:
            return self.error("You must be logged in to access this function")

        response = {
            "timestamp": str(int(time.time())),
            "sender": self.username,
            "response": "message",
            "content": message["content"]
        }
        self.server.statekeeper.logMessage(response)
        for client in self.server.statekeeper.getClients():
            client.request.sendall(json.dumps(response).encode("utf-8"))

    def names(self):
        if not self.loggedin:
            return self.error("You must be logged in to access this function")

        response = {
            "timestamp": str(int(time.time())),
            "sender": self.username,
            "response": "names",
            "content": "Names: \r\n" + "\r\n".join(self.server.statekeeper.getClientNames())
        }
        self.request.sendall(json.dumps(response).encode("utf-8"))

    def help(self):
        response = {
            "timestamp": str(int(time.time())),
            "sender": self.username,
            "response": "info",
            "content": """
login <username> sends a request to login to the server. The content is a string with the username.
logout sends a request to log out and disconnect from the server. The content is None.
msg <message> sends a message to the server that should be broadcasted to all connected clients. The content is a string with the message.
names should send a request to list all the usernames currently connected to the server.
help sends a request to the server to receive this help text containing all requests supported by the server.
            """
        }
        self.request.sendall(json.dumps(response).encode("utf-8"))

    def error(self, msg):
        response = {
            "timestamp": str(int(time.time())),
            "sender": self.username,
            "response": "error",
            "content": msg
        }
        self.request.sendall(json.dumps(response).encode("utf-8"))

    # The dispatch-method is called whenever the server receives a message
    # from the client. The message *should* be JSON-formatted, and conform to the
    # protocol as outlined by the assignment-text.
    # Some actions are also reserved for logged-on users only.

    def dispatch(self, msg):
        try:
            message = json.loads(msg)
        except ValueError:
            return

        dictionary = {
            "login": lambda: self.login(message),
            "message": lambda: self.msg(message),
            "help": self.help,
            "logout": self.logout,
            "names": self.names
        }
        return dictionary.get(message["request"], lambda: self.error("Illegal request."))()


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    print("Server running...")

    # Set up and initiate the TCP server
    server = ThreadedTCPServer(("0.0.0.0", 9998), ClientHandler)
    server.statekeeper = StateKeeper()
    server.serve_forever()
