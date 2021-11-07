# Antibacklash plugin for Cura designed to seamlessly run script from https://www.thingiverse.com/thing:3060573 by Alex True aka SteakSndwich to compensate backlash.
# Put this script and Antibacklash.exe into "C:\Program Files\Ultimaker Cura <CURA_VERSION>\plugins\PostProcessingPlugin\scripts"
# Set it up in Cura -> Extensions -> Post Processing -> Modify G-Code ->  Add a script -> Antibacklash

import glob
import os
import shutil
import tempfile
from UM.Logger import Logger
from subprocess import Popen, PIPE
from ..Script import Script

class Antibacklash(Script):
    def getSettingDataString(self):
        return """{
            "name": "Antibacklash",
            "key": "Antibacklash",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "x_backlash": {
                    "label": "X",
                    "description": "X axis backlash",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0,
                    "minimum_value": "0",
                    "maximum_value": "2"
                },
                "y_backlash": {
                    "label": "Y",
                    "description": "Y axis backlash",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0,
                    "minimum_value": "0",
                    "maximum_value": "2"
                }
            }
        }"""

    def execute(self, data):
        temp_folder = tempfile.mkdtemp()
        Logger.log("d", "Start Antibacklash. Temp directory: " + temp_folder)

        x_backlash = self.getSettingValueByKey("x_backlash")
        y_backlash = self.getSettingValueByKey("y_backlash")

        if not os.path.exists(temp_folder):
            os.mkdir(temp_folder)

        f = open(temp_folder + "/temp.gcode", "w")
        f.write("G90\n")
        for line in data:
            f.write(line)
        f.close()

        exe = Popen([".\plugins\PostProcessingPlugin\scripts\Antibacklash.exe"], stdin=PIPE, cwd=temp_folder)
        inputs = str(x_backlash) + "\n" + str(y_backlash) + "\ntemp"
        exe.communicate(inputs.encode())

        processed_file = glob.glob(temp_folder + "/ABL_*_temp.gcode")[0]
        f = open(processed_file, "r")
        new_data = f.read()
        f.close()

        shutil.rmtree(temp_folder)
        Logger.log("d", "Antibacklash done...")

        return new_data.splitlines(keepends=True)