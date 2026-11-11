# Leecher class
# Request list of available seeders from the tracker. Requests file chunks from available seeders by establishing TCP connection to them.
# TCP

from socket import AF_INET, SOCK_DGRAM, socket
import math
import concurrent.futures
import threading
from SeederClass import *
from MsgFormatter import MessageFormatter
import ast

class Leecher:
     
    msgF = MessageFormatter()
    localPort = ""

    def __init__(self, updateProgress = None):
        self.updateProgress = updateProgress #this code is to keep track of how many chunks are downloaded in order to update the progress bar accordingly
        self.chunksDownloaded = 0
        self.lock = threading.Lock()
        self.fileName = ""
        

    def leecherUDPServer(self, fileName):
        udpSocket = socket(AF_INET, SOCK_DGRAM)
        udpSocket.bind(('127.0.0.1', 0))  # Bind to available port
        
        self.fileName = fileName
        
        try:
            # Send request to tracker
            message = self.msgF.putTogether(0x06, fileName)
            udpSocket.sendto(message, ('127.0.0.1', 3535))
            print(f"Request for {fileName} sent to tracker")
            
            # Wait for response
            print("Waiting")
            message, addr = udpSocket.recvfrom(1024)
            print(f"[RECEIVED] {message}")
            
            # Process response
            msgID, bodyLength = self.msgF.pullApart(message[:5])
            print("MSGGGGGG   " + str(msgID))
            if msgID == 0x05:
                body = message[5:].decode()
                strFileSize, availableSeeders = body.split(",", 1)
                fileSize = int(strFileSize)
                print(f"File size: {fileSize}, Available seeders: {availableSeeders}")
                
                # Start downloading file chunks
                self.parallelTCPRequest(fileSize, availableSeeders, self.fileName)
                return True
            else:
                print(f"No seeders found with the file: {self.fileName}")
                return False
                

        finally:
            udpSocket.close()
    
    #connnects to a seeder via TCP, then requests a file chunk and receives the requested data
    def leecherTCPClient(self, serverAddress, message):
        print(serverAddress)
        try:
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.connect(serverAddress)
            clientSocket.send(message)

            header = clientSocket.recv(5)
            msgID, bodyLength = self.msgF.pullApart(header)
            fileChunk = clientSocket.recv(bodyLength)
            localIP, self.localPort = clientSocket.getsockname()
            return fileChunk
        except Exception as e:
            print(f"An error occurred in leecherTCPClient: {e}")
    
    # fetching the chunk that also keeps track of how many chunks downloaded and updates the progresss bar        
    def fetchChunk(self, seederAddress, message, totalChunks):
        fileChunk = self.leecherTCPClient(seederAddress, message)
        
        #with self.lock:
       #     self.chunksDownloaded += 1
      #      self.updateProgress(self.chunksDownloaded, totalChunks)
            
        return fileChunk


    def parallelTCPRequest(self,fileSize, availableSeeders, fileName):
        # available seeders is a list of the seeders and numSeeders the number of seeders available
        availableSeeders = ast.literal_eval(availableSeeders)
        
        numSeeders = len(availableSeeders)
        chunkSize = math.ceil(fileSize/numSeeders)  # fileSize will be stored and worked with as bytes
        # chunkCount will be used to control the parallel requests
        chunkCount = 0
        threads = []
        resultsDict = {}

        for i in range(numSeeders):
            begin = chunkCount*chunkSize
            end = min((begin + chunkSize - 1), fileSize)
            chunkCount = chunkCount + 1
            
            message = fileName + "," + str(begin) + "," + str(end)
            formattedMessage = self.msgF.putTogether(0x07, message)
            
            print("here look" + str(availableSeeders[i]))

            def download_chunk(seederAddr, msg, chunkIndex, resultsDict):
                chunkData = self.fetchChunk(seederAddr, msg, numSeeders)
                if chunkData:
                    with self.lock:
                        resultsDict[chunkIndex] = chunkData
                        print("CHUNK INDEX"+ str(chunkIndex))

            thread = threading.Thread(
                target=download_chunk,
                args=(availableSeeders[i], formattedMessage, i, resultsDict)
            )
            threads.append(thread)
            thread.start()
        
        # Waits for all threads to complete
        for thread in threads:
            thread.join()
            
        # chunks are then reordered
        orderedChunks = [resultsDict[i] for i in sorted(resultsDict.keys()) if i in resultsDict]
        
        # code to download file to device
        with open("output/"+fileName, "wb") as f:
            for dataChunk in orderedChunks:
                f.write(dataChunk)
        print("Download complete")
        
        # s = Seeder(self.localPort, fileName)
        # thread = threading.Thread(target=s.seederTCPServer)
        # thread.start()
        # thread2 = threading.Thread(target=s.updateUDPDirectory)
        # thread2.start()


        
        


            


