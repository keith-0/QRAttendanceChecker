from mainWindow import *
from webcamUI import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal
import sys, logging
import csv
from datetime import datetime
from playsound import playsound
class Controller:
    def __init__(self):
        pass
	#Adding comment for cloned repo
	
    def showMainWindow(self):
		
        self.mainWin = MainWindow()
        self.mainWin.show()
        #triggers when "Open New Event" button from mainWindow is clicked
        #passes eventname and video capture source index
        self.mainWin.eventSignal.connect(self.EventAttendanceCheck)
		
    def EventAttendanceCheck(self, csvName, vidSource):
		#creates folder for records and .csv file to store records
        if not path.isdir("./records"):
            mkdir("./records")
        self.full_dir = "./records/" + csvName + ".csv"
        
        logging.info(self.full_dir)
 
        self.mainWin.close()
        
        #WebCamWindow defined in webcamUI.py
        self.checkerUI = WebCamWindow(csvName, vidSource)
        #called from webcamWindow.addLog()
        #triggered by decodedDataSignal and enterKeypress signals
        self.checkerUI.QRDetectedSignal.connect(self.WriteToFile)

    def WriteToFile(self, data, mode):

        with open(self.full_dir, "a", newline='\n') as f:
            fieldnames = ["timestamp", "idNumber", "mode"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if mode == 0:
                writer.writerow({"timestamp": datetime.now().time(), "idNumber": data, "mode":"0"})
            if mode == 1:
                writer.writerow({"timestamp": datetime.now().time(), "idNumber": data, "mode": "1"})
        playsound("./assets/beep-08b.wav", block=False) #beep
        
def main():
    print("enter main")
    appl = QApplication(sys.argv)
    controller = Controller()cd 
    print("assigned aontroller")
    controller.showMainWindow()
    print("Main exited")
    sys.exit(appl.exec_())


main()
