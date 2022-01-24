from sardana.pool.controller import TwoDController, Referable


class MOENCHTangoTwoDController(TwoDController, Referable):

    ctrl_properties = {
        "tangoFQDN": {
            Type: str,
            Description: "The FQDN of the PI-MTE tango DS",
            DefaultValue: "domain/family/member",
        }
    }

    def __init__(self, inst, props, *args, **kwargs):
        """Constructor"""
        TwoDController.__init__(self, inst, props, *args, **kwargs)
        print("MOENCH Tango Initialization ...")
        self.proxy = DeviceProxy(self.tangoFQDN)
        print("SUCCESS")
        self._axes = {}
