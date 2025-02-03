import os, sys
from ctypes import *
from msl.loadlib import Server32

class MotorServer(Server32):
    def __init__(self, host, port, **kwargs):
        super(MotorServer, self).__init__(os.path.dirname(__file__)+'/MMC.dll', 'windll', host, port)
    def mmcfunc_mmc_com_open(self, com_port, baud_rate):
        return self.lib.MMC_COM_open(com_port, baud_rate)
    def mmcfunc_mmc_com_close(self):
        return self.lib.MMC_COM_close()
    def mmcfunc_mmc_set_device(self, device):
        return self.lib.MMC_setDevice(device)
    def mmcfunc_mmc_send_command(self, command):
        return self.lib.MMC_sendCommand(command)
    def mmcfunc_mmc_get_position(self):
        return self.lib.MMC_getPos()
    def mmcfunc_mmc_move_relatively(self, axis, cnt):
        return self.lib.MMC_moveR(axis, cnt)
    def mmcfunc_mmc_is_moving(self):
        return self.lib.MDC_moving()