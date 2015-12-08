# -*- coding: utf-8 -*-
__author__ = "Trond Humborstad"

from threading import Thread

class MessageReceiver(Thread):
    """
    This is the message receiver class. The class inherits Thread, something that
    is necessary to make the MessageReceiver start a new thread, and permits
    the chat client to both send and receive messages at the same time
    """

    def __init__(self, client, connection):
        super(MessageReceiver, self).__init__()

        # Flag to run thread as a daemon
        self.daemon = True
        self.client = client
        self.connection = connection

    def run(self):
        while True:
            received_string = self.connection.recv(4096)
            self.client.receive_message(received_string)
