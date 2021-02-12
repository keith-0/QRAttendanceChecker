from PyQt5.QtWidgets import QWidget, QLCDNumber, QHBoxLayout, QApplication
from PyQt5.QtCore import QTimer
import sys
from time import strftime
class ClockWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.LCD = QLCDNumber()
        self.clockLayout = QHBoxLayout()
        self.timer = QTimer()
        self.initUI()
        self.setLayout(self.clockLayout)
        self.show()

    def initUI(self):

        self.timer.timeout.connect(self.refreshLCD)
        self.timer.start(1000)
        self.LCD.setDigitCount(8)
        self.LCD.display(strftime("%H:%M:%S"))
        self.clockLayout.addWidget(self.LCD)

        self.setMaximumSize(650, 100)

    def refreshLCD(self):
        self.LCD.display(strftime("%H:%M:%S"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClockWidget()
    sys.exit(app.exec_())

