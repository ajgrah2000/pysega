import pysega.cpu.pc_state as pc_state
import unittest

class TestPC_State(unittest.TestCase):
    def test_pc_status(self):
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

    def test_pc_status_flags(self):
        flags = pc_state.PC_StatusFlags()
        flags.S = 1
        flags.Z = 1
        flags.X2 = 0
        flags.H = 1
        flags.X1 = 1
        flags.PV = 0
        flags.N = 1
        flags.C = 1

        self.assertEqual(str(flags), "(C:1 N:1 PV:0 X1:1 H:1 X2:0 Z:1 S:1)")

if __name__ == '__main__':
    unittest.main()
