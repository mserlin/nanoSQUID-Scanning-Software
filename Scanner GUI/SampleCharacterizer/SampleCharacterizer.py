from __future__ import division
import sys
import twisted
from PyQt4 import QtCore, QtGui, QtTest, uic
from twisted.internet.defer import inlineCallbacks, Deferred
import numpy as np
import pyqtgraph as pg
import exceptions
import time
import threading
import copy
from scipy.signal import detrend
#importing a bunch of stuff


#In retrospec, it is probably not well thought through in term of the long-term plan of organizing it.

################################################################################################################################



path = sys.path[0] + r"\SampleCharacterizer"
SampleCharacterizerWindowUI, QtBaseClass = uic.loadUiType(path + r"\SampleCharacterizerWindow.ui")
Ui_ServerList, QtBaseClass = uic.loadUiType(path + r"\requiredServers.ui")

#Not required, but strongly recommended functions used to format numbers in a particular way.
sys.path.append(sys.path[0]+'\Resources')
#from nSOTScannerFormat import readNum, formatNum, processLineData, processImageData, ScanImageView                #this part not sure, it was throwing an error


class Window(QtGui.QMainWindow, SampleCharacterizerWindowUI):

    def __init__(self, reactor, parent=None):
        super(Window, self).__init__(parent)



        self.aspectLocked = True
        self.FrameLocked = True
        self.LinearSpeedLocked = False
        self.DataLocked = True
        self.scanSmooth = True
        self.scanCoordinates = False
        self.dataProcessing = 'Raw'
        self.dataPostProcessing = 'Raw'


        self.reactor = reactor
        self.setupUi(self)


        self.Dict_LockIn= {  #A dictionary for lock in amplifier settings
         'V':1,
         'mV':10**-3,
         'uV':10**-6,
         'nV':10**-9,
         'uA':10**-6,
         'nA':10**-9,
         'pA':10**-12,
         'fA':10**-15,
         }


        self.DAC_Channel= {
         'DAC 1':0,
         'DAC 2':1,
         'DAC 3':2,
         'DAC 4':3,
         'ADC 1':0,# Defining Channel to Number
         'ADC 2':1,
         'ADC 3':2,
         'ADC 4':3,
         }

        self.randomFill = -0.987654321
        self.numberfastdata=100
        self.numberslowdata=100
        self.lineTime = 64e-3
        #do not know what it means

        self.FourTerminal_ChannelInput=[]
        self.FourTerminal_ChannelOutput=[]
        self.FourTerminal_MinVoltage=float(-1)
        self.FourTerminal_MaxVoltage=float(1)
        self.FourTerminal_Numberofstep=int(100)
        self.FourTerminal_Delay=int(10)
        self.lineEdit_FourTerminal_MinVoltage.setText(str(self.FourTerminal_MinVoltage))
        self.lineEdit_FourTerminal_MaxVoltage.setText(str(self.FourTerminal_MaxVoltage))
        self.lineEdit_FourTerminal_Numberofstep.setText(str(self.FourTerminal_Numberofstep))
        self.lineEdit_FourTerminal_Delay.setText(str(self.FourTerminal_Delay))

        #FourTerminal sweep basic parameter

        self.MainMagneticFieldSetting_MinimumField=float(0)
        self.MainMagneticFieldSetting_MaximumField=float(0)
        self.MainMagneticFieldSetting_NumberofstepsandMilifieldperTesla=int(1000)
        self.MainMagneticFieldSetting_FieldSweepSpeed=int(10)

        #Magnetic field sweep basic parameter

        self.comboBox_FourTerminal_Output1.setCurrentIndex(0)
        self.comboBox_FourTerminal_Input1.setCurrentIndex(1)
        self.comboBox_FourTerminal_Input2.setCurrentIndex(0)
        self.FourTerminal_Output1=self.comboBox_FourTerminal_Output1.currentIndex()
        self.FourTerminal_Input1=self.comboBox_FourTerminal_Input1.currentIndex()
        self.FourTerminal_Input2=self.comboBox_FourTerminal_Input2.currentIndex()



#        self.setupAdditionalUi()    #throwing an error

        self.moveDefault()

        #Connect show servers list pop up
        self.push_Servers.clicked.connect(self.showServersList)

#######################################
        self.pushButton_StartFourTerminalSweep.clicked.connect(self.Sweep)
        self.pushButton_DummyConnect.clicked.connect(self.connectLabRAD)

#######################################
        self.Device_Name='Device Name'
        self.FourTerminal_NameOutput1='Gate Voltage'
        self.FourTerminal_NameInput1='Voltage'
        self.FourTerminal_NameInput2='Current'
        self.lineEdit_Device_Name.setText(self.Device_Name)
        self.lineEdit_FourTerminal_NameOutput1.setText(self.FourTerminal_NameOutput1)
        self.lineEdit_FourTerminal_NameInput1.setText(self.FourTerminal_NameInput1)
        self.lineEdit_FourTerminal_NameInput2.setText(self.FourTerminal_NameInput2)

        self.lineEdit_FourTerminal_NameOutput1.editingFinished.connect(self.UpdateFourTerminal_NameOutput1)
        self.lineEdit_Device_Name.editingFinished.connect(self.UpdateDevice_Name)
        self.lineEdit_FourTerminal_NameInput1.editingFinished.connect(self.UpdateFourTerminal_NameInput1)
        self.lineEdit_FourTerminal_NameInput2.editingFinished.connect(self.UpdateFourTerminal_NameInput2)

#######################################
        self.lineEdit_FourTerminal_MinVoltage.editingFinished.connect(self.UpdateFourTerminal_MinVoltage)
        self.lineEdit_FourTerminal_MaxVoltage.editingFinished.connect(self.UpdateFourTerminal_MaxVoltage)
        self.lineEdit_FourTerminal_Numberofstep.editingFinished.connect(self.UpdateFourTerminal_Numberofstep)
        self.lineEdit_FourTerminal_Delay.editingFinished.connect(self.UpdateFourTerminal_Delay)
        self.Lineedit_MainMagneticFieldSetting_MinimumField.editingFinished.connect(self.UpdateMainMagneticFieldSetting_MinimumField)
        self.Lineedit_MainMagneticFieldSetting_MaximumField.editingFinished.connect(self.UpdateMainMagneticFieldSetting_MaximumField)
        self.Lineedit_MainMagneticFieldSetting_NumberofstepsandMilifieldperTesla.editingFinished.connect(self.UpdateMainMagneticFieldSetting_NumberofstepsandMilifieldperTesla)
        self.Lineedit_MainMagneticFieldSetting_FieldSweepSpeed.editingFinished.connect(self.UpdateMainMagneticFieldSetting_FieldSweepSpeed)
#######################################

        # self.Lineedit_Channel.editingFinished.connect(self.UpdateChannel)

#######################################
        self.comboBox_FourTerminal_Output1.currentIndexChanged.connect(self.ChangeFourTerminal_Output1_Channel)
        self.comboBox_FourTerminal_Input1.currentIndexChanged.connect(self.ChangeFourTerminal_Input1_Channel)
        self.comboBox_FourTerminal_Input2.currentIndexChanged.connect(self.ChangeFourTerminal_Input2_Channel)
#######################################

#######################################
        self.comboBox_Voltage_LI_Sensitivity_1stdigit.currentIndexChanged.connect(self.ChangeVoltage_LI_Sensitivity_1stdigit)
        self.comboBox_Voltage_LI_Sensitivity_2nddigit.currentIndexChanged.connect(self.ChangeVoltage_LI_Sensitivity_2nddigit)
        self.comboBox_Voltage_LI_Sensitivity_Unit.currentIndexChanged.connect(self.ChangeVoltage_LI_Sensitivity_Unit)
        self.comboBox_Voltage_LI_Expand.currentIndexChanged.connect(self.ChangeVoltage_LI_Expand)
        self.comboBox_Current_LI_Sensitivity_1stdigit.currentIndexChanged.connect(self.ChangeCurrent_LI_Sensitivity_1stdigit)
        self.comboBox_Current_LI_Sensitivity_2nddigit.currentIndexChanged.connect(self.ChangeCurrent_LI_Sensitivity_2nddigit)
        self.comboBox_Current_LI_Sensitivity_Unit.currentIndexChanged.connect(self.ChangeCurrent_LI_Sensitivity_Unit)
        self.comboBox_Current_LI_Expand.currentIndexChanged.connect(self.ChangeCurrent_LI_Expand)

#######################################
#######################################
        self.Voltage_LI_Multiplier1=0.0
        self.Voltage_LI_Multiplier2=0.0
        self.Voltage_LI_Multiplier3=0.0
        self.Voltage_LI_Multiplier4=0.0
        self.Current_LI_Multiplier1=0.0
        self.Current_LI_Multiplier2=0.0
        self.Current_LI_Multiplier3=0.0
        self.Current_LI_Multiplier4=0.0
        self.ChangeVoltage_LI_Sensitivity_1stdigit()
        self.ChangeVoltage_LI_Sensitivity_2nddigit()
        self.ChangeVoltage_LI_Sensitivity_Unit()
        self.ChangeVoltage_LI_Expand()
        self.ChangeCurrent_LI_Sensitivity_1stdigit()
        self.ChangeCurrent_LI_Sensitivity_2nddigit()
        self.ChangeCurrent_LI_Sensitivity_Unit()
        self.ChangeCurrent_LI_Expand()

#######################################

        #Initialize all the labrad connections as none
        self.cxn = None
        self.dv = None
        self.setupFourTerminalPlot()




        #self.lockInterface()


    def setupFourTerminalPlot(self):
        self.sweepFourTerminal_Plot1 = pg.PlotWidget(parent = self.FourTerminalPlot1)
        self.sweepFourTerminal_Plot1.setGeometry(QtCore.QRect(0, 0, 400, 200))
        self.sweepFourTerminal_Plot1.setLabel('left', self.FourTerminal_NameInput1, units = 'V')
        self.sweepFourTerminal_Plot1.setLabel('bottom', self.FourTerminal_NameOutput1, units = 'V')
        self.sweepFourTerminal_Plot1.showAxis('right', show = True)
        self.sweepFourTerminal_Plot1.showAxis('top', show = True)
        self.sweepFourTerminal_Plot1.setXRange(0,1)
        self.sweepFourTerminal_Plot1.setYRange(0,2)
        self.sweepFourTerminal_Plot1.enableAutoRange(enable = True)
        self.Layout_FourTerminalPlot1.addWidget(self.sweepFourTerminal_Plot1)

        self.sweepFourTerminal_Plot2 = pg.PlotWidget(parent = self.FourTerminalPlot2)
        self.sweepFourTerminal_Plot2.setGeometry(QtCore.QRect(0, 0, 400, 200))
        self.sweepFourTerminal_Plot2.setLabel('left', self.FourTerminal_NameInput2, units = 'A')
        self.sweepFourTerminal_Plot2.setLabel('bottom', self.FourTerminal_NameOutput1, units = 'V')
        self.sweepFourTerminal_Plot2.showAxis('right', show = True)
        self.sweepFourTerminal_Plot2.showAxis('top', show = True)
        self.sweepFourTerminal_Plot2.setXRange(0,1)
        self.sweepFourTerminal_Plot2.setYRange(0,2)
        self.sweepFourTerminal_Plot2.enableAutoRange(enable = True)
        self.Layout_FourTerminalPlot2.addWidget(self.sweepFourTerminal_Plot2)

        self.sweepFourTerminal_Plot3 = pg.PlotWidget(parent = self.FourTerminalPlot3)
        self.sweepFourTerminal_Plot3.setGeometry(QtCore.QRect(0, 0, 400, 200))
        self.sweepFourTerminal_Plot3.setLabel('left', 'Resistance', units = 'Ohm')
        self.sweepFourTerminal_Plot3.setLabel('bottom', self.FourTerminal_NameOutput1, units = 'V')
        self.sweepFourTerminal_Plot3.showAxis('right', show = True)
        self.sweepFourTerminal_Plot3.showAxis('top', show = True)
        self.sweepFourTerminal_Plot3.setXRange(0,1)
        self.sweepFourTerminal_Plot3.setYRange(0,2)
        self.sweepFourTerminal_Plot3.enableAutoRange(enable = True)
        self.Layout_FourTerminalPlot3.addWidget(self.sweepFourTerminal_Plot3)

    def updateFourTerminalPlotLabel(self):
        self.sweepFourTerminal_Plot1.setLabel('left', self.FourTerminal_NameInput2, units = 'V')
        self.sweepFourTerminal_Plot1.setLabel('bottom', self.FourTerminal_NameOutput1, units = 'V')
        self.sweepFourTerminal_Plot2.setLabel('left', 'DC Feedback Voltage', units = 'V')
        self.sweepFourTerminal_Plot2.setLabel('bottom', 'Bias Voltage', units = 'V')
        self.sweepFourTerminal_Plot3.setLabel('left', 'DC Feedback Voltage', units = 'V')
        self.sweepFourTerminal_Plot3.setLabel('bottom', 'Bias Voltage', units = 'V')

    def moveDefault(self):
        self.move(550,10)

    @inlineCallbacks
    def connectLabRAD(self, dict):
        try:
            from labrad.wrappers import connectAsync
            self.cxn = yield connectAsync(host = '127.0.0.1', password = 'pass')
            self.dv = yield self.cxn.data_vault
            self.dac = yield self.cxn.dac_adc
            yield self.dac.select_device(0L)

            self.push_Servers.setStyleSheet("#push_Servers{" +
            "background: rgb(0, 170, 0);border-radius: 4px;}")
        except Exception as inst:
            print inst
            self.push_Servers.setStyleSheet("#push_Servers{" +
            "background: rgb(161, 0, 0);border-radius: 4px;}")
        if not self.cxn:
            self.push_Servers.setStyleSheet("#push_Servers{" +
            "background: rgb(161, 0, 0);border-radius: 4px;}")
        elif not self.dac:
            self.push_Servers.setStyleSheet("#push_Servers{" +
            "background: rgb(161, 0, 0);border-radius: 4px;}")
        elif not self.dv:
            self.push_Servers.setStyleSheet("#push_Servers{" +
            "background: rgb(161, 0, 0);border-radius: 4px;}")
        else:
            print "Connection Finished"
            self.unlockInterface()

    def disconnectLabRAD(self):
        self.cxn = False
        self.cxn_dv = False
        self.dac = False
        self.gen_dv = False
        self.dv = False
        self.dc_box = False

        self.lockInterface()

        self.push_Servers.setStyleSheet("#push_Servers{" +
            "background: rgb(144, 140, 9);border-radius: 4px;}")






    def showServersList(self):
        serList = serversList(self.reactor, self)
        serList.exec_()

    def updateDataVaultDirectory(self):
        curr_folder = yield self.gen_dv.cd()
        yield self.dv.cd(curr_folder)


    # def setupAdditionalUi(self):
        # #Set up UI that isn't easily done from Qt Designer
        # self.view = pg.PlotItem(title="Plot")
# #        self.view.setLabel('left',text='Y position',units = 'm')
# #        self.view.setLabel('right',text='Y position',units = 'm')
# #        self.view.setLabel('top',text='X position',units = 'm')
# #        self.view.setLabel('bottom',text='X position',units = 'm')
        # self.Plot2D = ScanImageView(parent = self.centralwidget, view = self.view, randFill = self.randomFill)
        # self.view.invertY(False)
        # self.view.setAspectLocked(self.aspectLocked)
        # self.Plot2D.ui.roiBtn.hide()
        # self.Plot2D.ui.menuBtn.hide()
        # self.Plot2D.ui.histogram.item.gradient.loadPreset('bipolar')
        # self.Plot2D.lower()
        # self.PlotArea.close()
        # self.horizontalLayout.addWidget(self.Plot2D)

    def updateHistogramLevels(self, hist):
        mn, mx = hist.getLevels()
        self.Plot2D.ui.histogram.setLevels(mn, mx)

    # Below function is not necessary, but is often useful. Yielding it will provide an asynchronous
    # delay that allows other labrad / pyqt methods to run



    @inlineCallbacks
    def Sweep(self,c=None):
        self.lockInterface()

        try:
            self.sweepFourTerminal_Plot1.clear()
            self.sweepFourTerminal_Plot2.clear()#clear all the plot
            self.sweepFourTerminal_Plot3.clear()

            self.FourTerminal_ChannelOutput=[]
            self.FourTerminal_ChannelOutput.append(self.FourTerminal_Output1)#setup for bufferramp function

            self.FourTerminal_ChannelInput=[]
            self.FourTerminal_ChannelInput.append(self.FourTerminal_Input1)#setup for bufferramp function


            if self.FourTerminal_Input2!=4:
                self.FourTerminal_ChannelInput.append(self.FourTerminal_Input2)# Create the list of Channel that we read while sweep #setup for bufferramp function

            yield self.sleep(0.1)
            a = yield self.dac.read()
            while a != '':
                print a
                a = yield self.dac.read() #necessary for long ramp(ramp function does not read all the data)

            self.datavaultXaxis=[]
            self.datavaultXaxis.append(self.FourTerminal_NameOutput1+' index')# This part is for setting correct datavault input

            self.datavaultXaxis.append(self.FourTerminal_NameOutput1)
            self.datavaultYaxis=[]
            self.datavaultYaxis.append(self.FourTerminal_NameInput1)
            if self.FourTerminal_Input2!=4:  #add additional data if Input2 is not None
                self.datavaultYaxis.append(self.FourTerminal_NameInput2)#Yaxis is misnamed for independent variables
                self.datavaultYaxis.append("Resistance")#replace name one day
#change for resistance later                self.datavaultYaxis.append(self.FourTerminal_NameInput3)





            file_info = yield self.dv.new(self.Device_Name, self.datavaultXaxis,self.datavaultYaxis)
            self.dvFileName = file_info[1]
            self.lineEdit_ImageNumber.setText(file_info[1][0:5])
            session  = ''
            for folder in file_info[0][1:]:
                session = session + '\\' + folder
            self.lineEdit_ImageDir.setText(r'\.datavault' + session)

            yield self.dac.ramp1(self.FourTerminal_ChannelOutput[0],0.0,self.FourTerminal_MinVoltage,10000,100)    #ramp to initial value

            yield self.sleep(0.1)
            a = yield self.dac.read()
            while a != '':
                print a
                a = yield self.dac.read() #necessary for long ramp(ramp function does not read all the data)

            yield self.sleep(1)

            FourTerminalXaxis=np.linspace(self.FourTerminal_MinVoltage,self.FourTerminal_MaxVoltage,self.FourTerminal_Numberofstep)  #generating list of voltage at which sweeped
            dac_read= yield self.dac.buffer_ramp(self.FourTerminal_ChannelOutput,self.FourTerminal_ChannelInput,[self.FourTerminal_MinVoltage],[self.FourTerminal_MaxVoltage],self.FourTerminal_Numberofstep,self.FourTerminal_Delay) #dac_read[0] is voltage,dac_read[1] is current potentially

            yield self.sleep(0.1)
            a = yield self.dac.read()
            while a != '':
                print a
                a = yield self.dac.read() #necessary for long ramp(ramp function does not read all the data)

            yield self.sleep(1)


            formatted_data = []
            for j in range(0, self.FourTerminal_Numberofstep):
                DummyVoltage=float(dac_read[0][j])/10.0*self.MultiplierVoltage
                formatted_data.append((j, FourTerminalXaxis[j],DummyVoltage))
                if self.FourTerminal_Input2!=4:  #add additional data if Input2 is not None
                    DummyCurrent=float(dac_read[1][j])/10.0*self.MultiplierCurrent
                    formatted_data[j]+=(DummyCurrent,)
                    resistance=float(DummyVoltage/DummyCurrent) #generating resisitance
                    formatted_data[j]+=(resistance,)  #proccessing to Resistance


            yield self.dv.add(formatted_data)
            yield self.plotFourTerminal_Data1(formatted_data)


            yield self.dac.ramp1(self.FourTerminal_ChannelOutput[0],self.FourTerminal_MaxVoltage,0.0,10000,100)

            if self.FourTerminal_Input2!=4:
                 yield self.plotFourTerminal_Data2(formatted_data)
                 yield self.plotFourTerminal_Data3(formatted_data)
        except Exception as inst:
            print inst

        self.unlockInterface()
        yield self.sleep(0.25)
        self.saveDataToSessionFolder() #save the screenshot

    def saveDataToSessionFolder(self):
        try:
            p = QtGui.QPixmap.grabWindow(self.winId())
            a = p.save(self.sessionFolder + '\\' + self.dvFileName + '.jpg','jpg')
            if not a:
                print "Error saving Scan data picture"
        except Exception as inst:
            print 'Scan error: ', inst
            print 'on line: ', sys.exc_traceback.tb_lineno

    def plotFourTerminal_Data1(self, data):
        self.data = data
        xVals = [x[1] for x in self.data]
        yVals = [x[2] for x in self.data]
        self.sweepFourTerminal_Plot1.plot(x = xVals, y = yVals, pen = 0.5)


    def plotFourTerminal_Data2(self, data):
        self.data = data
        xVals = [x[1] for x in self.data]
        yVals = [x[3] for x in self.data]
        self.sweepFourTerminal_Plot2.plot(x = xVals, y = yVals, pen = 0.5)

    def plotFourTerminal_Data3(self, data):
        self.data = data
        xVals = [x[1] for x in self.data]
        yVals = [x[4] for x in self.data]
        self.sweepFourTerminal_Plot3.plot(x = xVals, y = yVals, pen = 0.5)

    @inlineCallbacks
    def update_data(self):
        try:
            #Create data vault file with appropriate parameters
            #Retrace index is 0 for trace, 1 for retrace
            file_info = yield self.dv.new("Sample Charactorizing Data " + self.fileName, ['Retrace Index','X Pos. Index','Y Pos. Index','X Pos. Voltage', 'Y Pos. Voltage'],['Z Position',self.inputs['Input 1 name'], self.inputs['Input 2 name']])
            self.dvFileName = file_info[1]
            self.lineEdit_ImageNum.setText(file_info[1][0:5])
            session  = ''
            for folder in file_info[0][1:]:
                session = session + '\\' + folder
            self.lineEdit_ImageDir.setText(r'\.datavault' + session)


            a = yield self.dac.read()
            while a != '':
                print a
                a = yield self.dac.read()

            startfast = self.startOutput1

            for i in range(0,self,numberslowdata):
                startslow = self.startOutput2
                stopfast = self.stopOutput1
                out_list = [self.outputs['Output 1']-1]
                in_list = [self.inputs['Input 1']-1]
                newData = yield self.dac.buffer_ramp(out_list,in_list,[startx],[stopx], self.numberfastdata, self.FourTerminal_Delay)

            for j in range(0, self.pixels):
                #Putting in 0 for SSAA voltage (last entry) because not yet being used/read
                formatted_data.append((1, j, i, x_voltage[::-1][j], y_voltage[::-1][j], self.data_retrace[0][j,i], self.data_retrace[1][j,i], self.data_retrace[2][j,i]))
                yield self.dv.add(formatted_data)
        except:
            print "This is an error message!"


    def UpdateMultiplier(self):
        self.MultiplierVoltage=self.Voltage_LI_Multiplier1*self.Voltage_LI_Multiplier2*self.Voltage_LI_Multiplier3*self.Voltage_LI_Multiplier4
        self.MultiplierCurrent=self.Current_LI_Multiplier1*self.Current_LI_Multiplier2*self.Current_LI_Multiplier3*self.Current_LI_Multiplier4



##########################Update All the parameters#################
    def UpdateFourTerminal_MinVoltage(self):
        self.FourTerminal_MinVoltage=float(str(self.lineEdit_FourTerminal_MinVoltage.text()))

    def UpdateFourTerminal_MaxVoltage(self):
        self.FourTerminal_MaxVoltage=float(str(self.lineEdit_FourTerminal_MaxVoltage.text()))

    def UpdateFourTerminal_Numberofstep(self):
        self.FourTerminal_Numberofstep=int(str(self.lineEdit_FourTerminal_Numberofstep.text()))

    def UpdateFourTerminal_Delay(self):
        self.FourTerminal_Delay=int(str(self.lineEdit_FourTerminal_Delay.text()))

    def UpdateDevice_Name(self):
        self.Device_Name=str(self.lineEdit_Device_Name.text())


    def UpdateFourTerminal_NameOutput1(self):
        self.FourTerminal_NameOutput1=str(self.lineEdit_FourTerminal_NameOutput1.text())
        self.updateFourTerminalPlotLabel()

    def UpdateFourTerminal_NameInput1(self):
        self.FourTerminal_NameInput1=str(self.lineEdit_FourTerminal_NameInput1.text())
        self.updateFourTerminalPlotLabel()

    def UpdateFourTerminal_NameInput2(self):
        self.FourTerminal_NameInput2=str(self.lineEdit_FourTerminal_NameInput2.text())
        self.updateFourTerminalPlotLabel()

    def UpdateMainMagneticFieldSetting_MinimumField(self):
        self.MainMagneticFieldSetting_MinimumField=float(str(self.Lineedit_MainMagneticFieldSetting_MinimumField.text()))

    def UpdateMainMagneticFieldSetting_MaximumField(self):
        self.MainMagneticFieldSetting_MaximumField=float(str(self.Lineedit_MainMagneticFieldSetting_MaximumField.text()))

    def UpdateMainMagneticFieldSetting_NumberofstepsandMilifieldperTesla(self):
        self.MainMagneticFieldSetting_NumberofstepsandMilifieldperTesla=int(str(self.Lineedit_MainMagneticFieldSetting_NumberofstepsandMilifieldperTesla.text()))

    def UpdateMainMagneticFieldSetting_FieldSweepSpeed(self):
        self.MainMagneticFieldSetting_FieldSweepSpeed=int(str(self.Lineedit_MainMagneticFieldSetting_FieldSweepSpeed.text()))

    def ChangeFourTerminal_Output1_Channel(self):
        self.FourTerminal_Output1=self.comboBox_FourTerminal_Output1.currentIndex()

    def ChangeFourTerminal_Input1_Channel(self):
        self.FourTerminal_Input1=self.comboBox_FourTerminal_Input1.currentIndex()

    def ChangeFourTerminal_Input2_Channel(self):
        self.FourTerminal_Input2=self.comboBox_FourTerminal_Input2.currentIndex()

    def ChangeVoltage_LI_Sensitivity_1stdigit(self):
        self.Voltage_LI_Multiplier1=int(self.comboBox_Voltage_LI_Sensitivity_1stdigit.currentText())
        self.UpdateMultiplier()

    def ChangeVoltage_LI_Sensitivity_2nddigit(self):
        self.Voltage_LI_Multiplier2=int(self.comboBox_Voltage_LI_Sensitivity_2nddigit.currentText())
        self.UpdateMultiplier()

    def ChangeVoltage_LI_Sensitivity_Unit(self):
        self.Voltage_LI_Multiplier3=float(self.Dict_LockIn[str(self.comboBox_Voltage_LI_Sensitivity_Unit.currentText())])
        self.UpdateMultiplier()

    def ChangeVoltage_LI_Expand(self):
        self.Voltage_LI_Multiplier4=float(self.comboBox_Voltage_LI_Expand.currentText())
        self.UpdateMultiplier()

    def ChangeCurrent_LI_Sensitivity_1stdigit(self):
        self.Current_LI_Multiplier1=int(self.comboBox_Current_LI_Sensitivity_1stdigit.currentText())
        self.UpdateMultiplier()

    def ChangeCurrent_LI_Sensitivity_2nddigit(self):
        self.Current_LI_Multiplier2=int(self.comboBox_Current_LI_Sensitivity_2nddigit.currentText())
        self.UpdateMultiplier()

    def ChangeCurrent_LI_Sensitivity_Unit(self):
        self.Current_LI_Multiplier3=float(self.Dict_LockIn[str(self.comboBox_Current_LI_Sensitivity_Unit.currentText())])
        self.UpdateMultiplier()

    def ChangeCurrent_LI_Expand(self):
        self.Current_LI_Multiplier4=float(self.comboBox_Current_LI_Expand.currentText())
        self.UpdateMultiplier()


        ##########################Update All the parameters#################


    def updateHistogramLevels(self, hist):
        mn, mx = hist.getLevels()
        self.Plot2D.ui.histogram.setLevels(mn, mx)
        #self.autoLevels = False

    def setSessionFolder(self, folder):
        self.sessionFolder = folder

    def sleep(self,secs):
        """Asynchronous compatible sleep command. Sleeps for given time in seconds, but allows
        other operations to be done elsewhere while paused."""
        d = Deferred()
        self.reactor.callLater(secs,d.callback,'Sleeping')
        return d

#----------------------------------------------------------------------------------------------#
    """ The following section has generally useful functions."""

    def lockInterface(self):
        self.lineEdit_FourTerminal_NameOutput1.setEnabled(False)
        self.lineEdit_FourTerminal_NameInput1.setEnabled(False)
        self.lineEdit_FourTerminal_NameInput2.setEnabled(False)
        self.lineEdit_FourTerminal_MinVoltage.setEnabled(False)
        self.lineEdit_FourTerminal_MaxVoltage.setEnabled(False)
        self.lineEdit_FourTerminal_Numberofstep.setEnabled(False)
        self.lineEdit_FourTerminal_Delay.setEnabled(False)
        self.PushButton_Preliminary_NoSmTpTSwitch_2.setEnabled(False)

        self.comboBox_FourTerminal_Output1.setEnabled(False)
        self.comboBox_FourTerminal_Input1.setEnabled(False)
        self.comboBox_FourTerminal_Input2.setEnabled(False)
        self.comboBox_Voltage_LI_Sensitivity_1stdigit.setEnabled(False)
        self.comboBox_Voltage_LI_Sensitivity_2nddigit.setEnabled(False)
        self.comboBox_Voltage_LI_Expand.setEnabled(False)
        self.comboBox_Current_LI_Sensitivity_1stdigit.setEnabled(False)
        self.comboBox_Current_LI_Sensitivity_2nddigit.setEnabled(False)
        self.comboBox_Current_LI_Sensitivity_Unit.setEnabled(False)
        self.comboBox_Current_LI_Expand.setEnabled(False)

        self.pushButton_StartFourTerminalSweep.setEnabled(False)

    def unlockInterface(self):
        self.lineEdit_FourTerminal_NameOutput1.setEnabled(True)
        self.lineEdit_FourTerminal_NameInput1.setEnabled(True)
        self.lineEdit_FourTerminal_NameInput2.setEnabled(True)
        self.lineEdit_FourTerminal_MinVoltage.setEnabled(True)
        self.lineEdit_FourTerminal_MaxVoltage.setEnabled(True)
        self.lineEdit_FourTerminal_Numberofstep.setEnabled(True)
        self.lineEdit_FourTerminal_Delay.setEnabled(True)
        self.PushButton_Preliminary_NoSmTpTSwitch_2.setEnabled(True)

        self.comboBox_FourTerminal_Output1.setEnabled(True)
        self.comboBox_FourTerminal_Input1.setEnabled(True)
        self.comboBox_FourTerminal_Input2.setEnabled(True)
        self.comboBox_Voltage_LI_Sensitivity_1stdigit.setEnabled(True)
        self.comboBox_Voltage_LI_Sensitivity_2nddigit.setEnabled(True)
        self.comboBox_Voltage_LI_Expand.setEnabled(True)
        self.comboBox_Current_LI_Sensitivity_1stdigit.setEnabled(True)
        self.comboBox_Current_LI_Sensitivity_2nddigit.setEnabled(True)
        self.comboBox_Current_LI_Sensitivity_Unit.setEnabled(True)
        self.comboBox_Current_LI_Expand.setEnabled(True)

        self.pushButton_StartFourTerminalSweep.setEnabled(True)

class serversList(QtGui.QDialog, Ui_ServerList):
    def __init__(self, reactor, parent = None):
        super(serversList, self).__init__(parent)
        self.setupUi(self)
        pos = parent.pos()
        self.move(pos)
