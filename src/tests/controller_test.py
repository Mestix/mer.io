import unittest

from src.controllers.mer_controller import MerController


class ControllerTests(unittest.TestCase):
    controller: MerController = MerController()

    def test_init_controller(self):
        """
        Should correctly initiate MerController
        """

        self.assertEqual(True, True)


