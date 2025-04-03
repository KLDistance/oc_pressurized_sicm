# Optically-correlated Scanning Ion Conductance Microscopy

> Wang, Y.; Shashishekar, M.; Spence, D. M.; Baker L. A., Subcellular Mechanical Imaging of Erythrocytes with Optically Correlated Scanning Ion Conductance Microscopy. ACS Meas. Sci. Au, 2025, DOI: [10.1021/acsmeasuresciau.5c00019](https://pubs.acs.org/doi/10.1021/acsmeasuresciau.5c00019)

## Software Prerequisites

1. LabVIEW 2024 Q1 64-bit (or newer), including FPGA Module for R series FPGA, Real-time Module.
2. Python 3.9 32-bit and 64-bit

## Module Usage

1. Open oc_pressurized_sicm/HoppingSICM_v2.lvproj LabVIEW Main menu.
2. Open oc_pressurized_sicm/HostCamera/HostCameraManager.vi for getting live-mode views from inverted optical microscope camera. This needs to be on while doing hopping-mode imaging.
3. Open oc_pressurized_sicm/Motor/Motor_Control.vi for z motor position control. This is used for manual operandos such as submerging pipette in solution, or retracting pipette away from surface.
4. Open oc_pressurized_sicm/Host_AutoApproach_v1.vi for pipette auto approach. This is used for fast pipette approach to make pipette extended state within z piezo traveling range.
5. Open oc_pressurized_sicm/HostHoppingScan/HostHoppingScan_v2_BoostedMultiRegion for hopping-mode pressurized SICM imaging.
