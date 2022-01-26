from sardana.pool.controller import TwoDController, Referable
from tango import Device, DeviceProxy, DevFailed


class MOENCHTangoTwoDController(TwoDController, Referable):
    ctrl_properties = {
        "controlMOENCHTangoFQDN": {
            Type: str,
            Description: "The FQDN of the PI-MTE tango DS",
            DefaultValue: "rsxs/moenchControl/bchip286",
        },
        "acquireMOENCHTangoFQDN": {
            Type: str,
            Description: "The FQDN of the PI-MTE tango DS",
            DefaultValue: "rsxs/moenchAcquire/bchip286",
        },
        "PointNb": {
            Type: int,
            Description: "pointNb of the scan",
            Access: DataAccess.ReadWrite,
            FGet: "getPointNb",
            FSet: "setPointNb",
        },
        "FileName": {
            Type: str,
            Description: "file name of image",
            Access: DataAccess.ReadWrite,
            FGet: "getFileName",
            FSet: "setFileName",
        },
    }
    axis_attributes = {
        "SavingEnabled": {
            Type: bool,
            FGet: "isSavingEnabled",
            FSet: "setSavingEnabled",
            Description: (
                "Enable/disable saving of images in HDF5 files."
                " Use with care in high demanding (fast)"
                " acquisitions. Trying to save at high rate may"
                " hang the acquisition process."
            ),
        }
    }

    def __init__(self, inst, props, *args, **kwargs):
        """Constructor"""
        TwoDController.__init__(self, inst, props, *args, **kwargs)
        print("MOENCH Tango Initialization ...")
        self.control_device = DeviceProxy(self.controlMOENCHTangoFQDN)
        self.acquire_device = DeviceProxy(self.acquireMOENCHTangoFQDN)
        print("Ping devices...")
        self.control_device.ping()
        self.acquire_device.ping()
        print("SUCCESS")
        self._axes = {}

    def AddDevice(self, axis):
        self._axes[axis] = {}

    def DeleteDevice(self, axis):
        self._axes.pop(axis)

    def ReadOne(self, axis):
        """Get the specified counter value"""
        # print(self._SavingEnabled)
        # print('Image saved to: {:s}'.format(self.proxy.LastSavedImage))
        return self.proxy.image

    def RefOne(self, axis):
        return self.proxy.LastSavedImage

    def SetAxisPar(self, axis, parameter, value):
        #        if parameter == "value_ref_pattern":
        #            print('value_ref_pattern ' + str(value))
        #        elif parameter == "value_ref_enabled":
        #            print('value_ref_enabled ' + str(value))
        #            self.setSavingEnabled(axis, value)
        pass

    def StateOne(self, axis):
        """Get the specified counter state"""
        #
        return self.control_device.detector_status, "Counter is acquiring or not"

    def PrepareOne(self, axis, value, repetitions, latency, nb_starts):
        # set exporsure time of GE cam
        self.proxy.ExposureTime = float(value)

    def LoadOne(self, axis, value, repetitions, latency):
        pass

    def StartOne(self, axis, value=None):
        """acquire the specified counter"""
        self.acquire_device.acquire()
        return

    def StopOne(self, axis):
        """Stop the specified counter"""
        self.control_device.rx_stop()
        # self.proxy.StopAcq()

    def AbortOne(self, axis):
        """Abort the specified counter"""
        self.control_device.rx_stop()
        # self.proxy.StopAcq()

    def isSavingEnabled(self, axis):
        return self.control_device.filewrite

    def setSavingEnabled(self, axis, value):
        self.control_device.filewrite = bool(value)
