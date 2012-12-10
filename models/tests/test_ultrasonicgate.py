"""test_ultrasonicgate.py - tests the ultrasonicgate module

Chris R. Coughlin (TRI/Austin, Inc.)
"""

__author__ = 'Chris R. Coughlin'

import unittest
from models import ultrasonicgate
import numpy as np
import random

class TestUltrasonicGate(unittest.TestCase):
    """Tests the UltrasonicGate class"""

    def setUp(self):
        self.sample_data = np.array(self.random_data())
        self.start_pos = random.randint(0, 15)
        self.stop_pos = self.start_pos + random.randint(0, 20)
        self.sample_gate = ultrasonicgate.UltrasonicGate(start_pos=self.start_pos, end_pos=self.stop_pos,
                                                         name="Test Gate", description="Dummy ultrasonic gate",
                                                         authors="TRI", url="www.tri-austin.com", version="1.1")

    def random_data(self):
        """Returns a list of random data"""
        return [random.uniform(-50, 50) for i in range(50)]

    def test_data_property(self):
        """Verify the gate's data property is set properly"""
        self.sample_gate.data = self.sample_data
        self.assertTrue(np.array_equal(self.sample_data, self.sample_gate.data))

    def test_apply_gate(self):
        """Verify the apply_gate method correctly applies an ultrasonic gate to input data"""
        left_of_gate = np.zeros(self.start_pos)
        right_of_gate = np.zeros(self.sample_data.shape[0] - self.stop_pos)
        middle_of_gate = np.ones(self.stop_pos - self.start_pos)
        default_gate = np.concatenate((left_of_gate, middle_of_gate, right_of_gate))
        expected_data = np.multiply(self.sample_data, default_gate)
        self.sample_gate.data = self.sample_data
        self.sample_gate.apply_gate()
        self.assertTrue(np.array_equal(expected_data, self.sample_gate.data))

    def test_apply_gate_3d(self):
        """Verify the apply_gate method correctly applies a gate to 3D data"""
        sample_data = np.array(self.random_data()).reshape([2, 5, -1])
        expected_data = np.array(sample_data)
        start_pos = 1
        stop_pos = 3
        left_of_gate = np.zeros(start_pos)
        middle_of_gate = np.ones(stop_pos - start_pos)
        right_of_gate = np.zeros(sample_data.shape[2] - stop_pos)
        completed_gate = np.concatenate((left_of_gate, middle_of_gate, right_of_gate))
        for xidx in range(sample_data.shape[1]):
            for yidx in range(sample_data.shape[0]):
                ascan = sample_data[yidx, xidx, :]
                new_ascan = np.multiply(ascan, completed_gate)
                expected_data[yidx, xidx, :] = new_ascan
        sample_gate = ultrasonicgate.UltrasonicGate(start_pos=start_pos, end_pos=stop_pos,
            name="Test Gate", description="Dummy ultrasonic gate",
            authors="TRI", url="www.tri-austin.com", version="1.1")
        sample_gate.data = sample_data
        sample_gate.apply_gate()
        self.assertTrue(np.array_equal(expected_data, sample_gate.data))

    def test_get_window(self):
        """Verify the base UltrasonicGate class returns a no-op window"""
        expected_gate = np.ones(self.stop_pos - self.start_pos)
        expected_gate_list = expected_gate.tolist()
        returned_gate_list = self.sample_gate.get_window().tolist()
        for idx in range(len(expected_gate_list)):
            self.assertAlmostEqual(expected_gate_list[idx], returned_gate_list[idx],
                                   delta=.01 * expected_gate_list[idx])

if __name__ == "__main__":
    unittest.main()