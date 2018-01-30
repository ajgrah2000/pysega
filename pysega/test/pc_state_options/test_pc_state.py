import pc_state_variations
import pc_state_register_classes
import pc_state_union
import unittest
import pysega.cpu.addressing as addressing
import time

class TimeTests(unittest.TestCase):

    def setUp(self):
        self.startTime = time.time()

    def tearDown(self):
        t = time.time() - self.startTime
        print("%s: %.4f" % (self.id(), t))

class TestPC_StateVariations(TimeTests):

    def setUp(self):
        super(TestPC_StateVariations, self).setUp()
        self._timing_iterations = 100000

    def test_pc_status(self):
        p = pc_state_variations.PC_State()
        p.A = 1
        p.A = p.A + 1
        p.A = p.A + 255
        self.assertEqual(p.A, 1)
        p.H = p.H + 1
        p.H = p.H + 257
        self.assertEqual(p.H, 2)
        self.assertEqual(p.HL, 512)
        self.assertEqual(p.IX, 0)
        p.IX = 259
        self.assertEqual(p.IXLow, 3)

        p.PC = p.PC + 513
        p.PC += 2

        self.assertEqual(p.PCHigh, 2)
        self.assertEqual(p.PCLow, 3)

        p.Fstatus.C = 1
        self.assertEqual(p.Fstatus.C, 1)
        self.assertEqual(p.Fstatus.H, 0)

    def test_time_8_bit_access(self):
        p = pc_state_variations.PC_State()
        p.A = 1
        for x in range(1, self._timing_iterations):
          p.A = p.A + x

        # Generate the expected result
        expected = 1
        for x in range(1, self._timing_iterations):
          expected = expected + x
        expected = expected & 0xFF

        self.assertEqual(p.A, expected)

    def test_time_16_bit_access(self):
        p = pc_state_variations.PC_State()
        p.SP = 1
        for x in range(1, self._timing_iterations):
          p.SP = p.SP + x

        # Generate the expected result
        expected = 1
        for x in range(1, self._timing_iterations):
          expected = expected + x
        expected = expected & 0xFFFF

        self.assertEqual(p.SP, expected)
        self.assertEqual(p.SPLow, expected & 0xFF)
        self.assertEqual(p.SPHigh, (expected >> 8) & 0xFF)

    def test_time_8_bit_access_register_classes(self):
        p = pc_state_register_classes.PC_State()
        p.A.set_value(1)
        for x in range(1, self._timing_iterations):
          p.A.set_value(p.A.get_value() + x)

        # Generate the expected result
        expected = 1
        for x in range(1, self._timing_iterations):
          expected = expected + x
        expected = expected & 0xFF

        self.assertEqual(p.A.get_value(), expected)

    def test_time_16_bit_access_register_classes(self):
        p = pc_state_register_classes.PC_State()
        p.SP.set_value(1)
        for x in range(1, self._timing_iterations):
          p.SP.set_value(p.SP.get_value() + x)

        # Generate the expected result
        expected = 1
        for x in range(1, self._timing_iterations):
          expected = expected + x
        expected = expected & 0xFFFF

        self.assertEqual(p.SP.get_value(), expected)
        self.assertEqual(p.SP.low_register.get_value(), expected & 0xFF)
        self.assertEqual(p.SP.high_register.get_value(), (expected >> 8) & 0xFF)

    def test_time_8_bit_access_struct(self):
        p = pc_state_union.PC_State()
        p.A = 1
        for x in range(1, self._timing_iterations):
          p.A = p.A + x

        # Generate the expected result
        expected = 1
        for x in range(1, self._timing_iterations):
          expected = expected + x
        expected = expected & 0xFF

        self.assertEqual(p.A, expected)

    def test_time_16_bit_access_struct(self):
        p = pc_state_union.PC_State()
        p.SP = 1
        for x in range(1, self._timing_iterations):
          p.SP = p.SP + x

        # Generate the expected result
        expected = 1
        for x in range(1, self._timing_iterations):
          expected = expected + x
        expected = expected & 0xFFFF

        self.assertEqual(p.SP, expected)
        self.assertEqual(p.SPLow, expected & 0xFF)
        self.assertEqual(p.SPHigh, (expected >> 8) & 0xFF)

    def test_pc_status_flags_struct(self):
        flags = pc_state_union.PC_StatusFlags()
        flags.status.S = 1
        flags.status.N = 1
        self.assertEqual(flags.value, 130)

    def test_pc_status_flags(self):
        flags = pc_state_variations.PC_StatusFlags()
        flags.S = 1
        flags.Z = 1
        flags.X2 = 0
        flags.H = 1
        flags.X1 = 1
        flags.PV = 0
        flags.N = 1
        flags.C = 1

        self.assertEqual(str(flags), "(C:1 N:1 PV:0 X1:1 H:1 X2:0 Z:1 S:1)")

    def test_pc_status_ref_check(self):
        p = pc_state_variations.PC_State()
        a1 = addressing.RegWrapper_E(p)
        a1.set(3)
        self.assertEqual(p.E, 3)

if __name__ == '__main__':
    unittest.main()
