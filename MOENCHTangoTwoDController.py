from sardana.pool.controller import TwoDController, Referable
from tango import DeviceProxy, DevState
import numpy as np


class MOENCHTangoTwoDController(TwoDController, Referable):
    "This class is the Tango Sardana Two D controller for the MOENCH PSI"
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
        # TODO: unclear what need to return in case of reference
        return np.zeros(400, 400)

    def RefOne(self, axis):
        return self.control_device.tiff_fullpath_last

    def SetAxisPar(self, axis, parameter, value):
        pass

    def StateOne(self, axis):
        """Get the specified counter state"""
        acquire_state = self.acquire_device.state
        if acquire_state == DevState.ON:
            tup = (acquire_state, "Camera ready")
        elif acquire_state == DevState.FAULT:
            tup = (acquire_state, "Camera in FAULT state")
        elif acquire_state == DevState.STANDBY:
            acquire_state = DevState.MOVING
            tup = (acquire_state, "Camera is waiting for trigger")
        elif acquire_state == DevState.RUNNING:
            # according to https://www.sardana-controls.org/devel/howto_controllers/howto_0dcontroller.html?highlight=stateone need to be set to MOVING while acquiring
            acquire_state = DevState.MOVING
            tup = (acquire_state, "Camera acquiring")
        return acquire_state, "Counter is acquiring or not"

    def PrepareOne(self, axis, value, repetitions, latency, nb_starts):
        # set exporsure time of GE cam
        self.control_device.exposure = float(value)

    def LoadOne(self, axis, value, repetitions, latency):
        pass

    def StartOne(self, axis, value=None):
        """acquire the specified counter"""
        self.acquire_device.acquire()
        return

    def StopOne(self, axis):
        """Stop the specified counter"""
        # FIXME: pending https://github.com/MBI-Div-B/pytango-moenchDetector/issues/13
        pass

    def AbortOne(self, axis):
        """Abort the specified counter"""
        # FIXME: pending https://github.com/MBI-Div-B/pytango-moenchDetector/issues/13
        pass

    def isSavingEnabled(self, axis):
        # TODO: check if a zmqfreq turn off is required
        return self.control_device.filewrite

    def setSavingEnabled(self, axis, value):
        self.control_device.filewrite = bool(value)
