#=============================================================================
#
# file :        LimaTacoCCDs.py
#
# description : Python source for the LimaCCDs and its commands. 
#                The class is derived from Device. It represents the
#                CORBA servant object which will be accessed from the
#                network. All commands which can be executed on the
#         LimaTacoCCDs are implemented in this file.
#
# project :    TANGO Device Server
#
# copyleft :    European Synchrotron Radiation Facility
#        BP 220, Grenoble 38043
#        FRANCE
#
#=============================================================================
#        This file is generated by seb
#
#      (c) - BLISS - ESRF
#=============================================================================
#

import sys,os
import PyTango
import weakref

from Lima import Core

import plugins
import camera

class LimaCCDs(PyTango.Device_4Impl) :

    Core.DEB_CLASS(Core.DebModApplication, 'LimaCCDs')
    
#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    def __init__(self,*args) :
        PyTango.Device_4Impl.__init__(self,*args)
        self.__className2deviceName = {}
        self.init_device()
        self.__lima_control = None
        
#------------------------------------------------------------------
#    Device destructor
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def delete_device(self) :
        try:
            m = __import__('camera.%s' % (self.LimaCameraType),None,None,'camera.%s' % (self.LimaCameraType))
        except ImportError:
            pass
        else:
            m.close_interface()

#------------------------------------------------------------------
#    Device initialization
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def init_device(self) :
        self.set_state(PyTango.DevState.ON)
        self.get_device_properties(self.get_device_class())
        #get sub devices
        fullpathExecName = sys.argv[0]
        execName = os.path.split(fullpathExecName)[-1]
        execName = os.path.splitext(execName)[0]
        personalName = '/'.join([execName,sys.argv[1]])
        dataBase = PyTango.Database()
        result = dataBase.get_device_class_list(personalName)
        for i in range(len(result.value_string) / 2) :
            class_name = result.value_string[i * 2]
            deviceName = result.value_string[i * 2 + 1]
            self.__className2deviceName[deviceName] = class_name
            
        try:
            m = __import__('camera.%s' % (self.LimaCameraType),None,None,'camera.%s' % (self.LimaCameraType))
        except ImportError:
            import traceback
            traceback.print_exc()
            self.set_state(PyTango.DevState.FAULT)
        else:
            properties = {}
            try:
                specificClass,specificDevice = m.get_tango_specific_class_n_device()
            except AttributeError: pass
            else:
		Core.DebParams.setTypeFlags(0)
                util = PyTango.Util.instance()
#                if specificClass and specificDevice:
#                    util.create_device(specificClass,specificDevice)
                #get properties for this device

                deviceName = self.__className2deviceName.get(specificDevice.__name__,None)
                if deviceName:
                    propertiesNames = dataBase.get_device_property_list(deviceName,"*")
                    for pName in propertiesNames.value_string:
                        key,value = dataBase.get_device_property(deviceName,pName).popitem()
                        if len(value) == 1:
                            value = value[0]
                        properties[key] = value
            
            self.__control = m.get_control(**properties)
            _set_control_ref(weakref.ref(self.__control))

        try:
            nb_thread = int(self.NbProcessingThread)
        except ValueError:
            pass
        else:
            Core.Processlib.PoolThreadMgr.get().setNumberOfThread(nb_thread)
            
            
        self.__ShutterMode = {'MANUAL': Core.ShutterManual, \
                              'AUTO_FRAME': Core.ShutterAutoFrame,\
                              'AUTO_SEQUENCE': Core.ShutterAutoSequence}			      
        self.__AcqMode = {'SINGLE': Core.Single, \
                          'CONCATENATION': Core.Concatenation,\
                          'ACCUMULATION': Core.Accumulation}

#==================================================================
# 
# Some Utils
#
#==================================================================

    def __getDictKey(self,dict, value):
        try:
            ind = dict.values().index(value)                            
        except ValueError:
            return None
        return dict.keys()[ind]

    def __getDictValue(self,dict, key):
        try:
            value = dict[key.upper()]
        except KeyError:
            return None
        return value

#==================================================================
#
#    LimaCCDs read/write attribute methods
#
#==================================================================

    ## @brief Read the Lima Type
    #
    @Core.DEB_MEMBER_FUNCT
    def read_lima_type(self,attr) :        
        value  = self.LimaCameraType	
        attr.set_value(value)

    ## @brief Read the Camera Type
    #
    @Core.DEB_MEMBER_FUNCT
    def read_camera_type(self,attr) :        
        interface = self.__control.interface()
	det_info = interface.getHwCtrlObj(Core.HwCap.DetInfo)
	value = det_info.getDetectorType()
        attr.set_value(value)

    ## @brief Read the Camera Model
    #
    @Core.DEB_MEMBER_FUNCT
    def read_camera_model(self,attr) :        
	interface = self.__control.interface()
	det_info = interface.getHwCtrlObj(Core.HwCap.DetInfo)
	value = det_info.getDetectorModel() 
	attr.set_value(value)

    ## @brief Read maximum accumulation exposure time
    #
    @Core.DEB_MEMBER_FUNCT
    def read_acc_max_expotime(self,attr) :        
	acq = self.__control.acquisition()

        value = acq.getAccMaxExpoTime()
	if value is None: value = -1
	
        attr.set_value(value)

    ## @brief Write the accumulation max exposure time
    #
    @Core.DEB_MEMBER_FUNCT
    def write_acc_max_expotime(self,attr) :
        data = []
        attr.get_write_value(data)
	acq = self.__control.acquisition()
        acq.setAccMaxExpoTime(*data)

    ## @brief Read calculated accumulation exposure time
    #
    @Core.DEB_MEMBER_FUNCT
    def read_acc_expotime(self,attr) :        
	acq = self.__control.acquisition()

        value = acq.getAccExpoTime()
	if value is None: value = -1
	
        attr.set_value(value)
	
    ## @brief Read calculated accumulation number of frames
    #
    @Core.DEB_MEMBER_FUNCT
    def read_acc_nb_frames(self,attr) :        
	acq = self.__control.acquisition()
        value = acq.getAccNbFrames()
	if value is None: value = -1
	
        attr.set_value(value)
	
    ## @brief Read acquisition mode
    # Single, Concatenation or Accumulation
    #
    @Core.DEB_MEMBER_FUNCT
    def read_acq_mode(self,attr) :        
	acq = self.__control.acquisition()

	value = self.__getDictKey(self.__AcqMode,acq.getAcqMode())	
        if value is None: value = "NOT_SUPPORTED"
	
        attr.set_value(value)
		
    ## @brief Write Acquisition mode
    #Single, Concatenation, Accumulation
    #
    @Core.DEB_MEMBER_FUNCT
    def write_acq_mode(self,attr) :
        data = []
        attr.get_write_value(data)
	acq = self.__control.acquisition()
	
	mode = self.__getDictValue(self.__AcqMode,data[0].upper())
	if mode is None:
            PyTango.Except.throw_exception('WrongData',\
                                           'Wrong value %s: %s'%('shutter_mode',data[0].upper()),\
                                           'LimaCCD Class') 
                                     

        acq.setAcqMode(mode)

    ## @brief Read latency time 
    #
    @Core.DEB_MEMBER_FUNCT
    def read_latency_time(self,attr) :
        acq = self.__control.acquisition()

        value = acq.getLatencyTime()
        if value is None: value = -1

        attr.set_value(value)

    ## @brief Write Latency time 
    #
    @Core.DEB_MEMBER_FUNCT
    def write_latency_time(self,attr) :
        data = []
        attr.get_write_value(data)
        acq = self.__control.acquisition()

        acq.setLatencyTime(*data)

    ## @brief Read last image acquired
    #
    @Core.DEB_MEMBER_FUNCT
    def read_last_image_ready(self,attr) :
        status = self.__control.getStatus()
	img_counters= status.ImageCounters

        value = img_counters.LastImageReady
        if value is None: value = -1

        attr.set_value(value)

    ## @brief Read last image saved
    #
    @Core.DEB_MEMBER_FUNCT
    def read_last_image_saved(self,attr) :
        status = self.__control.getStatus()
        img_counters= status.ImageCounters

        value = img_counters.LastImageSaved
        if value is None: value = -1

        attr.set_value(value)

    ## @brief read write statistic
    #
    @Core.DEB_MEMBER_FUNCT
    def read_write_statistic(self,attr) :
        saving = self.__control.saving()
        stat = saving.getWriteTimeStatistic()
        if not len(stat) :
            attr.set_value([-1],len(1))
        else:
            attr.set_value(stat,len(stat))
	
    ## @brief Read current shutter mode 
    #
    @Core.DEB_MEMBER_FUNCT
    def read_shutter_mode(self,attr) :
        shutter = self.__control.shutter()

        value = self.__getDictKey(self.__ShutterMode,shutter.getMode())	
        if value is None: value = "NOT_SUPPORTED"

        attr.set_value(value)

    ## @brief Write current shutter mode
    #
    @Core.DEB_MEMBER_FUNCT
    def write_shutter_mode(self,attr) :
        data = []
        attr.get_write_value(data)
        
        mode = self.__getDictValue(self.__ShutterMode,data[0].upper())
	if mode is None:
            PyTango.Except.throw_exception('WrongData',\
                                           'Wrong value %s: %s'%('shutter_mode',data[0].upper()),\
                                           'LimaCCD Class') 

        
        shutter = self.__control.shutter()
        shutter.setMode(mode)

    ## @brief Read current shutter state 
    # True-Open, False-Close
    @Core.DEB_MEMBER_FUNCT
    def read_shutter_manual_state(self,attr) :
        shutter = self.__control.shutter()

	if shutter.hasCapability() and shutter.getModeList().count(Core.ShutterManual):
            if shutter.getState(): state = "OPEN"
            else: state = "CLOSED"
	else:
            state = "NO_MANUAL_MODE"
			
        attr.set_value(value)


    ## @brief Read shutter open time
    # True-Open, False-Close
    @Core.DEB_MEMBER_FUNCT
    def read_shutter_open_time(self,attr) :
        shutter = self.__control.shutter()

        value = shutter.getOpenTime()
        if value is None: value = -1

        attr.set_value(value)

    ## @brief Write shutter open time 
    # 
    @Core.DEB_MEMBER_FUNCT
    def write_shutter_open_time(self,attr) :
        data = []
        attr.get_write_value(data)
        shutter = self.__control.shutter()

        shutter.setOpenTime(*data)

    ## @brief Read shutter close time
    # in seconds
    @Core.DEB_MEMBER_FUNCT
    def read_shutter_close_time(self,attr) :
        shutter = self.__control.shutter()

        value = shutter.getCloseTime()
        if value is None: value = -1

        attr.set_value(value)

    ## @brief Write shutter close time 
    # in seconds
    @Core.DEB_MEMBER_FUNCT
    def write_shutter_close_time(self,attr) :
        data = []
        attr.get_write_value(data)
        shutter = self.__control.shutter()
        
        shutter.setCloseTime(*data)

#==================================================================
#
#    LimaCCDs command methods
#
#==================================================================
#------------------------------------------------------------------
#    getAttrStringValueList command:
#
#    Description: return a list of authorized values if any
#    argout: DevVarStringArray   
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def getAttrStringValueList(self, attr_name):
        valueList=[]
        if attr_name == "acq_mode":
            valueList = self.__AcqMode.keys()
        elif attr_name == 'shutter_mode':
            shutter = self.__control.shutter()
            if shutter.hasCapability():
                #Depending of the camera only a subset of the mode list can be supported
                values = shutter.getModeList()
                valueList = [self.__getDictKey(self.__ShutterMode,val) for val in values]
				
        return valueList
#------------------------------------------------------------------
#    closeShutterManual command:
#
#    Description: Close the shutter manual
#    argout: DevVoid  
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def closeShutterManual(self):

        shutter = self.__control.shutter()
        
	if shutter.hasCapability() and shutter.getModeList().count(Core.ShutterManual):
            shutter.setState(False)
            
#------------------------------------------------------------------
#    openShutterManual command:
#
#    Description: Open the shutter manual
#    argout: DevVoid  
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def openShutterManual(self):

        shutter = self.__control.shutter()
        
	if shutter.hasCapability() and shutter.getModeList().count(Core.ShutterManual):
            shutter.setState(True)

#------------------------------------------------------------------
#    setDebugFlags command:
#
#    Description: Get the current acquired frame number
#    argout: DevVarDoubleArray    
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def setDebugFlags(self, deb_flags):
        deb_flags &= 0xffffffff
        deb.Param('Setting debug flags: 0x%08x' % deb_flags)
        Core.DebParams.setTypeFlags((deb_flags   >> 16)  & 0xff)
        Core.DebParams.setModuleFlags((deb_flags >>  0)  & 0xffff)

        deb.Trace('FormatFlags: %s' % Core.DebParams.getFormatFlagsNameList())
        deb.Trace('TypeFlags:   %s' % Core.DebParams.getTypeFlagsNameList())
        deb.Trace('ModuleFlags: %s' % Core.DebParams.getModuleFlagsNameList())

#------------------------------------------------------------------
#    getDebugFlags command:
#
#    Description: Get the current acquired frame number
#    argout: DevVarDoubleArray    
#------------------------------------------------------------------
    @Core.DEB_MEMBER_FUNCT
    def getDebugFlags(self):
        deb.Trace('FormatFlags: %s' % Core.DebParams.getFormatFlagsNameList())
        deb.Trace('TypeFlags:   %s' % Core.DebParams.getTypeFlagsNameList())
        deb.Trace('ModuleFlags: %s' % Core.DebParams.getModuleFlagsNameList())
        
        deb_flags = (((Core.DebParams.getTypeFlags()    & 0xff)   << 16) |
                     ((Core.DebParams.getModuleFlags()  & 0xffff) <<  0))
        deb_flags &= 0xffffffff
        deb.Return('Getting debug flags: 0x%08x' % deb_flags)
        return deb_flags



#==================================================================
#
#    LimaTacoCCDsClass class definition
#
#==================================================================
class LimaCCDsClass(PyTango.DeviceClass) :
    #    Class Properties
    class_property_list = {
        }


    #    Device Properties
    device_property_list = {
        'LimaCameraType' :
        [PyTango.DevString,
         "Camera Plugin name",[]],
        'NbProcessingThread' :
        [PyTango.DevString,
         "Number of thread for processing",[2]],
        }

    #    Command definitions
    cmd_list = {
        'getDebugFlags':
        [[PyTango.DevVoid, ""],
         [PyTango.DevULong, "Debug flag in HEX format"]],
        'setDebugFlags':
        [[PyTango.DevULong, "Debug flag in HEX format"],
         [PyTango.DevVoid, ""]],
        'openShutterManual':
        [[PyTango.DevVoid, ""],
         [PyTango.DevVoid, ""]],
        'closeShutterManual':
        [[PyTango.DevVoid, ""],
         [PyTango.DevVoid, ""]],
        'getAttrStringValueList':
        [[PyTango.DevString, "Attribute name"],
         [PyTango.DevVarStringArray, "Authorized String value list"]],
	}
    
    #    Attribute definitions
    attr_list = {
        'lima_type':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ]],
        'camera_type':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ]],	 
        'camera_model':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ]],	 
        'acc_max_expotime':
        [[PyTango.DevDouble,
          PyTango.SCALAR,
          PyTango.READ_WRITE]],
        'acc_expotime':
        [[PyTango.DevDouble,
          PyTango.SCALAR,
          PyTango.READ]],	      	
        'latency_time':
        [[PyTango.DevDouble,
          PyTango.SCALAR,
          PyTango.READ_WRITE]],	      	
        'acc_nb_frames':
        [[PyTango.DevLong,
          PyTango.SCALAR,
          PyTango.READ]],	      	
        'acq_mode':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE]],
        'last_image_ready':
        [[PyTango.DevLong,
          PyTango.SCALAR,
          PyTango.READ]],
        'last_image_saved':
        [[PyTango.DevLong,
          PyTango.SCALAR,
          PyTango.READ]],
        'write_statistic':
        [[PyTango.DevDouble,
          PyTango.SPECTRUM,
          PyTango.READ,256]],
        'shutter_mode':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE]],
        'shutter_state':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ]],
        'shutter_open_time':
        [[PyTango.DevDouble,
          PyTango.SCALAR,
          PyTango.READ_WRITE]],
        'shutter_close_time':
        [[PyTango.DevDouble,
          PyTango.SCALAR,
          PyTango.READ_WRITE]],
        }

def declare_camera_n_commun_to_tango_world(util) :
    for module_name in camera.__all__:
        try:
            m = __import__('camera.%s' % (module_name),None,None,'camera.%s' % (module_name))
        except ImportError:
            continue
        else:
            try:
		func = getattr(m,'get_tango_specific_class_n_device')
                specificClass,specificDevice = func()
            except AttributeError:
                continue
            else:
                util.add_TgClass(specificClass,specificDevice,specificDevice.__name__)

    for module_name in plugins.__all__:
        try:
            m = __import__('plugins.%s' % (module_name),None,None,'plugins.%s' % (module_name))
        except ImportError:
	    import traceback
	    traceback.print_exc()
            continue
        else:
            try:
		func = getattr(m,'get_tango_specific_class_n_device')
            except AttributeError:
	        import traceback
	        traceback.print_exc()
                continue
            else:
                specificClass,specificDevice = func()
		util.add_TgClass(specificClass,specificDevice,specificDevice.__name__)

def _set_control_ref(ctrl_ref) :
    for module_name in plugins.__all__:
        try:
            m = __import__('plugins.%s' % (module_name),None,None,'plugins.%s' % (module_name))
        except ImportError:
            continue
	else:
	    try:
	        func = getattr(m,"set_control_ref")
		func(ctrl_ref)
	    except AttributeError:
		continue
	
#==================================================================
#
#    LimaCCDs class main method
#
#==================================================================
if __name__ == '__main__':
    try:
        py = PyTango.Util(sys.argv)
        py.add_TgClass(LimaCCDsClass,LimaCCDs,'LimaCCDs')
	try:
        	declare_camera_n_commun_to_tango_world(py)
	except:
		print 'SEB_EXP'
		import traceback
		traceback.print_exc()
        
        U = PyTango.Util.instance()
        U.server_init()
        U.server_run()

    except PyTango.DevFailed,e:
        print '-------> Received a DevFailed exception:',e
    except Exception,e:
        print '-------> An unforeseen exception occured....',e
