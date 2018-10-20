# Runs a socket server to send commands to the bot

import socketserver
import datetime

import sys
sys.path.append('../library')

from bot import Bot

host = "localhost"
port = 9999
debug = True

server_bot = Bot()

# connect to the physical bot, comment out if only want simulation
server_bot.startSerialPort() 
server_bot.init()

# uncomment next line if want to simulate the bot moving
server_bot.openBotSimulation("Bot Server Simulation");

class MyTCPSocketHandler(socketserver.BaseRequestHandler):
    # The RequestHandler class for our server.
    # It is instantiated once per connection to the server and 
    # overrides the handle() method to communicate with the client.

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        bstring = self.data
        command = bstring.decode("utf-8")
        if debug:
           print("{} wrote:".format(self.client_address[0]), command)

        start_time = datetime.datetime.now()

        res = server_bot.processServerCommand(command)

        end_time = datetime.datetime.now();
        time_spent = end_time - start_time
        elapsed_seconds = time_spent.total_seconds()
        print("COMMAND",command,"TIME:",elapsed_seconds)
        
	# send result
        #self.request.sendall(bytes(res + "\n", 'utf8'))
        

if __name__ == "__main__":

    # instantiate the server, and bind to host on port
    server = socketserver.TCPServer((host, port), MyTCPSocketHandler)

    print("Bot Server started on",host,":",port)

    # activate the server
    # this will keep running until Ctrl-C
    server.serve_forever()
