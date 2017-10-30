import pysega.cpu.pc_state as pc_state
import unittest

class TestPC_State(unittest.TestCase):
    def test_pc_status(self):
        a = pc_state.PC_Register(8)
        a.set_value(8)
        b = pc_state.PC_Register(8)
        b.set_value(13)
        b = b + a
        b += 1
        p = pc_state.PC_State()
        p.A = 1
        p.A = p.A + 1
        p.A = p.A + 255
        self.assertEqual(p.A, 1)
        p.HLHigh = p.HLHigh + 1
        p.HLHigh = p.HLHigh + 257
        self.assertEqual(p.HLHigh, 2)
        self.assertEqual(p.HL, 512)
        self.assertEqual(p.IX, 0)
        p.IX = 259
        self.assertEqual(p.IXLow, 3)

        p.PC = p.PC + 513
        p.PC += 2

        self.assertEqual(p.PCHigh, 2)
        self.assertEqual(p.PCLow, 3)

if __name__ == '__main__':
    unittest.main()
