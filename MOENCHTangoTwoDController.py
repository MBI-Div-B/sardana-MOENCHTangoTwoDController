# from sardana import DataAccess
from sardana.pool.controller import TwoDController, Referable, Type, Access, Description
import tango
from tango import DeviceProxy, DevState
import numpy as np
from enum import Enum, IntEnum
from time import sleep

# ReadOnly = DataAccess.ReadOnly
# ReadWrite = DataAccess.ReadWrite


class MOENCHTangoTwoDController(TwoDController, Referable):
    "This class is the Tango Sardana Two D controller for the MOENCH PSI"
    # ctrl_properties = {
    #     "controlMOENCHTangoFQDN": {
    #         Type: str,
    #         Description: "The FQDN of the MOENCH tango DS",
    #         DefaultValue: "rsxs/moenchControl/bchip286",
    #     },
    # }

    # class FrameMode(IntEnum):
    #     # hence detectormode in slsdet uses strings (not enums) need to be converted to strings
    #     # RAW = "raw"
    #     # FRAME = "frame"
    #     # PEDESTAL = "pedestal"
    #     # NEWPEDESTAL = "newPedestal"
    #     # NO_FRAME_MODE = "noFrameMode"
    #     RAW = 0
    #     FRAME = 1
    #     PEDESTAL = 2
    #     NEWPEDESTAL = 3
    #     NO_FRAME_MODE = 4

    # class DetectorMode(IntEnum):
    #     # hence detectormode in slsdet uses strings (not enums) need to be converted to strings
    #     # COUNTING = "counting"
    #     # ANALOG = "analog"
    #     # INTERPOLATING = "interpolating"
    #     # NO_DETECTOR_MODE = "noDetectorMode"
    #     COUNTING = 0
    #     ANALOG = 1
    #     INTERPOLATING = 2
    #     NO_DETECTOR_MODE = 3

    class TimingMode(IntEnum):
        # the values are the same as in slsdet.timingMode so no bidict table is required
        AUTO_TIMING = 0
        TRIGGER_EXPOSURE = 1

    # class DetectorSettings(IntEnum):
    #     # [G1_HIGHGAIN, G1_LOWGAIN, G2_HIGHCAP_HIGHGAIN, G2_HIGHCAP_LOWGAIN, G2_LOWCAP_HIGHGAIN, G2_LOWCAP_LOWGAIN, G4_HIGHGAIN, G4_LOWGAIN]
    #     G1_HIGHGAIN = 0
    #     G1_LOWGAIN = 1
    #     G2_HIGHCAP_HIGHGAIN = 2
    #     G2_HIGHCAP_LOWGAIN = 3
    #     G2_LOWCAP_HIGHGAIN = 4
    #     G2_LOWCAP_LOWGAIN = 5
    #     G4_HIGHGAIN = 6
    #     G4_LOWGAIN = 7

    """
    here are presented only key features and most significant parameters which are expected
    to be changed during the normal measurements

    as an example I took:
    https://github.com/desy-fsec/sardana-controllers/blob/master/python/twod/Pilatus.py
    """

    # axis_attributes = {
    #     "exposure": {
    #         Type: tango.DevFloat,
    #         Access: ReadWrite,
    #         Description: "exposure of each frame in s",
    #     },
    #     "delay": {
    #         Type: tango.DevFloat,
    #         Access: ReadWrite,
    #         Description: "delay after each trigger in s",
    #     },
    #     "timing_mode": {
    #         Type: tango.DevEnum,
    #         Access: ReadWrite,
    #         Description: "AUTO/TRIGGER exposure mode",
    #     },
    #     "triggers": {
    #         Type: tango.DevInt,
    #         Access: ReadWrite,
    #         Description: "expect this amount of triggers in the acquire session",
    #     },
    #     "filename": {
    #         Type: tango.DevString,
    #         Access: ReadWrite,
    #         Description: "filename prefix",
    #     },
    #     "filepath": {
    #         Type: tango.DevString,
    #         Access: ReadWrite,
    #         Description: "path to save files",
    #     },
    #     "fileindex": {Type: tango.DevInt, Access: ReadWrite, Description: "index "},
    #     "frames": {
    #         Type: tango.DevInt,
    #         Access: ReadWrite,
    #         Description: "amount of frames for each trigger to acquire",
    #     },
    #     "framemode": {
    #         Type: tango.DevEnum,
    #         Access: ReadWrite,
    #         Description: "framemode of detector [RAW, FRAME, PEDESTAL, NEWPEDESTAL]",
    #     },
    #     "detectormode": {
    #         Type: tango.DevEnum,
    #         Access: ReadWrite,
    #         Description: "detectorMode [COUNTING, ANALOG, INTERPOLATING]",
    #     },
    #     "highvoltage": {
    #         Type: tango.DevInt,
    #         Access: ReadWrite,
    #         Description: "bias voltage on sensor",
    #     },
    #     "period": {
    #         Type: tango.DevFloat,
    #         Access: ReadWrite,
    #         Description: "period for auto timing mode, need be at least exposure + 250us",
    #     },
    #     "gain_settings": {
    #         Type: tango.DevEnum,
    #         Access: ReadWrite,
    #         Description: "[G1_HIGHGAIN, G1_LOWGAIN, G2_HIGHCAP_HIGHGAIN, G2_HIGHCAP_LOWGAIN, G2_LOWCAP_HIGHGAIN, G2_LOWCAP_LOWGAIN, G4_HIGHGAIN, G4_LOWGAIN]",
    #     },
    #     "tiff_fullpath_next": {
    #         Type: tango.DevString,
    #         Access: ReadWrite,
    #         Description: "full path of the next capture",
    #     },
    #     "tiff_fullpath_last": {
    #         Type: tango.DevString,
    #         Access: ReadWrite,
    #         Description: "full path of the last capture",
    #     },
    #     "sum_image_last": {
    #         Type: ((tango.DevLong,),),
    #         Access: ReadOnly,
    #         Description: "last summarized 400x400 image from detector",
    #     },
    # }

    def __init__(self, inst, props, *args, **kwargs):
        """Constructor"""
        TwoDController.__init__(self, inst, props, *args, **kwargs)
        print("MOENCHTangoTwoDController Initialization ...")
        self.control_device = DeviceProxy("rsxs/moenchControl/bchip286")
        print("Ping device...")
        print("SUCCESS")
        self._axes = {}

    def AddDevice(self, axis):
        self._axes[axis] = {}

    def DeleteDevice(self, axis):
        self._axes.pop(axis)

    def ReadOne(self, axis):
        """Get the specified counter value"""
        print(
            f"Called ReadOne with the last path: {self.control_device.tiff_fullpath_last}"
        )
        return self.control_device.sum_image_last

    def RefOne(self, axis):
        print(
            f"Called RefOne with the last path: {self.control_device.tiff_fullpath_last}"
        )
        return self.control_device.tiff_fullpath_last

    def SetAxisPar(self, axis, parameter, value):
        pass

    def StateOne(self, axis):
        """Get the specified counter state"""
        acquire_state = self.control_device.state()
        if acquire_state == DevState.ON:
            tup = (acquire_state, "Camera ready")
        elif acquire_state == DevState.FAULT:
            tup = (acquire_state, "Camera in FAULT state")
        elif acquire_state == DevState.STANDBY:
            tup = (DevState.MOVING, "Camera is waiting for trigger")
        elif acquire_state == DevState.RUNNING:
            # according to https://www.sardana-controls.org/devel/howto_controllers/howto_0dcontroller.html?highlight=stateone need to be set to MOVING while acquiring
            tup = (DevState.MOVING, "Camera acquiring")
        print(f"Called StateOne {tup}")
        return tup

    def PrepareOne(self, axis, value, repetitions, latency, nb_starts):
        """
        value is a exposure in sec
        we need to set only up amount of triggers, TRIGGER_EXPOSURE mode and only 1 frame per trigger
        detectormode will not be changed
        """
        sleep(0.3)
        triggers = int(value * 100)
        print("Set trigger to TRIGGER_EXPOSURE")
        self.control_device.timing_mode = self.TimingMode.TRIGGER_EXPOSURE
        print("Set frames per trigger to 1")
        self.control_device.frames = 1  # crashes here
        print(f"Set triggers to {triggers}")
        self.control_device.triggers = triggers

    def LoadOne(self, axis, value, repetitions, latency):
        pass

    def StartOne(self, axis, value=None):
        """acquire the specified counter"""
        print("Called StartOne")
        self.control_device.start_acquire()
        sleep(0.75)

    def StopOne(self, axis):
        """Stop the specified counter"""
        print("Called StopOne")
        self.control_device.stop_acquire()

    def AbortOne(self, axis):
        """Abort the specified counter"""
        print("Called AbortOne")
        self.control_device.stop_acquire()

    def GetAxisPar(self, axis, par):
        print("Called GetAxisPar")
        if par == "shape":
            return [400, 400]
