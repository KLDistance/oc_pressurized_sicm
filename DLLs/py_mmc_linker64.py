import os, sys
from msl.loadlib import Client64
from ctypes import *

class MotorClient(Client64):
    def __init__(self):
        super(MotorClient, self).__init__(module32='py_mmc_linker32')
    def mmcfunc_mmc_com_open(self, com_port, baud_rate):
        return self.request32('mmcfunc_mmc_com_open', com_port, baud_rate)
    def mmcfunc_mmc_com_close(self):
        return self.request32('mmcfunc_mmc_com_close')
    def mmcfunc_mmc_set_device(self, device):
        return self.request32('mmcfunc_mmc_set_device', device)
    def mmcfunc_mmc_send_command(self, command):
        return self.request32('mmcfunc_mmc_send_command', command)
    def mmcfunc_mmc_get_position(self):
        return self.request32('mmcfunc_mmc_get_position')
    def mmcfunc_mmc_move_relatively(self, axis, cnt):
        return self.request32('mmcfunc_mmc_move_relatively', axis, cnt)
    def mmcfunc_mmc_is_moving(self):
        return self.request32('mmcfunc_mmc_is_moving')

def init_obj():
    return MotorClient()

def motor_open(motor_obj, com_port, baud_rate):
    motor_obj.mmcfunc_mmc_com_open(com_port, baud_rate)

def motor_close(motor_obj):
    motor_obj.mmcfunc_mmc_com_close()

def motor_set_device(motor_obj, device):
    motor_obj.mmcfunc_mmc_set_device(device)

def motor_send_command(motor_obj, command):
    motor_obj.mmcfunc_mmc_send_command(command.encode(encoding='utf-8'))

def motor_get_position(motor_obj):
    return motor_obj.mmcfunc_mmc_get_position()

def motor_move_relatively(motor_obj, axis, cnt):
    motor_obj.mmcfunc_mmc_move_relatively(axis, cnt)

def motor_is_moving(motor_obj):
    return motor_obj.mmcfunc_mmc_is_moving()