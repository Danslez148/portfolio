import datetime
import tkinter as t
from tkinter import ttk
from LeecherClass import Leecher
from TrackerClass import Tracker
from threading import Thread
from SeederClass import Seeder
import threading

class TorrentUI:
    #creating all the parts of a simple UI
    def __init__(self, root):
        self.root = root
        self.root.title("Torrent Client")
        self.root.geometry("600x400")
        
        self.label = t.Label(root, text="Torrent Downloader", font=("Arial", 20, "bold"))
        self.label.pack(pady=20)
        
        self.progressLabel = t.Label(root, text="File name: ", font=("Arial", 12))
        self.progressLabel.pack(pady=5)        
        
        self.fileEntry = t.Entry(root, width=50, font=("Arial", 14))
        self.fileEntry.pack(pady=10)
        
        self.downloadButton = t.Button(root, text="Check/Download", font=("Arial", 14), command=self.startDownload)
        self.downloadButton.pack(pady=10)
        
        self.progressBar = ttk.Progressbar(root, length=400, mode='determinate')
        self.progressBar.pack(pady=10)
        


        
    #gets the file name and starts the download    
    def startDownload(self):
        fileName = self.fileEntry.get()
        if fileName:
            leecher = Leecher()
            leecher_thread = threading.Thread(target=leecher.leecherUDPServer, args=(fileName,))
            leecher_thread.start()
            leecher.leecherUDPServer(fileName)

            print(f"Downloading {fileName}")
            self.progressBar["value"] = 0
            self.progressBar["maximum"] = 0
            #fileName = "test.txt"
            # thread = Thread(target=self.downloadFile(fileName), args=(fileName,))
            # thread.start()
    
    #downloads the file

      
    #code to update the progress bar based on how many chunks have downloaded    
    def updateProgress(self, chunkCount, totalChunks):
        progress = (chunkCount+1)*100/totalChunks
        self.progressBar["value"] = progress
        self.root.update_idletasks()
    
    #error message framework    
    def showError(self, message):
        errorWindow = t.Toplevel(self.root)
        errorWindow.title("Error")
        t.Label(errorWindow, text=message, font=("Arial", 14)).pack(pady=20)
        t.Button(errorWindow, text="OK", font=("Arial", 12), command=errorWindow.destroy).pack()
            
if __name__ == "__main__":

    tracker = Tracker()
    tracker = threading.Thread(target=tracker.trackerUDPServer)
    tracker.start()

    seeder = Seeder(0, 'test.txt')
    seeder = Seeder(0, "test.txt")



 
    root = t.Tk()
    app = TorrentUI(root)
    root.mainloop()  



    while True:
        pass