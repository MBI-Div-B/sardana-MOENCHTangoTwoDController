# from sardana import DataAccess
from sardana.pool.controller import TwoDController
from tango import DeviceProxy, DevState
import numpy as np
from enum import Enum, IntEnum
from time import sleep

from sardana import State


# ReadOnly = DataAccess.ReadOnly
# ReadWrite = DataAccess.ReadWrite


class MOENCHZMQTangoTwoDController(TwoDController):
    "This class is the Tango Sardana Two D controller for the MOENCH detector using the own zmq processing server"

    class TimingMode(IntEnum):
        # the values are the same as in slsdet.timingMode so no bidict table is required
        AUTO_TIMING = 0
        TRIGGER_EXPOSURE = 1

    def __init__(self, inst, props, *args, **kwargs):
        """Constructor"""
        TwoDController.__init__(self, inst, props, *args, **kwargs)
        self._log.debug("MOENCHZMQTangoTwoDController Initialization ...")
        self.control_device = DeviceProxy("rsxs/moenchControl/bchip286")
        # self._log.debug(f"Control device state is {self.control_device.state()}")
        self.zmq_server = DeviceProxy("rsxs/moenchZmqServer/bchip286")
        # self._log.debug(f"ZMQ server state is {self.zmq_server.state()}")
        self.REPETITION_RATE = 100  # in Hz
        self.stored_triggers = 1
        self.stored_frames = 1
        self._axes = {}

    def AddDevice(self, axis):
        self._axes[axis] = {}

    def DeleteDevice(self, axis):
        self._axes.pop(axis)

    def ReadOne(self, axis):
        self._log.debug(f"Called ReadOne on axis {axis}")
        if axis == 0:
            return self.zmq_server.analog_img
        elif axis == 1:
            return self.zmq_server.analog_img_pumped
        elif axis == 2:
            return self.zmq_server.threshold_img
        elif axis == 3:
            return self.zmq_server.threshold_img_pumped
        elif axis == 4:
            return self.zmq_server.counting_img
        elif axis == 5:
            return self.zmq_server.counting_img_pumped

    def SetAxisPar(self, axis, parameter, value):
        pass

    # self.control_device.detector_status corresponds to
    # status_dict = {
    #     runStatus.IDLE: DevState.ON, -> ready
    #     runStatus.ERROR: DevState.FAULT,
    #     runStatus.WAITING: DevState.STANDBY, -> waiting for triggers
    #     runStatus.RUN_FINISHED: DevState.ON,
    #     runStatus.TRANSMITTING: DevState.RUNNING,
    #     runStatus.RUNNING: DevState.RUNNING, -> acquiring
    #     runStatus.STOPPED: DevState.ON,
    # }

    # zmq server corresponds to
    # if acquiring -> DevState.RUNNING
    # if ready -> DevState.ON

    def StateAll(self):
        self._log.debug("Called StateAll")

    def StateOne(self, axis):
        """Get the specified counter state"""
        self._log.debug(f"Called StateOne on axis {axis}")
        detector_state = self.control_device.detector_status
        zmq_server_state = self.zmq_server.state()

        self._log.debug(f"detector state: {detector_state}")
        self._log.debug(f"zmq server state: {zmq_server_state}")
        if detector_state == DevState.ON and zmq_server_state == DevState.ON:
            tup = (DevState.ON, "Camera ready")
        elif detector_state == DevState.FAULT or zmq_server_state == DevState.FAULT:
            tup = (DevState.FAULT, "Camera and/or zmq server in FAULT state")
        elif (
            detector_state == DevState.STANDBY and zmq_server_state == DevState.RUNNING
        ):
            tup = (DevState.MOVING, "Camera is waiting for trigger")
        elif detector_state == DevState.MOVING or zmq_server_state == DevState.RUNNING:
            tup = (
                DevState.MOVING,
                "Camera acquiring and/or zmq server process the data",
            )
        self._log.debug(f"tup = {tup}")
        return tup

    def PrepareOne(self, axis, value, repetitions, latency, nb_starts):
        """
        value is a exposure in sec
        we need to set only up amount of triggers, TRIGGER_EXPOSURE mode and only 1 frame per trigger
        detectormode will not be changed
        """
        self._log.debug(f"Called PrepareOne on axis {axis}")
        self.stored_triggers = int(value * self.REPETITION_RATE)
        self._log.debug(f"Stored {self.stored_triggers} triggers")
        self._log.debug(f"Leaving PrepareOne on axis {axis}")

    def PreStartAll(self):
        self._log.debug(f"Called PreStartAll")
        frames = self.stored_frames
        self._log.debug(f"Set frames per trigger on the detector to {frames}")
        self.control_device.frames = frames
        triggers = self.stored_triggers
        self._log.debug(f"Set triggers  on the detector to {triggers}")
        self.control_device.triggers = triggers
        self._log.debug(f"Set timing mode on the detector to TRIGGER_EXPOSURE")
        self.control_device.timing_mode = self.TimingMode.TRIGGER_EXPOSURE
        self._log.debug(f"Leaving PreStartAll")

    def LoadOne(self, axis, value, repetitions, latency):
        self._log.debug(f"Called LoadOne on axis {axis}")
        pass

    def LoadAll(self):
        self._log.debug("Called LoadAll")
        pass

    def StartOne(self, axis, value=None):
        """acquire the specified counter"""
        self._log.debug("Called StartOne")

    def StartAll(self):
        self._log.debug("Called StartAll")
        self.control_device.start_acquire()
        # some time is required for the hardware detector to be ready
        self._log.debug("Leaving StartOne")

    def StopOne(self, axis):
        """Stop the specified counter"""
        if axis == 0:
            self._log.debug("Called StopOne")
            self.control_device.stop_acquire()

    def AbortOne(self, axis):
        """Abort the specified counter"""
        self._log.debug(f"Called AbortOne on axis {axis}")

    def AbortAll(self):
        self._log.debug(f"Called AbortAll")
        self.control_device.stop_acquire()
        self.zmq_server.abort_receiver()

    def GetAxisPar(self, axis, par):
        self._log.debug("Called GetAxisPar")
        if par == "shape":
            return [400, 400]
