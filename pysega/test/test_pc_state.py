import pysega.cpu.pc_state_union as pc_state
import unittest
import pysega.cpu.addressing as addressing

class TestPC_State(unittest.TestCase):
    def test_pc_status(self):
        p = pc_state.PC_State()
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

        p.F.Fstatus.C = 1
        self.assertEqual(p.F.Fstatus.C, 1)
        self.assertEqual(p.F.Fstatus.H, 0)

    def test_pc_status_flags(self):
        flags = pc_state.PC_StatusFlags()
        flags.Fstatus.S = 1
        flags.Fstatus.Z = 1
        flags.Fstatus.X2 = 0
        flags.Fstatus.H = 1
        flags.Fstatus.X1 = 1
        flags.Fstatus.PV = 0
        flags.Fstatus.N = 1
        flags.Fstatus.C = 1

        self.assertEqual(str(flags.Fstatus), "(C:1 N:1 PV:0 X1:1 H:1 X2:0 Z:1 S:1)")

    def test_pc_status_ref_check(self):
        p = pc_state.PC_State()
        a1 = addressing.RegWrapper_E(p)
        a1.set(3)
        self.assertEqual(p.E, 3)

if __name__ == '__main__':
    unittest.main()
