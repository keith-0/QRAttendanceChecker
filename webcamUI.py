from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QTextEdit, QComboBox, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPixmap, QImage, QFont, QTextCursor
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QSize
from ClockWidget import ClockWidget
from PIL import Image
import numpy
import cv2
import sys
import datetime
import time
from os import path
from os import mkdir
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol

VIDEO_SOURCE = 2
CAM_CAP_WIDTH = 480
CAP_CAM_HEIGHT = 640


class WebCamWindow(QWidget):
	#Triggered when enter is pressed with entry on inputbox (i.e. manual input)
    enterKeypress = pyqtSignal(str, int)
    #TODO: Allow changing video source mid-stream
    #Currently unused
    #sourceChangeSignal = pyqtSignal(int)
    
	#Signal called by addLog()
    QRDetectedSignal = pyqtSignal(str, int)
    
    def __init__(self, instanceName, videoSource):
        super().__init__()
        self.enterKeypress.connect(self.addLog)
    # video source selected in mainWindow
        self.videoSource = videoSource
        self.setWindowTitle(instanceName)
    # declare mainQWidget for WebCamWindow
        self.mainWidget = QWidget()
        print("mainWidget Initialized")
        self.mainWidgetLayout = QHBoxLayout()
    # initialize clock widget
        self.timeWidget = ClockWidget()
    # configure stream output widget
        self.webCamScreen = WebcamWidget(videoSource, instanceName)
        self.webCamScreen.decodedDataSignal.connect(self.addLog)
        self.webCamScreen.show()
    # configure left half of main widget (clock and webcamstream)
        self.streamInterface = QWidget()
        self.confStreamInterface()
    # configure log box
        # configure right half of main widget (Log window)
        self.dataInput = QLineEdit()
        self.dataInputButton = QPushButton()
        self.logInterface = QWidget()
        self.dataInputLayout = QHBoxLayout()
        self.confLogWindow()
    # configure mainWidgetLayout for webCamWindow
        self.mainWidgetLayout.addWidget(self.streamInterface)
        self.mainWidgetLayout.addWidget(self.logInterface)
        self.logInterface.resize(QSize(150, 500))
        self.setLayout(self.mainWidgetLayout)
        self.show()

    def confLogWindow(self):
        self.logWindow = QTextEdit()
        self.logWindow.resize(50,500)
        self.logWindow.setReadOnly(True)

        font = QFont()
        font.setPointSize(30)
        self.dataInput.setFont(font)
        font.setPointSize(15)
        self.logWindow.setFont(font)
        
        self.dataInputButton.setFixedSize(50,50)
        self.dataInputButton.clicked.connect(self.inputButtonClicked)
        logWindowLabel = QLabel()
        logWindowLabel.setText("Log")
        logWindowLabel.setFixedHeight(25)
        self.dataInputLayout.addWidget(self.dataInput)
        self.dataInputLayout.addWidget(self.dataInputButton)
        logWindowLayout = QVBoxLayout()
        logWindowLayout.addLayout(self.dataInputLayout)
        logWindowLayout.addWidget(logWindowLabel)
        logWindowLayout.addWidget(self.logWindow)

        self.logInterface.setLayout(logWindowLayout)
    
    def inputButtonClicked(self):
        self.dataInput.selectAll()
        self.enterKeypress.emit(self.dataInput.text(), 1) #connects to addLog()
        self.dataInput.selectAll()
        self.dataInput.setFocus()
    #When user manually enters id num to inputfield, 
    #Allows use of enter key to confirm input
    def keyPressEvent(self, keypress):
        if keypress.key() == QtCore.Qt.Key_Return:
            self.enterKeypress.emit(self.dataInput.text(), 1) #connects to addLog()
            self.dataInput.selectAll()
            self.dataInput.setFocus()

	#Connected do enterKeypress and decodedDataSignal
    def addLog(self, data, mode):
        self.QRDetectedSignal.emit(data, mode) # sends pysignal to mainController
        self.logWindow.moveCursor(QtGui.QTextCursor.Start)
        self.logWindow.insertHtml(time.strftime("[%H:%M:%S]\t")+data + "<br>")
        self.logWindow.ensureCursorVisible()
    # left part of webCamWindow
    def confStreamInterface(self):
        confStreamInterface = QVBoxLayout()
        confStreamInterface.addWidget(self.timeWidget)
        confStreamInterface.addWidget(self.webCamScreen)
        self.streamInterface.setLayout(confStreamInterface)
        self.streamInterface.setFixedSize(QSize(600,500))
        self.streamInterface.setGeometry(0, 0, 250, 500)



class RefreshFrameThread(QThread):

    # emits image for webcamwindow.label
    # emits data for detected QR
    changePixmap = pyqtSignal(QImage)
    detectedCode = pyqtSignal(str, int)

    def __init__(self, source, fileName):
        super(RefreshFrameThread, self).__init__()
        self.s=int(source)
        self.filename = fileName
    def run(self):
        # TODO: pass argument for csv file
        self.cap = cv2.VideoCapture(self.s)
        print("set source to "+str(self.s))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_CAP_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAP_CAM_HEIGHT)

        found = set()

        # todo: pass argument for video source
        if self.cap.isOpened():
            while True:
                ret, frame = self.cap.read()
            # decoder keeps detecting PDF417 barcode
            # restrict to reading QR
                barcodes = pyzbar.decode(frame, symbols=[ZBarSymbol.QRCODE])
            # draw bounding box
                for barcode in barcodes:

                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    # convert decoded data into string from bytes
                    barcodeData = barcode.data.decode("utf-8")
                    barcodeType = barcode.type

                    # draw the barcode data and barcode type on the image
                    text = "{} ({})".format(barcodeData, barcodeType)

                    cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    if barcodeData not in found:
                        found.add(barcodeData)
                        self.detectedCode.emit(barcodeData, 0)

                if ret:
                    # https://stackoverflow.com/a/55468544/6622587
                    # convert cv2 img so compatible with QImage
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QtGui.QImage(rgbImage.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)

class WebcamWidget(QWidget):

    decodedDataSignal = pyqtSignal(str, int)
    def __init__(self, source, csv):
        super().__init__()
        # self.title = "Webcam UI"
        # self.width = 800
        # self.height = 1000
        # self.top = 100
        # self.left = 100

        self.src=source
        self.csv = csv
        self.initUI()
    @pyqtSlot(QImage)
    def startThread(self, source):
        self.th = RefreshFrameThread(source, self.csv)
        self.th.changePixmap.connect(self.refreshImage)
        self.th.detectedCode.connect(self.emitToMain)
        self.th.start()


    #def reqSourceChange(self, int):
    # signal functions
    def refreshImage(self, image):
        self.webcamDisplay.setPixmap(QPixmap.fromImage(image))

    def emitToMain(self, data, mode):
        self.decodedDataSignal.emit(data, mode)

    def initUI(self):

        self.resize(700, 500)
        # create a QPixmap label
        self.webcamDisplay = QLabel(self)
        self.webcamDisplay.move(0, 0)
        self.webcamDisplay.resize(640, 480)
        self.startThread(self.src)

    def reStartThread(self, source):
        self.th.quit()
        self.th.wait(500)
        self.th = RefreshFrameThread(source)
        self.th.changePixmap.connect(self.refreshImage)
        self.th.detectedCode.connect(self.emitToMain)
        self.th.start()

if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = WebCamWindow("Hello")
    window.show()
    sys.exit(app.exec_())
