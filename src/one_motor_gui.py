import sys
from PyQt4 import QtCore, QtGui, uic
import serial
import stepper_control

PORT_NUM = 2
BAUD = 9600
REFRESH_INTERVAL = 2000
 
serial_connection = serial.Serial(PORT_NUM, BAUD, timeout=1)
form_class = uic.loadUiType("one_motor.ui")[0]                 # Load the UI
 
class MyWindowClass(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.btn_setaddr.clicked.connect(self.btn_setaddr_clicked)  # Bind the event handlers
        self.btn_jog_left.clicked.connect(self.btn_jog_left_clicked)  # Bind the event handlers
        self.btn_jog_right.clicked.connect(self.btn_jog_right_clicked)  # Bind the event handlers
        self.btn_goto.clicked.connect(self.btn_goto_clicked)
        
        #self.timer = QtCore.QTimer()
        #QtCore.QObject.connect(self.timer, QtCore.SIGNAL('timeout()'), self.refresh_position)
        
        self.motor = None
        #self.btn_FtoC.clicked.connect(self.btn_FtoC_clicked)  #   to the buttons
 
    def btn_setaddr_clicked(self):
        addr = int(self.motor_num_text_inp.text())
        # TODO: allow selection of COM port number
        self.motor = stepper_control.Motor(serial_connection, addr)
        #self.timer.start(REFRESH_INTERVAL)
        print "initialized motor address"

    def btn_jog_left_clicked(self):
        jogSize = self.spin_jog_inp.value()
        if self.motor != None:
            self.motor.rel(-1 * jogSize)
            #self.spin_position_readout.setText(str(self.motor.query('query_position')))
        #TODO: error handling for the case where motor == None


    def btn_jog_right_clicked(self):
        jogSize = self.spin_jog_inp.value()
        if self.motor != None:
            self.motor.rel(jogSize)
            #self.spin_position_readout.setText(str(self.motor.query('query_position')))
        #TODO: error handling for the case where motor == None

    def btn_goto_clicked(self):
        if self.motor != None:
            position = self.spin_abs_position.value()
            self.motor.absolute(position)
            #self.spin_position_readout.setText(str(self.motor.query('query_position')))
            
    def refresh_position(self):
        try:
            self.spin_position_readout.setText(str(self.motor.query('query_position')))
        finally:
            QtCore.QTimer.singleShot(REFRESH_INTERVAL, self.refresh_position)


def cleanUp():
    serial_connection.close()
    print "closed serial connection"

#    def btn_CtoF_clicked(self):                  # CtoF button event handler
#        cel = float(self.editCel.text())         #
#        fahr = cel * 9 / 5.0 + 32                #
#        self.spinFahr.setValue(int(fahr + 0.5))  #
 
#    def btn_FtoC_clicked(self):                  # FtoC button event handler
#        fahr = self.spinFahr.value()             #
#        cel = (fahr - 32) *                      #
#        self.editCel.setText(str(cel))           #
 
app = QtGui.QApplication(sys.argv)
#app.aboutToQuit.connect(cleanUp)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()
cleanUp()
