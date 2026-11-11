# Seeder class
# Hosts of the files and divides and sends the files to requesting leechers. They notify the tracker of their presence. 
# TCP

from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM, socket 
from datetime import *
import time
from MsgFormatter import MessageFormatter
import threading
import ast

class Seeder:
    msgF = MessageFormatter()
    def __init__(self, port, fileName):
        self.port = port
        self.fileName = fileName
        self.SeederUDPClient('test.txt', 5)
        thread = threading.Thread(target=self.seederTCPServer)
        thread.start()
        

    # method to create and open the TCP socket and 'listens' for requests from leechers and responds with file chunks
    def seederTCPServer(self):

        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.bind(('127.0.0.1', self.port))
        serverSocket.listen(1)

        while True:

            connectionSocket, addr = serverSocket.accept()
            header = connectionSocket.recv(5)
            msgID, bodyLength = self.msgF.pullApart(header)
            message = connectionSocket.recv(bodyLength)
            message = message.decode()
            fileName, begin, end = message.split(",")
            print(f"Received request for {fileName} from {addr}")
            begin = int(begin)
            end = int(end)

            
            # respond with the asked for file chunk 
            fileChunk = self.getFileChunk(fileName, begin, end)
            fileChunk = fileChunk.decode()
            message = self.msgF.putTogether(0x05, fileChunk)
            connectionSocket.send(message)
        
    def getFileChunk(self, fileName, begin, end):
        with open(fileName, 'rb') as file:
                file.seek(begin)
                numBytes = end - begin + 1
                extractedBytes = file.read(numBytes)
        return extractedBytes        
        # retrieve the chunk required and send back to be encoded and sent to client
    
    # method to update the tracker with the files the seeder has available by calling the SeederUDPClient method every 15 seconds
    # def updateUDPDirectory(self):
    #     while True:
    #         self.SeederUDPClient()
    #         time.sleep(15)
    
    # method to send a message to the tracker with the files the seeder has available 
    def SeederUDPClient(self, fileName, fileSize):
        timeStamp = datetime.now()
        body = fileName + ","+str(fileSize) +","+ str(timeStamp)
        message = self.msgF.putTogether(0x01,body)
        try:
            udpSocket = socket(AF_INET, SOCK_DGRAM)
            udpSocket.sendto(message, ('127.0.0.1', 3535))
            message, clientAdd = udpSocket.recvfrom(1024)
            address = message[5:].decode()
            address = ast.literal_eval(address)
            self.port = address[1]

            print(f"[RECEIVED SEEDER] {str(self.port)}")

        except Exception as e:
            print(f"An error occurred in leecherUDPClient: {e}")
    


