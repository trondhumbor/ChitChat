# -*- coding: utf-8 -*-
__author__ = "Trond Humborstad"

import SocketServer, json, time

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

class ClientHandler(SocketServer.BaseRequestHandler):
    
    """
    This class handles the connection between a client and the server.
    This class is instantiated once for each client.
    The handle()-function is run automatically when a client connects.
    """

    def handle(self):
        # By default, the client isn't logged in.
        self.loggedin = False
        self.username = "Server"

        # Listen for incoming messages from the client.
        while True:
            received_string = self.request.recv(4096)
            self.dispatch(received_string)

    def login(self, message):
        self.username = message["content"]
        self.loggedin = True
        self.server.statekeeper.connectedClients.append(self)
        response = {
            "timestamp": time.time(),
            "sender": self.username,
            "response": "history",
            "content": self.server.statekeeper.chatlog
        }
        self.request.sendall(json.dumps(response))

    def logout(self):
        response = {
            "timestamp": time.time(),
            "sender": self.username,
            "response": "info",
            "content": "You've been logged out"
        }
        self.request.sendall(json.dumps(response))
        self.loggedin = False
        self.username = "Server"
        self.server.statekeeper.connectedClients.remove(self)

    def msg(self, message):
        for client in self.server.statekeeper.connectedClients:
            response = {
                "timestamp": time.time(),
                "sender": self.username,
                "response": "message",
                "content": message["content"]
            }
            client.request.sendall(json.dumps(response))
        self.server.statekeeper.chatlog.append(response)

    def names(self):
        response = {
            "timestamp": time.time(),
            "sender": self.username,
            "response": "names",
            "content": "Names: \r\n" + "\r\n".join([client.username for client in self.server.statekeeper.connectedClients])
        }
        self.request.sendall(json.dumps(response))

    def help(self):
        response = {
            "timestamp": time.time(),
            "sender": self.username,
            "response": "info",
            "content": "No help currently available" # TODO: Add some useful message here
        }
        self.request.sendall(json.dumps(response))

    def error(self, msg):
        response = {
            "timestamp": time.time(),
            "sender": self.username,
            "response": "error",
            "content": msg
        }
        self.request.sendall(json.dumps(response))

    # The dispatch-method is called whenever the server receives a message
    # from the client. The message *should* be JSON-formatted, and conform to the
    # protocol as outlined by the assignment-text.
    # Some actions are also reserved for logged-on users only.

    def dispatch(self, msg):
        try:
            message = json.loads(msg)
        except ValueError as e:
            self.error("Malformed message")
            return

        if message["request"] == "login" and not self.loggedin:
            if message["content"].isalnum():
                self.login(message)
            else:
                self.error("Illegal username. Only alphanumeric chars are allowed.")
        
        elif message["request"] == "help":
            self.help()
        
        elif not self.loggedin:
            # After this, we know that the clients are logged in, and
            # they may then access the actions reserved for logged-in users.
            self.error("You must be logged in to access this function")

        elif message["request"] == "logout":
            self.logout()
        
        elif message["request"] == "message":
            self.msg(message)
        
        elif message["request"] == "names":
            self.names()
        
        else:
            self.error("Illegal request.")


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    HOST, PORT = "localhost", 9998
    print("Server running...")

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.statekeeper = StateKeeper()
    server.serve_forever()
