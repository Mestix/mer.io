import sys

from controllers.mer_controller import MerController

if __name__ == '__main__':
    controller = MerController()
    sys.exit(controller.run())
