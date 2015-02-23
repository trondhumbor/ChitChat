# -*- coding: utf-8 -*-
__author__ = "Trond Humborstad"

import SocketServer, json, time

class StateKeeper(object):
    def __init__(self):
        self.connectedClients = []
        self.chatlog = []

class ClientHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        """
        This method handles the connection between a client and the server.
        """
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request

        self.loggedin = False
        self.username = "Server"

        while True:
            received_string = self.connection.recv(4096)
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
        self.connection.sendall(json.dumps(response))

    def logout(self):
        response = {
            "timestamp": time.time(),
            "sender": self.username,
            "response": "info",
            "content": "You've been logged out"
        }
        self.connection.sendall(json.dumps(response))
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
            client.connection.sendall(json.dumps(response))
        self.server.statekeeper.chatlog.append(response)

    def names(self):
        response = {
            "timestamp": time.time(),
            "sender": self.username,
            "response": "names",
            "content": "Names: \r\n" + "\r\n".join([client.username for client in self.server.statekeeper.connectedClients])
        }
        self.connection.sendall(json.dumps(response))

    def help(self):
        response = {
            "timestamp": time.time(),
            "sender": self.username,
            "response": "info",
            "content": "No help available"
        }
        self.connection.sendall(json.dumps(response))

    def error(self, msg):
        response = {
            "timestamp": time.time(),
            "sender": self.username,
            "response": "error",
            "content": msg
        }
        self.connection.sendall(json.dumps(response))

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
