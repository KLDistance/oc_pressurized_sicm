import numpy as np
import pymmcore

class CameraObj:
    def __init__(self, cfg_fp):
        self.mmc = pymmcore.CMMCore()
        self.mmc.loadSystemConfiguration(cfg_fp)
        self.mmc.setProperty('TIS_DCAM', 'Device Flip_V', 'On')
        #self.mmc.setProperty('TIS_DCAM', 'Exposure Auto', 'On')
        self.mmc.setProperty('TIS_DCAM', 'Exposure Auto', 'Off')
        self.mmc.setProperty('TIS_DCAM', 'Exposure', 2.1)
        self.mmc.setProperty('TIS_DCAM', 'Property Gain_Auto', 'Off')
        self.mmc.setProperty('TIS_DCAM', 'Property Gain', 64)
        self.last_exposure_val = 0.0
    def set_denoise_level(self, denoise_level):
        self.mmc.setProperty('TIS_DCAM', 'DeNoise', denoise_level)
    def snap(self, exposure):
        if self.last_exposure_val != exposure:
            self.mmc.setProperty('TIS_DCAM', 'Exposure', exposure)
            self.last_exposure_val = exposure
        self.mmc.snapImage()
        img_data = self.mmc.getImage()
        return img_data
    def denoised_snap(self, iteration):
        #self.mmc.setProperty('TIS_DCAM', 'Exposure Auto', 'Off')
        #self.mmc.setProperty('TIS_DCAM', 'Exposure', self.last_exposure_val)
        img_buf = []
        for iter in range(iteration):
            self.mmc.snapImage()
            img_buf.append(self.mmc.getImage())
        img_data = np.mean(np.array(img_buf), axis=0).astype(int)
        #self.mmc.setProperty('TIS_DCAM', 'Exposure Auto', 'On')
        return img_data.tolist()

def camera_init(cfg_fp):
    camera_obj = CameraObj(cfg_fp)
    return camera_obj

def camera_set_denoise_level(camera_obj, denoise_level):
    camera_obj.set_denoise_level(denoise_level)

def camera_snap_image(camera_obj, exposure):
    return camera_obj.snap(exposure)

def camera_snap_denoised_image(camera_obj, iteration):
    return camera_obj.denoised_snap(iteration)


