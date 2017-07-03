import sys
from PyQt4 import QtGui, QtCore, uic
from twisted.internet.defer import inlineCallbacks
import twisted
import numpy as np
import pyqtgraph as pg

path = sys.path[0]
sys.path.append(path+'\Resources')
sys.path.append(path+'\ScanControl')
sys.path.append(path+'\LabRADConnect')
sys.path.append(path+r'\nSOTCharacterizer')    
sys.path.append(path+'\DataVaultBrowser')
sys.path.append(path+'\Plotter')

UI_path = path + r"\MainWindow.ui"
MainWindowUI, QtBaseClass = uic.loadUiType(UI_path)

#import all windows for gui
import ScanControl
import LabRADConnect
import nSOTCharacterizer
import plotter

import exceptions

#import labrad.errors

class MainWindow(QtGui.QMainWindow, MainWindowUI):
            
    """ The following section initializes, or defines the initialization of the GUI and 
    connecting to servers."""
    def __init__(self, reactor, parent=None):
        """ nSOT Scanner GUI """
        
        super(MainWindow, self).__init__(parent)
        self.reactor = reactor
        self.setupUi(self)
        self.setupAdditionalUi()
        
        #Move to default position
        self.moveDefault()
        
        #Intialize all widgets. 
        self.SC = ScanControl.Window(self.reactor, self)
        self.LabRAD = LabRADConnect.Window(self.reactor, self)
        self.nSOTChar = nSOTCharacterizer.Window(self.reactor,self)
        self.Plot = plotter.Plotter(self.reactor,self)
        
        #Connects all drop down menu button
        self.actionScan_Control.triggered.connect(self.openScanControlWindow)
        self.actionLabRAD_Connect.triggered.connect(self.openLabRADConnectWindow)
        self.actionnSOT_Characterizer.triggered.connect(self.opennSOTCharWindow)
        self.actionData_Plotter.triggered.connect(self.openDataPlotter)
        
        #Connectors all layout buttons
        self.push_Layout1.clicked.connect(self.setLayout1)
        
        self.push_Logo.clicked.connect(self.toggleLogo)
        self.isRedEyes = False
        
        #Connect 
        self.LabRAD.cxnSuccessful.connect(self.distributeLabRADConnections)
        self.LabRAD.cxnDisconnected.connect(self.disconnectLabRADConnections)
        
    def setupAdditionalUi(self):
        """Some UI elements would not set properly from Qt Designer. These initializations are done here."""
        self.push_Layout1.setToolTip('Loads and repositions Scan Control and' +
        'Main Window. Closes the rest.')
        
    #----------------------------------------------------------------------------------------------#
            
    """ The following section connects actions related to default opening windows."""
    
    def moveDefault(self):
        self.move(10,10)
        
    def distributeLabRADConnections(self,dict):
        self.Plot.connectLabRAD(dict)
        self.nSOTChar.connectLabRAD(dict)
        
    def disconnectLabRADConnections(self,dict):
        self.Plot.disconnectLabRAD()
        self.nSOTChar.disconnectLabRAD()
    
    def openScanControlWindow(self):
        self.SC.moveDefault()
        if self.SC.isVisible() == False:
            self.SC.show()
            
    def openLabRADConnectWindow(self):
        self.LabRAD.moveDefault()
        if self.LabRAD.isVisible() == False:
            self.LabRAD.show()
            
    def opennSOTCharWindow(self):
        self.nSOTChar.moveDefault()
        if self.nSOTChar.isVisible() == False:
            self.nSOTChar.show()
            
    def openDataPlotter(self):
        self.Plot.moveDefault()
        if self.Plot.isVisible() == False:
            self.Plot.show()
    
    #----------------------------------------------------------------------------------------------#
            
    """ The following section connects actions related to setting the default layouts."""
        
    def setLayout1(self):
        self.moveDefault()
        self.hideAllWindows()
        self.openScanControlWindow()
        self.openLabRADConnectWindow()
        
    def toggleLogo(self):
        if self.isRedEyes == False:
            self.push_Logo.setStyleSheet("#push_Logo{"+
            "image:url(:/nSOTScanner/Pictures/SQUIDRotated.png);background: black;}")
            self.isRedEyes = True
        else:
            self.push_Logo.setStyleSheet("#push_Logo{"+
            "image:url(:/nSOTScanner/Pictures/SQUIDRotated2.png);background: black;}")
            self.isRedEyes = False
            
    def hideAllWindows(self):
        self.SC.hide()
        self.LabRAD.hide()
        self.nSOTChar.hide()
        self.Plot.hide()
            
    def closeEvent(self, e):
        self.SC.close()
        self.nSOTChar.close()
        self.Plot.close()
        self.LabRAD.disconnectLabRAD()
        self.LabRAD.close()
        self.reactor.stop()
        print 'Reactor shut down.'
        
#----------------------------------------------------------------------------------------------#
            
""" The following runs the GUI"""

if __name__=="__main__":
    app = QtGui.QApplication([])
    from qtreactor import pyqt4reactor
    pyqt4reactor.install()
    from twisted.internet import reactor
    window = MainWindow(reactor)
    window.show()
    reactor.run()
