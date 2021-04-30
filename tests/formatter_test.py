import unittest

from utility.formatters import format_degrees_to_coordinate_long, format_degrees_to_coordinate_lat, format_minutes, \
    format_degrees_long, format_degrees_lat


class DegreesToCoordinatesTests(unittest.TestCase):

    def test_lat(self):
        """
        Should correctly convert lat degrees to lat coordinates
        """
        lat_coordinate = format_degrees_to_coordinate_lat(11.111)
        self.assertEqual("N 11° 06.66'", lat_coordinate)

    def test_long(self):
        """
        Should correctly convert long degrees to long coordinates
        """
        long_coordinate = format_degrees_to_coordinate_long(-1.1111)
        self.assertEqual("W 001° 06.67'", long_coordinate)

    def test_format_minute(self):
        """
        Should round minutes to 2 decimals
        """
        minutes = format_minutes(32.5689)
        self.assertEqual("32.57", minutes)

    def test_format_degrees_long(self):
        """
        Should format long coordinate to consists of 3 numbers and 0 decimals
        """

        cases = {
            1: '001',
            11: '011',
            111: '111',
            1.1: '001',
            1.6: '002'
        }

        for key, value in cases.items():
            with self.subTest(key=key):
                self.assertEqual(value, format_degrees_long(key))

    def test_format_degrees_lat(self):
        """
        Should format lat coordinate to consists of 2 numbers and 0 decimals
        """

        cases = {
            11: '11',
            11.1: '11',
            11.11: '11',
            11.111: '11',
            11.9: '12'
        }

        for key, value in cases.items():
            with self.subTest(key=key):
                self.assertEqual(value, format_degrees_lat(key))


