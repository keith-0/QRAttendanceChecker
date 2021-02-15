from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QVBoxLayout, QWidget, QDialog, QInputDialog, QLineEdit
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QObject
from webcamUI import *
import sys, logging

#MainWindow is the first QWidget called by MainController
#MainWindow initializes the program by getting the video capture source
#index and eventname

class MainWindow(QWidget):
    #triggered when name dialogbox is submitted
    #contains video capture device index and event name
	eventSignal = pyqtSignal(str, str) 
	
	def __init__(self):
		super().__init__()
		self.title = "QR Scanner"
		self.winX = 500
		self.winY = 300
		self.winW = 200
		self.winH = 150
		self.setWindowTitle(self.title)
		self.setGeometry(self.winX, self.winY, self.winW, self.winH)
		self.dropdown = QComboBox()
		self.dropdown.setGeometry(75, 0, 50, 20)
		self.eventNameInp = QLineEdit()
		self. mainWindowLayout = QVBoxLayout()
		self.button1 = QPushButton("Open New Event")
		self.button1.setFixedSize(200, 25)
		#Connects/returns mainWindow to mainController
		#mainController calls EventAttendanceCheck here
		self.button1.clicked.connect(self.emitEventInitiate)
		logging.info("Populating setup dialogbox\n")
		self.populate()


    # gathers all available video capture devices in pc
    # they are returned as index numbers starting at
    # 0 for default laptop webcam and 1, 2, 3 ... fr auxillary cameras
    # TODO: find method to retrieve hardware descriptions for cameras
    # TODO: catch if there is no available video capture device
	def getVideoSources(self):
		arr = []
		# loops through valid video capture sources
		# appends index to arr if valid
		for x in range(-1, 5):
			print(x)
			cap = cv2.VideoCapture(x)
			if cap is None or not cap.isOpened():
				continue
			else:
				arr.append(str(x))
			cap.release()
		return arr

	# emitted when button1 is clicked; connects to mainController.EventAttendanceCheck()
	def emitEventInitiate(self):
		self.eventSignal.emit(self.eventNameInp.text(), self.dropdown.currentText())
	
	def populate(self):

		logging.info("Scanning for list of video capture devices\n")
		src = self.getVideoSources()
		self.dropdown.addItems(src)
		
		logging.info("Adding widgets to mainwindow\n")
		self.mainWindowLayout.addWidget(self.dropdown)
		self.mainWindowLayout.addWidget(self.eventNameInp)
		self.mainWindowLayout.addWidget(self.button1)
		self.setLayout(self.mainWindowLayout)
		logging.info("Launching MainWindow\n")


if __name__ == "__main__":
#
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
