# Tracker Socket 
# Tracker is in charge of keeping the directory up to date and then sending this directory out to requesting leechers.
# are we going to use a timing feature to eliminate those not available or how do we keep it up to date 
# UDP

import sys
import os
import threading
from socket import AF_INET, SOCK_DGRAM, socket
from time import *
from datetime import *
#from .MsgFormatter import MessageFormatter

# Add the directory containing MessageFormatter.py to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'path_to_directory_containing_MessageFormatter')))

try:
    from MsgFormatter import MessageFormatter
except ImportError:
    print("MessageFormatter module could not be imported. Please ensure it is installed and available.")

class Tracker:
    
    msgF = MessageFormatter()

    def __init__(self):
        self.seeders = []      # available will be a list of elements that are made up of clientAddress, fileName, fileSize ie. ((clientAdd, fileName, fileSize, timeStamp),...)
        self.port = 3535
        self.serverSocket = None

    # method to create and keep the socket open and call formulateResponse   
    def trackerUDPServer(self):
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverSocket.bind(('127.0.0.1', self.port))
        print("The server is ready to receive")
        while True:
            message, addr = self.serverSocket.recvfrom(2048)
            print("[MESSAGE]", message)
            msgID, bodyLength = self.msgF.pullApart(message[:5])
            self.formulateResponse(message[5:], addr, msgID, )
            
    # method will respond to the client based on what they are requesting. 
    def formulateResponse(self, message, clientAdd, msgID):
        response = ""
        if msgID == 0x06 :  # 0x06 - request message for available seeders
            avail = []
            fileName = message.decode() # the message here will be the fileName of the file the leecher is requesting available seeders for
            fileSize = 0
            print(self.seeders)
            for a in self.seeders:
                print(a)
                if a[1] == fileName:
                    avail.append(a[0])
                    fileSize = a[2]

            if len(avail) == 0:
                responseID = 0x10  # this will be the custom message ID to show the data requested is unavailable
                print("No seeders available for the file.")
            else:
                responseID = 0x05  # this will be the message ID to show that the response has got the data requested attached
                response = str(fileSize) + ","+ str(avail)
        elif msgID == 0x01 :  # hello from the peer to show they are still active with the file or a new peer joining the directory.
            fileName, fileSize, timeStamp = message.decode().split(",") # the message here will be the fileName, fileSize, and timeStamp of the seeders file
            fileSize = int(fileSize)
            timeStamp = datetime.now()

            found = False
            for seeder in self.seeders:
                if seeder[0] == clientAdd and seeder[1] == fileName:
                    seeder[3] = timeStamp
                    found = True

            if not found:
                self.seeders.append([clientAdd, fileName, fileSize, timeStamp])
                responseID = 0x01
                response = str(clientAdd)


        print("Seeder is active with file.")
        message = self.msgF.putTogether(responseID, response)
        # response sending (if the request was for seeders available it will send the list of seeders. if it was a hello it will respond with nothing)
        print("about to send through tracker "+ str(responseID))
        self.serverSocket.sendto(message, clientAdd)


        # def updateDirectory():

        #     while True:
        #         current = datetime.now()
        #         prior = timedelta(seconds=15)
        #         fifteenPrior = current - prior
        #         updatedAvail = []
        #     # runs through all elements in a copy of the list to safely remove any outdated elements
        #         with availableLock: # makes sure the list of avilable seeders is accurately appended and read
        #             for a in self.available[:]:
        #         # checks if the timestamp on the list element is later than 15seconds before the current time and keeps those that are
        #                 if a[3] >= fifteenPrior:  
        #                     updatedAvail.append(a)

        # # Assign the updated list back to self.available
        #         self.available = updatedAvail

        #         time.sleep(15)