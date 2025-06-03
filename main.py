import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from package_name.xarm_controller import XArmController

def main():
    controller = XArmController(ip="192.168.1.210")
    controller.run()

if __name__ == "__main__":
    main()