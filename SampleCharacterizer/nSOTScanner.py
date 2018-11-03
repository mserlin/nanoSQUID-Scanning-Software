import sys
from PyQt4 import QtGui, QtCore, uic
import time 

path = sys.path[0]
sys.path.append(path+'\Resources')
sys.path.append(path+'\ScanControl')
sys.path.append(path+'\LabRADConnect')
sys.path.append(path+r'\nSOTCharacterizer')    
sys.path.append(path+'\DataVaultBrowser')
sys.path.append(path+'\Plotter')
sys.path.append(path+'\TFCharacterizer')
sys.path.append(path+'\ApproachModule')
sys.path.append(path+'\ApproachMonitor')
sys.path.append(path+'\JPEPositionControl')
sys.path.append(path+'\PositionCalibration')
sys.path.append(path+'\Field Control')
sys.path.append(path+'\ScriptingModule')
sys.path.append(path+'\TemperatureControl')
sys.path.append(path+'\DeviceCharacterizer')


UI_path = path + r"\MainWindow.ui"
MainWindowUI, QtBaseClass = uic.loadUiType(UI_path)

#import all windows for gui
import ScanControl
import LabRADConnect
import nSOTCharacterizer
import plotter
import TFCharacterizer
import Approach
import ApproachMonitor
import JPEControl
import PositionCalibration
import FieldControl
import Scripting
import TemperatureControl
import DeviceCharacterizer


import exceptions

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
        self.ScanControl = ScanControl.Window(self.reactor, None)
        self.LabRAD = LabRADConnect.Window(self.reactor, None)
        self.nSOTChar = nSOTCharacterizer.Window(self.reactor, None)
        self.Plot = plotter.Plotter(self.reactor, None)
        self.TFChar = TFCharacterizer.Window(self.reactor, None)
        self.Approach = Approach.Window(self.reactor, None)
        self.ApproachMonitor = ApproachMonitor.Window(self.reactor, None)
        self.JPEControl = JPEControl.Window(self.reactor, None)
        self.PosCalibration = PositionCalibration.Window(self.reactor, None)
        self.FieldControl = FieldControl.Window(self.reactor, None)
        self.TempControl = TemperatureControl.Window(self.reactor,None)
        self.DeviceCharacterizer = DeviceCharacterizer.Window(self.reactor,None)

        
        #This module should always be initialized last, and have the modules
        #That are desired to be scriptable be input
        self.Scripting = Scripting.Window(self.reactor, None, self.ScanControl, self.Approach, 
                                          self.JPEControl, self.nSOTChar, self.FieldControl, self.TempControl)
        
        #Connects all drop down menu button
        self.actionScan_Control.triggered.connect(self.openScanControlWindow)
        self.actionLabRAD_Connect.triggered.connect(self.openLabRADConnectWindow)
        self.actionnSOT_Characterizer.triggered.connect(self.opennSOTCharWindow)
        self.actionData_Plotter.triggered.connect(self.openDataPlotter)
        self.actionTF_Characterizer.triggered.connect(self.openTFCharWindow)
        self.actionApproach_Control.triggered.connect(self.openApproachWindow)
        self.actionApproach_Monitor.triggered.connect(self.openApproachMonitorWindow)
        self.actionJPE_Coarse_Position_Control.triggered.connect(self.openJPEControlWindow)
        self.actionAttocube_Position_Calibration.triggered.connect(self.openPosCalibrationWindow)
        self.actionMagnetic_Field_Control.triggered.connect(self.openFieldControlWindow)
        self.actionRun_Scripts.triggered.connect(self.openScriptingModule)
        self.actionTemperature_Control.triggered.connect(self.openTempControlWindow)
        self.actionDevice_Characterizer.triggered.connect(self.openDeviceCharacterizerWindow)
        
        #Connectors all layout buttons
        self.push_Layout1.clicked.connect(self.setLayout1)
        
        self.push_Logo.clicked.connect(self.toggleLogo)
        self.isRedEyes = False
        
        #Connect 
        self.LabRAD.cxnLocal.connect(self.distributeLocalLabRADConnections)
        self.LabRAD.cxnRemote.connect(self.distributeRemoteLabRADConnections)
        self.LabRAD.cxnDisconnected.connect(self.disconnectLabRADConnections)
        self.LabRAD.newSessionFolder.connect(self.distributeSessionFolder)
        
        self.TFChar.workingPointSelected.connect(self.distributeWorkingPoint)

        self.Approach.newPLLData.connect(self.ApproachMonitor.updatePLLPlots)
        self.Approach.newFdbkDCData.connect(self.ApproachMonitor.updateFdbkDCPlot)
        self.Approach.newFdbkACData.connect(self.ApproachMonitor.updateFdbkACPlot)
        self.Approach.newZData.connect(self.ApproachMonitor.updateZPlot)
        
        self.Approach.updateFeedbackStatus.connect(self.ScanControl.updateFeedbackStatus)
        self.Approach.updateConstantHeightStatus.connect(self.ScanControl.updateConstantHeightStatus)
        self.Approach.updateApproachStatus.connect(self.JPEControl.updateApproachStatus)
        
        self.PosCalibration.newTemperatureCalibration.connect(self.setVoltageCalibration)
        
        self.ScanControl.updateScanningStatus.connect(self.Approach.updateScanningStatus)

        self.JPEControl.newJPESettings.connect(self.Approach.updateJPESettings)
        
        #Make sure default calibration is emitted 
        self.PosCalibration.emitCalibration()
        
        #Make sure default session flder is emitted
        self.LabRAD.newSessionFolder.emit(self.LabRAD.session_2)

        #Open by default the LabRAD Connect Module
        self.openLabRADConnectWindow()
        self.openDeviceCharacterizerWindow()

        
    def setupAdditionalUi(self):
        """Some UI elements would not set properly from Qt Designer. These initializations are done here."""
        pass
        
    #----------------------------------------------------------------------------------------------#
            
    """ The following section connects actions related to default opening windows."""
    
    def moveDefault(self):
        self.move(10,10)
    
    def openScanControlWindow(self):
        self.ScanControl.moveDefault()
        self.ScanControl.raise_()
        if self.ScanControl.isVisible() == False:
            self.ScanControl.show()
            
    def openLabRADConnectWindow(self):
        self.LabRAD.moveDefault()
        self.LabRAD.raise_()
        if self.LabRAD.isVisible() == False:
            self.LabRAD.show()
            
    def opennSOTCharWindow(self):
        self.nSOTChar.moveDefault()
        self.nSOTChar.raise_()
        if self.nSOTChar.isVisible() == False:
            self.nSOTChar.show()
            
    def openDataPlotter(self):
        self.Plot.moveDefault()
        self.Plot.raise_()
        if self.Plot.isVisible() == False:
            self.Plot.show()
            
    def openTFCharWindow(self):
        self.TFChar.moveDefault()
        self.TFChar.raise_()
        if self.TFChar.isVisible() == False:
            self.TFChar.show()
    
    def openApproachWindow(self):
        self.Approach.moveDefault()
        self.Approach.raise_()
        if self.Approach.isVisible() == False:
            self.Approach.show()

    def openApproachMonitorWindow(self):
        self.ApproachMonitor.moveDefault()
        self.ApproachMonitor.raise_()
        if self.ApproachMonitor.isVisible() == False:
            self.ApproachMonitor.show()
            
    def openJPEControlWindow(self):
        self.JPEControl.moveDefault()
        self.JPEControl.raise_()
        if self.JPEControl.isVisible() == False:
            self.JPEControl.show()

    def openPosCalibrationWindow(self):
        self.PosCalibration.moveDefault()
        self.PosCalibration.raise_()
        if self.PosCalibration.isVisible() == False:
            self.PosCalibration.show()
            
    def openFieldControlWindow(self):
        self.FieldControl.moveDefault()
        self.FieldControl.raise_()
        if self.FieldControl.isVisible() == False:
            self.FieldControl.show()
            
    def openTempControlWindow(self):
        self.TempControl.moveDefault()
        self.TempControl.raise_()
        self.TempControl.show()
        
    def openDeviceCharacterizerWindow(self):
        self.DeviceCharacterizer.moveDefault()
        self.DeviceCharacterizer.raise_()
        self.DeviceCharacterizer.show()
        
    def openScriptingModule(self):
        self.Scripting.moveDefault()
        self.Scripting.raise_()
        if self.Scripting.isVisible() == False:
            self.Scripting.show()
            
#----------------------------------------------------------------------------------------------#
            
    """ The following section connects actions related to passing LabRAD connections."""
    
    def distributeLocalLabRADConnections(self,dict):
        #Call connectLabRAD functions for relevant modules
        self.Plot.connectLabRAD(dict)
        self.nSOTChar.connectLabRAD(dict)
        self.ScanControl.connectLabRAD(dict)
        self.TFChar.connectLabRAD(dict)
        self.Approach.connectLabRAD(dict)
        self.JPEControl.connectLabRAD(dict)
        self.Scripting.connectLabRAD(dict)
        self.DeviceCharacterizer.connectLabRAD(dict)

        
    def distributeRemoteLabRADConnections(self,dict):
        #Call connectRemoteLabRAD functions for relevant modules
        self.FieldControl.connectRemoteLabRAD(dict)
        self.Scripting.connectRemoteLabRAD(dict)
        self.nSOTChar.connectRemoteLabRAD(dict)
        self.TempControl.connectRemoteLabRAD(dict)

    def disconnectLabRADConnections(self):
        self.Plot.disconnectLabRAD()
        self.nSOTChar.disconnectLabRAD()
        self.ScanControl.disconnectLabRAD()
        self.TFChar.disconnectLabRAD()
        self.Approach.disconnectLabRAD()
        self.JPEControl.disconnectLabRAD()
        self.FieldControl.disconnectLabRAD()
        self.Scripting.disconnectLabRAD()
        self.TempControl.disconnectLabRAD()
        self.DeviceCharacterizer.disconnectLabRAD(dict)

        
    def distributeSessionFolder(self, folder):
        self.TFChar.setSessionFolder(folder)
        self.ScanControl.setSessionFolder(folder)
        self.nSOTChar.setSessionFolder(folder)
        self.DeviceCharacterizer.setSessionFolder(folder)

        
    def updateDataVaultFolder(self):
        self.ScanControl.updateDataVaultDirectory()
        self.TFChar.updateDataVaultDirectory()
        self.nSOTChar.updateDataVaultDirectory()
        self.DeviceCharacterizer.updateDataVaultDirectory()


#----------------------------------------------------------------------------------------------#
            
    """ The following section connects signals between various modules."""
    def distributeWorkingPoint(self,freq, phase, channel, amplitude):
        self.Approach.setWorkingPoint(freq, phase, channel, amplitude)
        
    def setVoltageCalibration(self,data):
        self.Approach.set_voltage_calibration(data)
        self.ScanControl.set_voltage_calibration(data)

#----------------------------------------------------------------------------------------------#
            
    """ The following section connects actions related to setting the default layouts."""
        
    def setLayout1(self):
        self.moveDefault()
        self.hideAllWindows()
        self.openScanControlWindow()
        self.openApproachWindow()
        
    def toggleLogo(self):
        if self.isRedEyes == False:
            self.push_Logo.setStyleSheet("#push_Logo{"+
            "image:url(:/nSOTScanner/Pictures/SQUIDRotated.png);background: black;}")
            self.push_Logo.setToolTip('A SQUID has been hidden in every module (no exceptions). Can you find them all?')
            self.isRedEyes = True
        else:
            self.push_Logo.setStyleSheet("#push_Logo{"+
            "image:url(:/nSOTScanner/Pictures/SQUIDRotated2.png);background: black;}")
            self.push_Logo.setToolTip('')
            self.isRedEyes = False
            
    def hideAllWindows(self):
        self.ScanControl.hide()
        self.LabRAD.hide()
        self.nSOTChar.hide()
        self.Plot.hide()
        self.TFChar.hide()
        self.Approach.hide()
        self.ApproachMonitor.hide()
        self.JPEControl.hide()
        self.PosCalibration.hide()
            
    def closeEvent(self, e):
        try:
            self.disconnectLabRADConnections()
            self.ScanControl.close()
            self.nSOTChar.close()
            self.Plot.close()
            self.TFChar.close()
            self.Approach.close()
            self.ApproachMonitor.close()
            self.JPEControl.close()
            self.PosCalibration.close()
            self.Scripting.close()
            self.FieldControl.close()
            self.LabRAD.close()
        except Exception as inst:
            print inst
    
#----------------------------------------------------------------------------------------------#     
""" The following runs the GUI"""

if __name__=="__main__":
    import qt4reactor
    app = QtGui.QApplication(sys.argv)
    qt4reactor.install()
    from twisted.internet import reactor
    window = MainWindow(reactor)
    window.show()
    reactor.runReturn()
    sys.exit(app.exec_())

