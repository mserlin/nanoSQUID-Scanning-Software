import sys
from PyQt4 import QtGui, QtCore, uic
from twisted.internet.defer import inlineCallbacks, Deferred

path = sys.path[0] + r"\DeviceSelect"
DeviceSelectUI, QtBaseClass = uic.loadUiType(path + r"\DeviceSelect.ui")

#Not required, but strongly recommended functions used to format numbers in a particular way. 
sys.path.append(sys.path[0]+'\Resources')
from nSOTScannerFormat import readNum, formatNum

class Window(QtGui.QMainWindow, DeviceSelectUI):
    newDeviceInfo = QtCore.pyqtSignal(dict)
    
    def __init__(self, reactor, parent=None):
        super(Window, self).__init__(parent)
        
        self.reactor = reactor
        self.setupUi(self)
        self.setupAdditionalUi()

        #name of the file that stores the information about which configuration is the default configuration
        self.fileName = path + '\ConfigurationInfo.txt'
        
        self.moveDefault()
        
        self.localLabRADConnected = False
        self.remoteLabRADConnected = False
        
        #Set device dictionary to default empty state
        self.resetDeviceDictionary()
        
        #Creates a dictionary that organizes the GUI items into a similar structure as the deviceDictionary 
        #for easy iteration and structure
        self.GUIDictionary = {
        'devices': {
                    'system' : {
                        'magnet supply':  self.comboBox_MagnetPowerSupply,
                        'specific supply':   self.comboBox_MagnetSupplyDevice,
                        'blink device':     self.comboBox_BlinkDevice
                    },
                    'approach and TF' : {
                        'dac_adc':  self.comboBox_Approach_DACADC,
                        'dc_box':   self.comboBox_Approach_DCBox,
                        'hf2li':    self.comboBox_Approach_HF2LI
                    },
                    'scan' : {
                        'dac_adc':  self.comboBox_Scan_DACADC
                    },
                    'nsot' : {
                        'dac_adc':  self.comboBox_nSOT_DACADC
                    },
                    'sample' : {
                        'dac_adc':  self.comboBox_Sample_DACADC,
                        'dc_box':   self.comboBox_Sample_DCBox
                    }
        },
        'channels':{
                    'system' : {
                        'blink channel':     self.comboBox_BlinkChannel,
                        'toellner volt':    self.comboBox_ToeVolt,
                        'toellner current':    self.comboBox_ToeCurr
                    },
                    'approach and TF' : {
                        'pll input':    self.comboBox_Approach_PLLInput,
                        'pll output':    self.comboBox_Approach_PLLOutput,
                        'pid z out':    self.comboBox_Approach_PIDZOut,
                        'z monitor':    self.comboBox_Approach_ZMonitor
                    },
                    'scan' : {
                    },
                    'nsot' : {
                    },
                    'sample' : {
                    }
        }
        }
        
        self.push_setDefault.clicked.connect(self.setDefaultConfiguration)
        self.push_saveConfig.clicked.connect(self.saveConfigurationInfo)
        
        self.push_loadConfig.clicked.connect(self.loadNewConfigurationInfo)
        
        self.comboBox_Approach_DACADC.currentIndexChanged.connect(self.setApproachDACADC)
        self.comboBox_Approach_DCBox.currentIndexChanged.connect(self.setApproachDCBox)
        self.comboBox_Approach_HF2LI.currentIndexChanged.connect(self.setApproachHF2LI)
        
        self.comboBox_Scan_DACADC.currentIndexChanged.connect(self.setScanDACADC)
        
        self.comboBox_nSOT_DACADC.currentIndexChanged.connect(self.setNSOTDACADC)
        
        self.comboBox_MagnetPowerSupply.currentIndexChanged.connect(self.setMagnetPowerSupply)
        self.comboBox_MagnetSupplyDevice.currentIndexChanged.connect(self.setMagnetSupplyDevice)
        
        self.comboBox_Sample_DACADC.currentIndexChanged.connect(self.setSampleDACADC)
        self.comboBox_Sample_DCBox.currentIndexChanged.connect(self.setSampleDCBox)
        
        self.comboBox_BlinkDevice.currentIndexChanged.connect(self.setBlinkDevice)
        self.comboBox_BlinkChannel.currentIndexChanged.connect(self.setBlinkChannel)
        
    def moveDefault(self):
        self.move(550,10)
        
    def setupAdditionalUi(self):
        #Set up UI that isn't easily done from Qt Designer
        pass
        
    def setApproachDACADC(self):
        self.deviceDictionary['devices']['approach and TF']['dac_adc'] = str(self.comboBox_Approach_DACADC.currentText())
        
        self.label_Approach_DAC.setText(str(self.comboBox_Approach_DACADC.currentText()))
        
        ComboBox1 = self.comboBox_Approach_Sig1Device
        ComboBox2 = self.comboBox_Approach_Sig2Device
        
        AllItems = [ComboBox1.itemText(i) for i in range(ComboBox1.count())]
                
        for item in AllItems:
            if str(item).startswith('DA'):
                ComboBox1.removeItem(AllItems.index(item))
                ComboBox2.removeItem(AllItems.index(item))
        
        ComboBox1.addItem(str(self.comboBox_Approach_DACADC.currentText()))
        ComboBox2.addItem(str(self.comboBox_Approach_DACADC.currentText()))
        
    def setApproachDCBox(self):
        self.deviceDictionary['devices']['approach and TF']['dc_box'] = str(self.comboBox_Approach_DCBox.currentText())
        self.label_Approach_DCBox.setText(str(self.comboBox_Approach_DCBox.currentText()))
    
    def setApproachHF2LI(self):
        self.deviceDictionary['devices']['approach and TF']['hf2li'] = str(self.comboBox_Approach_HF2LI.currentText())
        self.label_Approach_HF1.setText(str(self.comboBox_Approach_HF2LI.currentText()))
        self.label_Approach_HF2.setText(str(self.comboBox_Approach_HF2LI.currentText()))
        self.label_Approach_HF3.setText(str(self.comboBox_Approach_HF2LI.currentText()))
        self.label_Approach_HF4.setText(str(self.comboBox_Approach_HF2LI.currentText()))
        
        ComboBox1 = self.comboBox_Approach_Sig1Device
        ComboBox2 = self.comboBox_Approach_Sig2Device
        
        AllItems = [ComboBox1.itemText(i) for i in range(ComboBox1.count())]
                
        for item in AllItems:
            if str(item).startswith('dev'):
                ComboBox1.removeItem(AllItems.index(item))
                ComboBox2.removeItem(AllItems.index(item))
        
        ComboBox1.addItem(str(self.comboBox_Approach_HF2LI.currentText()))
        ComboBox2.addItem(str(self.comboBox_Approach_HF2LI.currentText()))
        
    def setScanDACADC(self):
        self.deviceDictionary['devices']['scan']['dac_adc'] = str(self.comboBox_Scan_DACADC.currentText())
        self.label_Scan_Device1.setText(str(self.comboBox_Scan_DACADC.currentText()))
        self.label_Scan_Device2.setText(str(self.comboBox_Scan_DACADC.currentText()))
        self.label_Scan_Device3.setText(str(self.comboBox_Scan_DACADC.currentText()))
        
    def setNSOTDACADC(self):
        self.deviceDictionary['devices']['nsot']['dac_adc'] = str(self.comboBox_nSOT_DACADC.currentText())
        
        self.label_nSOT_Device1.setText(str(self.comboBox_nSOT_DACADC.currentText()))
        self.label_nSOT_Device2.setText(str(self.comboBox_nSOT_DACADC.currentText()))
        self.label_nSOT_Device3.setText(str(self.comboBox_nSOT_DACADC.currentText()))
        self.label_nSOT_Device4.setText(str(self.comboBox_nSOT_DACADC.currentText()))
        self.label_nSOT_Device5.setText(str(self.comboBox_nSOT_DACADC.currentText()))
        
    def setMagnetPowerSupply(self):
        self.deviceDictionary['devices']['system']['magnet supply'] = str(self.comboBox_MagnetPowerSupply.currentText())
        if str(self.comboBox_MagnetPowerSupply.currentText()).startswith('IPS'):
            self.label_ToeVolt.setVisible(False)
            self.label_ToeCurr.setVisible(False)
            self.label_ToeVoltDevice.setVisible(False)
            self.label_ToeCurrDevice.setVisible(False)
            self.comboBox_ToeVolt.setVisible(False)
            self.comboBox_ToeCurr.setVisible(False)
        elif str(self.comboBox_MagnetPowerSupply.currentText()).startswith('Toe'):
            self.label_ToeVolt.setVisible(True)
            self.label_ToeCurr.setVisible(True)
            self.label_ToeVoltDevice.setVisible(True)
            self.label_ToeCurrDevice.setVisible(True)
            self.comboBox_ToeVolt.setVisible(True)
            self.comboBox_ToeCurr.setVisible(True)
        
    def setMagnetSupplyDevice(self):
        self.deviceDictionary['devices']['system']['specific supply'] = str(self.comboBox_MagnetSupplyDevice.currentText())
        self.label_ToeVoltDevice.setText(str(self.comboBox_MagnetSupplyDevice.currentText()))
        self.label_ToeCurrDevice.setText(str(self.comboBox_MagnetSupplyDevice.currentText()))
        
    def setBlinkDevice(self):
        self.deviceDictionary['devices']['system']['blink device'] = str(self.comboBox_BlinkDevice.currentText())
        self.label_BlinkDevice.setText(str(self.comboBox_BlinkDevice.currentText()))
        
    def setBlinkChannel(self):
        self.deviceDictionary['channels']['system']['blink channel'] = str(self.comboBox_BlinkChannel.currentText())
        
    def setSampleDACADC(self):
        self.deviceDictionary['devices']['sample']['dac_adc'] = str(self.comboBox_Sample_DACADC.currentText())
        
    def setSampleDCBox(self):
        self.deviceDictionary['devices']['sample']['dc_box'] = str(self.comboBox_Sample_DCBox.currentText())

        
    @inlineCallbacks
    def connectLabRAD(self, dict):
        try:
            self.deviceDictionary['servers']['local'] = dict
        
            if not not dict['dac_adc']:
                list = yield dict['dac_adc'].list_devices()
                
                #For this section, adding the items to the comboBoxes 
                for device in list:
                    self.GUIDictionary['devices']['approach and TF']['dac_adc'].addItem(device[1])
                    self.GUIDictionary['devices']['scan']['dac_adc'].addItem(device[1])
                    self.GUIDictionary['devices']['nsot']['dac_adc'].addItem(device[1])
                    self.GUIDictionary['devices']['sample']['dac_adc'].addItem(device[1])
                    self.GUIDictionary['devices']['system']['specific supply'].addItem(device[1])
                    self.GUIDictionary['devices']['system']['blink device'].addItem(device[1])
                    
                if len(list) > 0:
                    self.GUIDictionary['devices']['system']['magnet supply'].addItem('Toellner Power Supply')

            if not not dict['dc_box']:
                list = yield dict['dc_box'].list_devices()
                for device in list:
                    self.GUIDictionary['devices']['approach and TF']['dc_box'].addItem(device[1])
                    self.GUIDictionary['devices']['sample']['dc_box'].addItem(device[1])
                    self.GUIDictionary['devices']['system']['blink device'].addItem(device[1])
                    
            if not not dict['hf2li']:
                list = yield dict['hf2li'].list_devices()
                for device in list:
                    self.comboBox_Approach_HF2LI.addItem(device[1])
                    
            self.localLabRADConnected = True
            if self.localLabRADConnected and self.remoteLabRADConnected:
                self.loadDefaultConfigurationInfo()
        except Exception as inst:
            print 'connectLocal', inst
            print 'on line: ', sys.exc_traceback.tb_lineno
            
    @inlineCallbacks
    def connectRemoteLabRAD(self, dict):
        try:
            self.deviceDictionary['servers']['remote'] = dict
            
            if not not dict['ips120']:
                list = yield dict['ips120'].list_devices()
                for device in list:
                    self.comboBox_MagnetSupplyDevice.addItem(device[1])

                if len(list) > 0:
                    self.deviceDictionary['devices']['system']['specific supply'] = list[0][1]
                    self.comboBox_MagnetPowerSupply.addItem('IPS 120 Power Supply')

            self.remoteLabRADConnected = True
            if self.localLabRADConnected and self.remoteLabRADConnected:
                self.loadDefaultConfigurationInfo()
        except Exception as inst:
            print 'connectRemote', inst
            print 'on line: ', sys.exc_traceback.tb_lineno
        
    def resetDeviceDictionary(self):
        self.deviceDictionary = {
        'servers': {
        #Gets autopopulated from the labrad connect server emitted 
        },
        'devices': {
                    'system' : {
                        'magnet supply':  False,
                        'specific supply':   False,
                        'blink device':  False,
                    },
                    'approach and TF' : {
                        'dac_adc':  False,
                        'dc_box':   False,
                        'hf2li':    False
                    },
                    'scan' : {
                        'dac_adc':  False
                    },
                    'nsot' : {
                        'dac_adc':  False
                    },
                    'sample' : {
                        'dac_adc':  False,
                        'dc_box':   False,
                    }
        },
        'channels':{
                    'system' : {
                        'toellner dac voltage':  4,
                        'toellner dac current':  3,
                        'blink channel':  2,
                    },
                    'approach and TF' : {
                        'pll input':    'Sig In 1',
                        'pll output':   'Sig Out 1',
                        'pid z out':    'Aux Out 1',
                        'z monitor':    'Aux In 1(<20 kHz)',
                        'step Z out':   'DAC Out 1', 
                        'sum board toggle': 'DC BOx 1',
                    },
                    'scan' : {
                        'z out':        1,
                        'x out':        2,
                        'y out':        3,
                    },
                    'nsot' : {
                        'Bias Reference':    1,
                        'DC Readout':        2,
                        'AC Readout':        3,
                        'Noise Readout':     2,
                        'nSOT Bias':         4, 
                        'nSOT Gate':         3, 
                    },
                    'sample' : {
                        'dac_adc':  self.comboBox_Sample_DACADC,
                        'dc_box':   self.comboBox_Sample_DCBox
                    }
        }
        }
        
    def disconnectLabRAD(self):
        #Reinitialize deviceDictionary to be empty
        self.resetDeviceDictionary()
        self.localLabRADConnected = False
        self.remoteLabRADConnected = False
        
        #Remove all devices from the GUI
        for section, dev_list in self.GUIDictionary['devices'].iteritems():
            for dev, dev_name in dev_list.iteritems():
                self.GUIDictionary['devices'][section][dev].clear() 
        
    def loadDefaultConfigurationInfo(self):
        f = open(self.fileName,'r')
        defaultConfig = f.read()
        self.configFileName = defaultConfig
        self.label_currentConfigFile.setText(self.configFileName)
        f.close()
        
        self.loadConfigurationInfo()
        
    def loadNewConfigurationInfo(self):
        file = str(QtGui.QFileDialog.getOpenFileName(self, directory = path, filter = "Text files (*.txt)"))
        self.configFileName = file.split('/')[-1]
        self.label_currentConfigFile.setText(self.configFileName)
        
        self.loadConfigurationInfo()
        
    def loadConfigurationInfo(self):
        f = open(path + '\\' + self.configFileName,'r')
        message = f.read()
        f.close()
        
        entries = message.splitlines()
        for entry in entries:
            entry = entry.split(';')
            name = entry[0]
            entry.remove(entry[0])
            for item in entry:
                item = item.split(',')
                self.deviceDictionary['devices'][name][item[0]] = item[1]
        
        self.checkLoadedConfiguration()
        
    def checkLoadedConfiguration(self):
        try:
            #keep track of which parts of the loaded config file were not found
            configNotFound = ''
            
            #Check all the devices in all the sections
            for section, dev_list in self.deviceDictionary['devices'].iteritems():
                for dev, dev_name in dev_list.iteritems():
                    ComboBox = self.GUIDictionary['devices'][section][dev]
                    AllItems = [ComboBox.itemText(i) for i in range(ComboBox.count())]
                
                    if dev_name in AllItems:
                        ComboBox.setCurrentIndex(AllItems.index(dev_name))
                    else:
                        if len(AllItems) > 0:
                            self.deviceDictionary['devices'][section][dev] = AllItems[0]
                        else:
                            self.deviceDictionary['devices'][section][dev] = False
                        configNotFound = configNotFound + str(dev_name) + ' was not found in the ' + str(section) + ' tab for the following device: ' + dev + '.\n'
            
            #If something wasn't found, throw error letting user know that the config wasn't valid
            if len(configNotFound) > 0:
                msgBox = QtGui.QMessageBox(self)
                msgBox.setIcon(QtGui.QMessageBox.Information)
                msgBox.setWindowTitle('Loaded Configuration Invalid')
                message = '''\r\n The loaded configuration file cannot be properly loaded with the servers and devices currently connected to the computer. The following 
                                connections cannot be made: \n''' + configNotFound
                msgBox.setText(message)
                msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
                msgBox.setStyleSheet("background-color:black; color:rgb(168,168,168)")
                msgBox.exec_()
            
            self.sendDeviceInfo()
            
        except Exception as inst:
            print 'check Loaded', inst
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print 'line num ', exc_tb.tb_lineno
            
    @inlineCallbacks
    def sendDeviceInfo(self):
        try:
            #Select the proper devices for the system general devices
            if self.deviceDictionary['devices']['system']['magnet supply'] == 'IPS 120 Power Supply':
                yield self.deviceDictionary['servers']['remote']['ips120'].select_device(self.deviceDictionary['devices']['system']['specific supply'])
            elif self.deviceDictionary['devices']['system']['magnet supply'] == 'Toellner Power Supply':
                yield self.deviceDictionary['servers']['local']['dac_adc'].select_device(self.deviceDictionary['devices']['system']['specific supply'])
            
            self.newDeviceInfo.emit(self.deviceDictionary)
        except Exception as inst:
            print 'check Loaded', inst
            print 'on line: ', sys.exc_traceback.tb_lineno
            
    def setDefaultConfiguration(self):
        f = open(self.fileName,'w')
        f.write(self.configFileName)
        f.close()
        print 'Devices: ', self.deviceDictionary['devices']

    def saveConfigurationInfo(self):
        file = str(QtGui.QFileDialog.getSaveFileName(self, directory = path, filter = "Text files (*.txt)"))
        f = open(file,'w')
        message  = ''
        #For now, only adding devices into the configuration file
        for section, dev_list in self.deviceDictionary['devices'].iteritems():
            message = message + section + ';'
            for dev, dev_name in dev_list.iteritems():
                message = message + str(dev) + ',' + str(dev_name) + ';'
            message = message[:-1] + '\n'
        
        #Add channel info here eventually
        f.write(message)
        f.close()
            
        self.configFileName = file.split('/')[-1]
        self.label_currentConfigFile.setText(self.configFileName)
        
    # Below function is not necessary, but is often useful. Yielding it will provide an asynchronous 
    # delay that allows other labrad / pyqt methods to run
    def sleep(self,secs):
        """Asynchronous compatible sleep command. Sleeps for given time in seconds, but allows
        other operations to be done elsewhere while paused."""
        d = Deferred()
        self.reactor.callLater(secs,d.callback,'Sleeping')
        return d