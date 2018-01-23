from . import instructions
import addressing
import types

class InstructionDecode(object):
    def __init__(self, clocks, pc_state, memory, instruction_lookup):
        self.pc_state           = pc_state
        self.clocks             = clocks
        self.memory             = memory
        self.instruction        = None
        self.instruction_lookup = instruction_lookup 

    def execute(self):
        if (None == self.instruction):
            op_code = self.memory.read(self.pc_state.PC);
            ins = self.instruction_lookup.getInstruction(op_code)
            if hasattr(ins, 'get_cached_execute'):
              self.instruction_exec = types.MethodType(ins.get_cached_execute(), ins)
            else:
              self.instruction_exec = ins.execute

        def _execute_replacement(self):
            # Need to add cycles *after* to ensure during recursive calls (ie
            # EI), the 'child' clock increase doesn't get clobbered. (ie self.clocks isn't on stack).
            c = self.clocks.cycles
            self.clocks.cycles = self.instruction_exec() + c

        _execute_replacement(self)

        # Bind inner method
        self.execute = types.MethodType(_execute_replacement, self)

class InstructionCache(object):
    def __init__(self, clocks, pc_state, memory, instruction_lookup):
        self.absolute_instruction_cache = [InstructionDecode(clocks, pc_state, memory, instruction_lookup) for _ in range(memory.get_max_absolute_instruction_address())]


class InstructionStore(object):
    def __init__(self, clocks, pc_state, ports):
        self.clocks          = clocks
        self.pc_state        = pc_state
        self.ports           = ports

        self.instruction_lookup    = [None] * 256
        self.instruction_cb_lookup = [None] * 256
        self.instruction_dd_lookup = [None] * 256
        self.instruction_ed_lookup = [None] * 256
        self.instruction_fd_lookup = [None] * 256

    def populate_instruction_map(self, clocks, pc_state, memory, interupt, poll_interupts, step_func):
        self._initialise_register_wrappers(pc_state)

        self._populate_core_instruction_map(clocks, pc_state, memory, self.ports, interupt, poll_interupts, step_func)
        self._populate_extended_fd_instruction_map(pc_state, memory)
        self._populate_extended_ed_instruction_map(pc_state, memory, self.ports)
        self._populate_extended_dd_instruction_map(pc_state, memory)
        self._populate_extended_cb_instruction_map(pc_state, memory)

        # Try 'installing' extended instructions.
        self.instruction_lookup[0xCB] = instructions.ExtendedInstruction(memory, pc_state, self.getExtendedCB)
        self.instruction_lookup[0xDD] = instructions.ExtendedInstruction(memory, pc_state, self.getExtendedDD)
        self.instruction_lookup[0xFD] = instructions.ExtendedInstruction(memory, pc_state, self.getExtendedFD)
        self.instruction_lookup[0xED] = instructions.ExtendedInstruction(memory, pc_state, self.getExtendedED)

    def _initialise_register_wrappers(self, pc_state):
        self._reg_wrapper_a  = addressing.RegWrapper_A(pc_state)
        self._reg_wrapper_b  = addressing.RegWrapper_B(pc_state)
        self._reg_wrapper_c  = addressing.RegWrapper_C(pc_state)
        self._reg_wrapper_d  = addressing.RegWrapper_D(pc_state)
        self._reg_wrapper_e  = addressing.RegWrapper_E(pc_state)
        self._reg_wrapper_h  = addressing.RegWrapper_H(pc_state)
        self._reg_wrapper_l  = addressing.RegWrapper_L(pc_state)
        self._reg_wrapper_sp = addressing.RegWrapper_SP(pc_state)
        self._reg_wrapper_bc = addressing.RegWrapper_BC(pc_state)
        self._reg_wrapper_de = addressing.RegWrapper_DE(pc_state)
        self._reg_wrapper_hl = addressing.RegWrapper_HL(pc_state)
        self._reg_wrapper_ix = addressing.RegWrapper_IX(pc_state)
        self._reg_wrapper_iy = addressing.RegWrapper_IY(pc_state)
        self._reg_wrapper_sp = addressing.RegWrapper_SP(pc_state)

    def _populate_core_instruction_map(self, clocks, pc_state, memory, ports, interupt, poll_interupts, step_func):

        self.instruction_lookup[0xFB] = instructions.EI(memory, clocks, pc_state, interupt, poll_interupts, step_func)

        self.instruction_lookup[0xC3] = instructions.JumpInstruction(memory, pc_state)
        self.instruction_lookup[0x31] = instructions.LD_16_nn(memory, pc_state, self._reg_wrapper_sp); # LD DE, nn

        self.instruction_lookup[0x00] = instructions.Noop(memory, pc_state);
        self.instruction_lookup[0x01] = instructions.Load16BC(memory, pc_state, self._reg_wrapper_bc);
        self.instruction_lookup[0x02] = instructions.LD_mem_r(memory, pc_state, self._reg_wrapper_bc, self._reg_wrapper_a); # LD (BC), A
        self.instruction_lookup[0x03] = instructions.INC_BC(memory, pc_state); # INC cpu_state->BC
        self.instruction_lookup[0x04] = instructions.INC_r(memory, pc_state, self._reg_wrapper_b); # INC cpu_state->B
        self.instruction_lookup[0x06] = instructions.LD_r(memory, pc_state, self._reg_wrapper_b);
        self.instruction_lookup[0x07] = instructions.RLCA(memory, pc_state);  #RLCA
        self.instruction_lookup[0x09] = instructions.ADD16(memory, pc_state, self._reg_wrapper_hl, self._reg_wrapper_bc,11);
        self.instruction_lookup[0x0A] = instructions.LD_r_mem(memory, pc_state, self._reg_wrapper_a, self._reg_wrapper_bc); # LD A, (BC)
        self.instruction_lookup[0x0B] = instructions.DEC_16(memory, pc_state, self._reg_wrapper_bc, 6);
        self.instruction_lookup[0x0C] = instructions.INC_r(memory, pc_state, self._reg_wrapper_c); # INC C
        self.instruction_lookup[0x0E] = instructions.LD_r(memory, pc_state, self._reg_wrapper_c); # LD C, n
        self.instruction_lookup[0x0F] = instructions.RRCA(memory, pc_state);
        self.instruction_lookup[0x10] = instructions.DJNZ(memory, pc_state); # DJNZ n
        self.instruction_lookup[0x11] = instructions.LD_16_nn(memory, pc_state, self._reg_wrapper_de); # LD DE, nn
        self.instruction_lookup[0x12] = instructions.LD_mem_r(memory, pc_state, self._reg_wrapper_de, self._reg_wrapper_a); # LD (DE), A
        self.instruction_lookup[0x21] = instructions.LD_16_nn(memory, pc_state, self._reg_wrapper_hl); # LD HL, nn
        self.instruction_lookup[0x2A] = instructions.LD_r16_mem(memory, pc_state, self._reg_wrapper_hl); # LD HL, (nn)
        self.instruction_lookup[0x31] = instructions.LD_16_nn(memory, pc_state, self._reg_wrapper_sp); # LD DE, nn
        self.instruction_lookup[0x13] = instructions.INC_16(memory, pc_state, self._reg_wrapper_de, 6);
        self.instruction_lookup[0x14] = instructions.INC_r(memory, pc_state, self._reg_wrapper_d); # INC D
        self.instruction_lookup[0x16] = instructions.LD_r(memory, pc_state, self._reg_wrapper_d); # LD D, n
        self.instruction_lookup[0x19] = instructions.ADD16(memory, pc_state, self._reg_wrapper_hl, self._reg_wrapper_de,11);
        self.instruction_lookup[0x1A] = instructions.LD_r_mem(memory, pc_state, self._reg_wrapper_a, self._reg_wrapper_de); # LD A, (DE)
        self.instruction_lookup[0x1B] = instructions.DEC_16(memory, pc_state, self._reg_wrapper_de, 6);
 
        self.instruction_lookup[0x1C] = instructions.INC_r(memory, pc_state, self._reg_wrapper_e); # INC E
        self.instruction_lookup[0x1E] = instructions.LD_r(memory, pc_state, self._reg_wrapper_e); # LD E, n
 
        self.instruction_lookup[0x20] = instructions.JRNZe(memory, pc_state); # JR NZ, e
 
        self.instruction_lookup[0x23] = instructions.INC_16(memory, pc_state, self._reg_wrapper_hl, 6);
 
        self.instruction_lookup[0x24] = instructions.INC_r(memory, pc_state, self._reg_wrapper_h); # INC H
        self.instruction_lookup[0x26] = instructions.LD_r(memory, pc_state, self._reg_wrapper_h); # LD H, n
        self.instruction_lookup[0x28] = instructions.JRZe(memory, pc_state); # JR Z, e
        self.instruction_lookup[0x29] = instructions.ADD16(memory, pc_state, self._reg_wrapper_hl, self._reg_wrapper_hl,11);
        self.instruction_lookup[0x2B] = instructions.DEC_16(memory, pc_state, self._reg_wrapper_hl, 6);
 
        self.instruction_lookup[0x2C] = instructions.INC_r(memory, pc_state, self._reg_wrapper_l); # INC L
        self.instruction_lookup[0x2E] = instructions.LD_r(memory, pc_state, self._reg_wrapper_l); # LD L, n
        self.instruction_lookup[0x33] = instructions.INC_16(memory, pc_state, self._reg_wrapper_sp, 6);
        self.instruction_lookup[0x34] = instructions.INC_HL(memory, pc_state); # INC HL
        self.instruction_lookup[0x35] = instructions.DEC_HL(memory, pc_state); # DEC HL
 
        self.instruction_lookup[0x36] = instructions.LD_mem_n(memory, pc_state, self._reg_wrapper_hl); # LD (HL), n
 
        self.instruction_lookup[0x39] = instructions.ADD16(memory, pc_state, self._reg_wrapper_hl, self._reg_wrapper_sp,11);
 
        self.instruction_lookup[0x3A] = instructions.LD_r8_mem(memory, pc_state, self._reg_wrapper_a); # LD A, (n)
        self.instruction_lookup[0x3B] = instructions.DEC_16(memory, pc_state, self._reg_wrapper_sp, 6);
        self.instruction_lookup[0x3C] = instructions.INC_r(memory, pc_state, self._reg_wrapper_a); # INC A
        self.instruction_lookup[0x3E] = instructions.LD_r(memory, pc_state, self._reg_wrapper_a); # LD A, n
 
        self.instruction_lookup[0x70] = instructions.LD_mem_r(memory, pc_state, self._reg_wrapper_hl, self._reg_wrapper_b); # LD (HL), B
        self.instruction_lookup[0x71] = instructions.LD_mem_r(memory, pc_state, self._reg_wrapper_hl, self._reg_wrapper_c); # LD (HL), C
        self.instruction_lookup[0x72] = instructions.LD_mem_r(memory, pc_state, self._reg_wrapper_hl, self._reg_wrapper_d); # LD (HL), D
        self.instruction_lookup[0x73] = instructions.LD_mem_r(memory, pc_state, self._reg_wrapper_hl, self._reg_wrapper_e); # LD (HL), E
        self.instruction_lookup[0x74] = instructions.LD_mem_r(memory, pc_state, self._reg_wrapper_hl, self._reg_wrapper_h); # LD (HL), H
        self.instruction_lookup[0x75] = instructions.LD_mem_r(memory, pc_state, self._reg_wrapper_hl, self._reg_wrapper_l); # LD (HL), L
        self.instruction_lookup[0x77] = instructions.LD_mem_r(memory, pc_state, self._reg_wrapper_hl, self._reg_wrapper_a); # LD (HL), A
 
        self.instruction_lookup[0x80] = instructions.ADD_r(memory, pc_state, self._reg_wrapper_b); # ADD r, cpu_state->B
        self.instruction_lookup[0x81] = instructions.ADD_r(memory, pc_state, self._reg_wrapper_c); # ADD r, cpu_state->C
        self.instruction_lookup[0x82] = instructions.ADD_r(memory, pc_state, self._reg_wrapper_d); # ADD r, cpu_state->D
        self.instruction_lookup[0x83] = instructions.ADD_r(memory, pc_state, self._reg_wrapper_e); # ADD r, cpu_state->E
        self.instruction_lookup[0x84] = instructions.ADD_r(memory, pc_state, self._reg_wrapper_h); # ADD r, cpu_state->H
        self.instruction_lookup[0x85] = instructions.ADD_r(memory, pc_state, self._reg_wrapper_l); # ADD r, cpu_state->L
        self.instruction_lookup[0x87] = instructions.ADD_r(memory, pc_state, self._reg_wrapper_a); # ADD r, cpu_state->A

        self.instruction_lookup[0x90] = instructions.SUB_r(memory, pc_state, self._reg_wrapper_b); # SUB r, cpu_state->B
        self.instruction_lookup[0x91] = instructions.SUB_r(memory, pc_state, self._reg_wrapper_c); # SUB r, cpu_state->C
        self.instruction_lookup[0x92] = instructions.SUB_r(memory, pc_state, self._reg_wrapper_d); # SUB r, cpu_state->D
        self.instruction_lookup[0x93] = instructions.SUB_r(memory, pc_state, self._reg_wrapper_e); # SUB r, cpu_state->E
        self.instruction_lookup[0x94] = instructions.SUB_r(memory, pc_state, self._reg_wrapper_h); # SUB r, cpu_state->H
        self.instruction_lookup[0x95] = instructions.SUB_r(memory, pc_state, self._reg_wrapper_l); # SUB r, cpu_state->L
        self.instruction_lookup[0x97] = instructions.SUB_r(memory, pc_state, self._reg_wrapper_a); # SUB r, cpu_state->A
 
        self.instruction_lookup[0xA0] = instructions.AND_r(memory, pc_state, self._reg_wrapper_b); # AND r, cpu_state->A
        self.instruction_lookup[0xA1] = instructions.AND_r(memory, pc_state, self._reg_wrapper_c); # AND r, cpu_state->A
        self.instruction_lookup[0xA2] = instructions.AND_r(memory, pc_state, self._reg_wrapper_d); # AND r, cpu_state->A
        self.instruction_lookup[0xA3] = instructions.AND_r(memory, pc_state, self._reg_wrapper_e); # AND r, cpu_state->A
        self.instruction_lookup[0xA4] = instructions.AND_r(memory, pc_state, self._reg_wrapper_h); # AND r, cpu_state->A
        self.instruction_lookup[0xA5] = instructions.AND_r(memory, pc_state, self._reg_wrapper_l); # AND r, cpu_state->A
        self.instruction_lookup[0xA7] = instructions.AND_r(memory, pc_state, self._reg_wrapper_a); # AND r, cpu_state->A
 
        self.instruction_lookup[0xA8] = instructions.XOR_r(memory, pc_state, self._reg_wrapper_b); # XOR r, cpu_state->A
        self.instruction_lookup[0xA9] = instructions.XOR_r(memory, pc_state, self._reg_wrapper_c); # XOR r, cpu_state->A
        self.instruction_lookup[0xAA] = instructions.XOR_r(memory, pc_state, self._reg_wrapper_d); # XOR r, cpu_state->A
        self.instruction_lookup[0xAB] = instructions.XOR_r(memory, pc_state, self._reg_wrapper_e); # XOR r, cpu_state->A
        self.instruction_lookup[0xAC] = instructions.XOR_r(memory, pc_state, self._reg_wrapper_h); # XOR r, cpu_state->A
        self.instruction_lookup[0xAD] = instructions.XOR_r(memory, pc_state, self._reg_wrapper_l); # XOR r, cpu_state->A
        self.instruction_lookup[0xAF] = instructions.XOR_r(memory, pc_state, self._reg_wrapper_a); # XOR r, cpu_state->A
 
        self.instruction_lookup[0xB0] = instructions.OR_r(memory, pc_state, self._reg_wrapper_b); # OR r, cpu_state->A
        self.instruction_lookup[0xB1] = instructions.OR_r(memory, pc_state, self._reg_wrapper_c); # OR r, cpu_state->A
        self.instruction_lookup[0xB2] = instructions.OR_r(memory, pc_state, self._reg_wrapper_d); # OR r, cpu_state->A
#        self.instruction_lookup[0xB3] = instructions.OR_r(memory, pc_state, self._reg_wrapper_e); # OR r, cpu_state->A
        self.instruction_lookup[0xB3] = instructions.OR_e(memory, pc_state); # OR r, cpu_state->A
        self.instruction_lookup[0xB4] = instructions.OR_r(memory, pc_state, self._reg_wrapper_h); # OR r, cpu_state->A
        self.instruction_lookup[0xB5] = instructions.OR_r(memory, pc_state, self._reg_wrapper_l); # OR r, cpu_state->A
        self.instruction_lookup[0xB7] = instructions.OR_r(memory, pc_state, self._reg_wrapper_a); # OR r, cpu_state->A
 
        self.instruction_lookup[0xB8] = instructions.CP_r(memory, pc_state, self._reg_wrapper_b); # CP r, cpu_state->A
        self.instruction_lookup[0xB9] = instructions.CP_r(memory, pc_state, self._reg_wrapper_c); # CP r, cpu_state->A
        self.instruction_lookup[0xBA] = instructions.CP_r(memory, pc_state, self._reg_wrapper_d); # CP r, cpu_state->A
        self.instruction_lookup[0xBB] = instructions.CP_r(memory, pc_state, self._reg_wrapper_e); # CP r, cpu_state->A
        self.instruction_lookup[0xBC] = instructions.CP_r(memory, pc_state, self._reg_wrapper_h); # CP r, cpu_state->A
        self.instruction_lookup[0xBD] = instructions.CP_r(memory, pc_state, self._reg_wrapper_l); # CP r, cpu_state->A
        self.instruction_lookup[0xBF] = instructions.CP_r(memory, pc_state, self._reg_wrapper_a); # CP r, cpu_state->A
 
        self.instruction_lookup[0xD3] = instructions.OUT_n_A(memory, pc_state, self.ports); # OUT (n), cpu_state->A
        self.instruction_lookup[0xD2] = instructions.JPNC(memory, pc_state); # JP NC
        self.instruction_lookup[0xD9] = instructions.EXX(memory, pc_state); # EXX
        self.instruction_lookup[0xDA] = instructions.JPCnn(memory, pc_state); # JP C, nn
 
        self.instruction_lookup[0xE6] = instructions.AND_n(memory, pc_state); # AND n
        self.instruction_lookup[0xFE] = instructions.CP_n(memory, pc_state); # CP n

        self.instruction_lookup[0x05] = instructions.DEC_r(memory, pc_state, self._reg_wrapper_b); # DEC B
        self.instruction_lookup[0x0d] = instructions.DEC_r(memory, pc_state, self._reg_wrapper_c); # DEC C
        self.instruction_lookup[0x15] = instructions.DEC_r(memory, pc_state, self._reg_wrapper_d); # DEC D
        self.instruction_lookup[0x1d] = instructions.DEC_r(memory, pc_state, self._reg_wrapper_e); # DEC E
        self.instruction_lookup[0x25] = instructions.DEC_r(memory, pc_state, self._reg_wrapper_h); # DEC H
        self.instruction_lookup[0x2d] = instructions.DEC_r(memory, pc_state, self._reg_wrapper_l); # DEC L
        self.instruction_lookup[0x3d] = instructions.DEC_r(memory, pc_state, self._reg_wrapper_a); # DEC A

        self.instruction_lookup[0x46] = instructions.LD_r_mem(memory, pc_state, self._reg_wrapper_b, self._reg_wrapper_hl); # LD_r_mem B
        self.instruction_lookup[0x4e] = instructions.LD_r_mem(memory, pc_state, self._reg_wrapper_c, self._reg_wrapper_hl); # LD_r_mem C
        self.instruction_lookup[0x56] = instructions.LD_r_mem(memory, pc_state, self._reg_wrapper_d, self._reg_wrapper_hl); # LD_r_mem D
        self.instruction_lookup[0x5e] = instructions.LD_r_mem(memory, pc_state, self._reg_wrapper_e, self._reg_wrapper_hl); # LD_r_mem E
        self.instruction_lookup[0x66] = instructions.LD_r_mem(memory, pc_state, self._reg_wrapper_h, self._reg_wrapper_hl); # LD_r_mem H
        self.instruction_lookup[0x6e] = instructions.LD_r_mem(memory, pc_state, self._reg_wrapper_l, self._reg_wrapper_hl); # LD_r_mem L
        self.instruction_lookup[0x7e] = instructions.LD_r_mem(memory, pc_state, self._reg_wrapper_a, self._reg_wrapper_hl); # LD_r_mem A

        self.instruction_lookup[0x06] = instructions.LD_r(memory, pc_state, self._reg_wrapper_b); # LD_r B
        self.instruction_lookup[0x0e] = instructions.LD_r(memory, pc_state, self._reg_wrapper_c); # LD_r C
        self.instruction_lookup[0x16] = instructions.LD_r(memory, pc_state, self._reg_wrapper_d); # LD_r D
        self.instruction_lookup[0x1e] = instructions.LD_r(memory, pc_state, self._reg_wrapper_e); # LD_r E
        self.instruction_lookup[0x26] = instructions.LD_r(memory, pc_state, self._reg_wrapper_h); # LD_r H
        self.instruction_lookup[0x2e] = instructions.LD_r(memory, pc_state, self._reg_wrapper_l); # LD_r L
        self.instruction_lookup[0x3e] = instructions.LD_r(memory, pc_state, self._reg_wrapper_a); # LD_r A

        for (i1, r1) in [(0, self._reg_wrapper_b), (1, self._reg_wrapper_c), (2, self._reg_wrapper_d), (3, self._reg_wrapper_e), (4, self._reg_wrapper_h), (5, self._reg_wrapper_l), (7, self._reg_wrapper_a)]:
          for (i2, r2) in [(0, self._reg_wrapper_b), (1, self._reg_wrapper_c), (2, self._reg_wrapper_d), (3, self._reg_wrapper_e), (4, self._reg_wrapper_h), (5, self._reg_wrapper_l), (7, self._reg_wrapper_a)]:
            self.instruction_lookup[0x40 + i1 + (i2 * 8)] = instructions.LD_r_r(memory, pc_state, r2, r1) 

        self.instruction_lookup[0xC9] = instructions.RET(memory, pc_state); # RET

        self.instruction_lookup[0x08] = instructions.EX(memory, pc_state)
        self.instruction_lookup[0x12] = instructions.LD_DE_A(memory, pc_state)
        self.instruction_lookup[0x17] = instructions.RLA(memory, pc_state)
        self.instruction_lookup[0x18] = instructions.JR_e(memory, pc_state)
        self.instruction_lookup[0x1F] = instructions.RRA(memory, pc_state)
        self.instruction_lookup[0x22] = instructions.LD__nn_HL(memory, pc_state)
        self.instruction_lookup[0x27] = instructions.DAA(memory, pc_state)
        self.instruction_lookup[0x2F] = instructions.CPL(memory, pc_state)
        self.instruction_lookup[0x30] = instructions.JRNC_e(memory, pc_state)
        self.instruction_lookup[0x32] = instructions.LD_nn_A(memory, pc_state)
        self.instruction_lookup[0x37] = instructions.SCF(memory, pc_state)
        self.instruction_lookup[0x38] = instructions.JRC_e(memory, pc_state)
        self.instruction_lookup[0x3F] = instructions.CCF(memory, pc_state)
        self.instruction_lookup[0x76] = instructions.LD_HL_HL(memory, pc_state)
        self.instruction_lookup[0x86] = instructions.ADD_HL(memory, pc_state)

        self.instruction_lookup[0x88] = instructions.ADC_r(memory, pc_state, self._reg_wrapper_b)
        self.instruction_lookup[0x89] = instructions.ADC_r(memory, pc_state, self._reg_wrapper_c)
        self.instruction_lookup[0x8A] = instructions.ADC_r(memory, pc_state, self._reg_wrapper_d)
        self.instruction_lookup[0x8B] = instructions.ADC_r(memory, pc_state, self._reg_wrapper_e)
        self.instruction_lookup[0x8C] = instructions.ADC_r(memory, pc_state, self._reg_wrapper_h)
        self.instruction_lookup[0x8D] = instructions.ADC_r(memory, pc_state, self._reg_wrapper_l)
        self.instruction_lookup[0x8F] = instructions.ADC_r(memory, pc_state, self._reg_wrapper_a)
        self.instruction_lookup[0x8E] = instructions.ADC_HL(memory, pc_state)

        self.instruction_lookup[0x96] = instructions.SUB_HL(memory, pc_state)

        self.instruction_lookup[0x98] = instructions.SBC_A_r(memory, pc_state, self._reg_wrapper_b)
        self.instruction_lookup[0x99] = instructions.SBC_A_r(memory, pc_state, self._reg_wrapper_c)
        self.instruction_lookup[0x9A] = instructions.SBC_A_r(memory, pc_state, self._reg_wrapper_d)
        self.instruction_lookup[0x9B] = instructions.SBC_A_r(memory, pc_state, self._reg_wrapper_e)
        self.instruction_lookup[0x9C] = instructions.SBC_A_r(memory, pc_state, self._reg_wrapper_h)
        self.instruction_lookup[0x9D] = instructions.SBC_A_r(memory, pc_state, self._reg_wrapper_l)
        self.instruction_lookup[0x9F] = instructions.SBC_A_r(memory, pc_state, self._reg_wrapper_a)
        self.instruction_lookup[0x9E] = instructions.SBC_A_HL(memory, pc_state)

        self.instruction_lookup[0xA6] = instructions.AND_HL(memory, pc_state)
        self.instruction_lookup[0xAE] = instructions.XOR_HL(memory, pc_state)
        self.instruction_lookup[0xB6] = instructions.OR_HL(memory, pc_state)
        self.instruction_lookup[0xBE] = instructions.CP_HL(memory, pc_state)
        self.instruction_lookup[0xC0] = instructions.RET_NZ(memory, pc_state)
        self.instruction_lookup[0xC1] = instructions.POP(memory, pc_state, self._reg_wrapper_bc)
        self.instruction_lookup[0xC2] = instructions.JPNZ_nn(memory, pc_state)
        self.instruction_lookup[0xC3] = instructions.JP_nn(memory, pc_state)
        self.instruction_lookup[0xC4] = instructions.CALL_NZ_nn(memory, pc_state)
        self.instruction_lookup[0xC5] = instructions.PUSH(memory, pc_state, self._reg_wrapper_bc)
        self.instruction_lookup[0xC6] = instructions.ADD_n(memory, pc_state)
        self.instruction_lookup[0xC7] = instructions.RST(memory, pc_state, 0x00) # RST_00
        self.instruction_lookup[0xC8] = instructions.RST_Z(memory, pc_state)
        self.instruction_lookup[0xCA] = instructions.JPZ_nn(memory, pc_state)
        self.instruction_lookup[0xCC] = instructions.CALL_Z_nn(memory, pc_state)
        self.instruction_lookup[0xCD] = instructions.CALL_nn(memory, pc_state)
        self.instruction_lookup[0xCE] = instructions.ADC_nn(memory, pc_state)
        self.instruction_lookup[0xCF] = instructions.RST(memory, pc_state, 0x08) # RST_08
        self.instruction_lookup[0xD0] = instructions.RET_NC(memory, pc_state)
        self.instruction_lookup[0xD1] = instructions.POP(memory, pc_state, self._reg_wrapper_de)
        self.instruction_lookup[0xD4] = instructions.CALL_NC_nn(memory, pc_state)
        self.instruction_lookup[0xD5] = instructions.PUSH(memory, pc_state, self._reg_wrapper_de)
        self.instruction_lookup[0xD6] = instructions.SUB_n(memory, pc_state)
        self.instruction_lookup[0xD7] = instructions.RST(memory, pc_state, 0x10) # RST_10
        self.instruction_lookup[0xD8] = instructions.RET_C(memory, pc_state)
        self.instruction_lookup[0xDB] = instructions.IN_A_n(memory, pc_state, ports)
        self.instruction_lookup[0xDC] = instructions.CALL_C_nn(memory, pc_state)
        self.instruction_lookup[0xDE] = instructions.SBC_n(memory, pc_state)
        self.instruction_lookup[0xDF] = instructions.RST(memory, pc_state, 0x18) # RST_18
        self.instruction_lookup[0xE0] = instructions.RET_PO(memory, pc_state)
        self.instruction_lookup[0xE1] = instructions.POP(memory, pc_state, self._reg_wrapper_hl)
        self.instruction_lookup[0xE2] = instructions.JP_PO_nn(memory, pc_state)
        self.instruction_lookup[0xE3] = instructions.EX_SP_HL(memory, pc_state)
        self.instruction_lookup[0xE4] = instructions.CALL_PO_nn(memory, pc_state)
        self.instruction_lookup[0xE5] = instructions.PUSH(memory, pc_state, self._reg_wrapper_hl)
        self.instruction_lookup[0xE7] = instructions.RST(memory, pc_state, 0x20) # RST_20
        self.instruction_lookup[0xE8] = instructions.RET_PE(memory, pc_state)
        self.instruction_lookup[0xE9] = instructions.LD_PC_HL(memory, pc_state)
        self.instruction_lookup[0xEA] = instructions.JP_PE_nn(memory, pc_state)
        self.instruction_lookup[0xEB] = instructions.EX_DE_HL(memory, pc_state)
        self.instruction_lookup[0xEC] = instructions.CALL_PE_nn(memory, pc_state)
        self.instruction_lookup[0xEE] = instructions.XOR_n(memory, pc_state)
        self.instruction_lookup[0xEF] = instructions.RST(memory, pc_state, 0x28) # RST_28
        self.instruction_lookup[0xF0] = instructions.RET_P(memory, pc_state)
        self.instruction_lookup[0xF1] = instructions.POP_AF(memory, pc_state)
        self.instruction_lookup[0xF2] = instructions.JP_P_nn(memory, pc_state)
        self.instruction_lookup[0xF3] = instructions.DI(memory, pc_state)
        self.instruction_lookup[0xF4] = instructions.CALL_P_nn(memory, pc_state)
        self.instruction_lookup[0xF5] = instructions.PUSH_AF(memory, pc_state)
        self.instruction_lookup[0xF6] = instructions.OR_n(memory, pc_state)
        self.instruction_lookup[0xF7] = instructions.RST(memory, pc_state, 0x30) # RST_30
        self.instruction_lookup[0xF8] = instructions.RET_M(memory, pc_state)
        self.instruction_lookup[0xF9] = instructions.LD_SP_HL(memory, pc_state)
        self.instruction_lookup[0xFA] = instructions.JP_M_nn(memory, pc_state)
#        self.instruction_lookup[0xFB] = instructions.EI(memory, pc_state)
        self.instruction_lookup[0xFC] = instructions.CALL_M_nn(memory, pc_state)
        self.instruction_lookup[0xFF] = instructions.RST(memory, pc_state, 0x38) # RST_38



    def _populate_extended_fd_instruction_map(self, pc_state, memory):
        self.instruction_fd_lookup[0x09] = instructions.ADD16(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_bc,15,2);
        self.instruction_fd_lookup[0x19] = instructions.ADD16(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_de,15,2);
        self.instruction_fd_lookup[0x23] = instructions.INC_16(memory, pc_state, self._reg_wrapper_iy, 10,2);
        self.instruction_fd_lookup[0x29] = instructions.ADD16(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_iy,15,2);
        self.instruction_fd_lookup[0x2B] = instructions.DEC_16(memory, pc_state, self._reg_wrapper_iy, 10,2);
        self.instruction_fd_lookup[0x39] = instructions.ADD16(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_sp,15,2);

        self.instruction_fd_lookup[0x21] = instructions.LD_I_nn(memory, pc_state, self._reg_wrapper_iy)
        self.instruction_fd_lookup[0x22] = instructions.LD_nn_I(memory, pc_state, self._reg_wrapper_iy)
        self.instruction_fd_lookup[0x2A] = instructions.LD_I__nn_(memory, pc_state, self._reg_wrapper_iy)
        self.instruction_fd_lookup[0x34] = instructions.INC_I_d(memory, pc_state, self._reg_wrapper_iy)
        self.instruction_fd_lookup[0x35] = instructions.DEC_I_d(memory, pc_state, self._reg_wrapper_iy)
        self.instruction_fd_lookup[0x36] = instructions.LD_I_d_n(memory, pc_state, self._reg_wrapper_iy)

        self.instruction_fd_lookup[0x46] = instructions.LD_r_I_e(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_b)
        self.instruction_fd_lookup[0x4E] = instructions.LD_r_I_e(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_c)
        self.instruction_fd_lookup[0x56] = instructions.LD_r_I_e(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_d)
        self.instruction_fd_lookup[0x5E] = instructions.LD_r_I_e(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_e)
        self.instruction_fd_lookup[0x66] = instructions.LD_r_I_e(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_h)
        self.instruction_fd_lookup[0x6E] = instructions.LD_r_I_e(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_l)
        self.instruction_fd_lookup[0x7E] = instructions.LD_r_I_e(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_a)

        self.instruction_fd_lookup[0x70] = instructions.LD_I_d_r(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_b)
        self.instruction_fd_lookup[0x71] = instructions.LD_I_d_r(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_c)
        self.instruction_fd_lookup[0x72] = instructions.LD_I_d_r(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_d)
        self.instruction_fd_lookup[0x73] = instructions.LD_I_d_r(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_e)
        self.instruction_fd_lookup[0x74] = instructions.LD_I_d_r(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_h)
        self.instruction_fd_lookup[0x75] = instructions.LD_I_d_r(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_l)
        self.instruction_fd_lookup[0x77] = instructions.LD_I_d_r(memory, pc_state, self._reg_wrapper_iy, self._reg_wrapper_a)

        self.instruction_fd_lookup[0x86] = instructions.ADDA_I_d(memory, pc_state, self._reg_wrapper_iy)
        self.instruction_fd_lookup[0x8E] = instructions.ADC_I_d(memory, pc_state, self._reg_wrapper_iy)
        self.instruction_fd_lookup[0x96] = instructions.SUB_I_d(memory, pc_state, self._reg_wrapper_iy)
        self.instruction_fd_lookup[0xA6] = instructions.AND_I_d(memory, pc_state, self._reg_wrapper_iy)
        self.instruction_fd_lookup[0xAE] = instructions.XOR_I_d(memory, pc_state, self._reg_wrapper_iy)
        self.instruction_fd_lookup[0xB6] = instructions.OR_I_d(memory, pc_state, self._reg_wrapper_iy)
        self.instruction_fd_lookup[0xBE] = instructions.CP_I_d(memory, pc_state, self._reg_wrapper_iy)

        self.instruction_fd_lookup[0xCB] = instructions.BIT_I_d(memory, pc_state, self._reg_wrapper_iy)
        self.instruction_fd_lookup[0xE1] = instructions.POP_I(memory, pc_state, self._reg_wrapper_iy)
        self.instruction_fd_lookup[0xE3] = instructions.EX_SP_I(memory, pc_state, self._reg_wrapper_iy)
        self.instruction_fd_lookup[0xE5] = instructions.PUSH_I(memory, pc_state, self._reg_wrapper_iy)
        self.instruction_fd_lookup[0xE9] = instructions.LD_PC_I(memory, pc_state, self._reg_wrapper_iy)

    def _populate_extended_ed_instruction_map(self, pc_state, memory, ports):
        self.instruction_ed_lookup[0x40] = instructions.IN_r_C(memory, pc_state, ports, self._reg_wrapper_b)
        self.instruction_ed_lookup[0x48] = instructions.IN_r_C(memory, pc_state, ports, self._reg_wrapper_c)
        self.instruction_ed_lookup[0x50] = instructions.IN_r_C(memory, pc_state, ports, self._reg_wrapper_d)
        self.instruction_ed_lookup[0x58] = instructions.IN_r_C(memory, pc_state, ports, self._reg_wrapper_e)
        self.instruction_ed_lookup[0x60] = instructions.IN_r_C(memory, pc_state, ports, self._reg_wrapper_h)
        self.instruction_ed_lookup[0x68] = instructions.IN_r_C(memory, pc_state, ports, self._reg_wrapper_l)
        self.instruction_ed_lookup[0x78] = instructions.IN_r_C(memory, pc_state, ports, self._reg_wrapper_a)

        self.instruction_ed_lookup[0x41] = instructions.OUT_C_r(memory, pc_state, ports, self._reg_wrapper_b)
        self.instruction_ed_lookup[0x49] = instructions.OUT_C_r(memory, pc_state, ports, self._reg_wrapper_c)
        self.instruction_ed_lookup[0x51] = instructions.OUT_C_r(memory, pc_state, ports, self._reg_wrapper_d)
        self.instruction_ed_lookup[0x59] = instructions.OUT_C_r(memory, pc_state, ports, self._reg_wrapper_e)
        self.instruction_ed_lookup[0x61] = instructions.OUT_C_r(memory, pc_state, ports, self._reg_wrapper_h)
        self.instruction_ed_lookup[0x69] = instructions.OUT_C_r(memory, pc_state, ports, self._reg_wrapper_l)
        self.instruction_ed_lookup[0x79] = instructions.OUT_C_r(memory, pc_state, ports, self._reg_wrapper_a)

        self.instruction_ed_lookup[0x42] = instructions.SBC_HL_r16(memory, pc_state, self._reg_wrapper_bc)
        self.instruction_ed_lookup[0x43] = instructions.LD_nn_BC(memory, pc_state)
        self.instruction_ed_lookup[0x44] = instructions.NEG(memory, pc_state)
        self.instruction_ed_lookup[0x47] = instructions.LD_I_A(memory, pc_state)
        self.instruction_ed_lookup[0x4A] = instructions.ADC_HL_r16(memory, pc_state, self._reg_wrapper_bc)
        self.instruction_ed_lookup[0x4B] = instructions.LD_BC_nn(memory, pc_state)
        self.instruction_ed_lookup[0x4D] = instructions.RETI(memory, pc_state)
        self.instruction_ed_lookup[0x52] = instructions.SBC_HL_r16(memory, pc_state, self._reg_wrapper_de)
        self.instruction_ed_lookup[0x53] = instructions.LD_nn_DE(memory, pc_state)
        self.instruction_ed_lookup[0x56] = instructions.IM_1(memory, pc_state)
        self.instruction_ed_lookup[0x57] = instructions.LD_A_I(memory, pc_state)
        self.instruction_ed_lookup[0x5A] = instructions.ADC_HL_r16(memory, pc_state, self._reg_wrapper_de)
        self.instruction_ed_lookup[0x5B] = instructions.LD_DE_nn(memory, pc_state)
        self.instruction_ed_lookup[0x5F] = instructions.LD_A_R(memory, pc_state)
        self.instruction_ed_lookup[0x62] = instructions.SBC_HL_r16(memory, pc_state, self._reg_wrapper_hl)
        self.instruction_ed_lookup[0x63] = instructions.LD_nn_HL(memory, pc_state)
        self.instruction_ed_lookup[0x67] = instructions.RRD(memory, pc_state)
        self.instruction_ed_lookup[0x6A] = instructions.ADC_HL_r16(memory, pc_state, self._reg_wrapper_hl)
        self.instruction_ed_lookup[0x6B] = instructions.LD_HL_nn(memory, pc_state)
        self.instruction_ed_lookup[0x72] = instructions.SBC_HL_r16(memory, pc_state, self._reg_wrapper_sp)
        self.instruction_ed_lookup[0x73] = instructions.LD_nn_SP(memory, pc_state)
        self.instruction_ed_lookup[0x7A] = instructions.ADC_HL_r16(memory, pc_state, self._reg_wrapper_sp)
        self.instruction_ed_lookup[0x7B] = instructions.LD_SP_nn(memory, pc_state)
        self.instruction_ed_lookup[0xA0] = instructions.LDI(memory, pc_state)
        self.instruction_ed_lookup[0xA1] = instructions.CPI(memory, pc_state)
        self.instruction_ed_lookup[0xA2] = instructions.INI(memory, pc_state, ports)
        self.instruction_ed_lookup[0xA3] = instructions.OUTI(memory, pc_state, ports)
        self.instruction_ed_lookup[0xAB] = instructions.OUTD(memory, pc_state, ports)
        self.instruction_ed_lookup[0xB0] = instructions.LDIR(memory, pc_state)
        self.instruction_ed_lookup[0xB1] = instructions.CPIR(memory, pc_state)
        self.instruction_ed_lookup[0xB3] = instructions.OTIR(memory, pc_state, ports)
        self.instruction_ed_lookup[0xB8] = instructions.LDDR(memory, pc_state)

    def _populate_extended_dd_instruction_map(self, pc_state, memory):
        self.instruction_dd_lookup[0x09] = instructions.ADD16(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_bc,15,2);
        self.instruction_dd_lookup[0x19] = instructions.ADD16(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_de,15,2);
        self.instruction_dd_lookup[0x23] = instructions.INC_16(memory, pc_state, self._reg_wrapper_ix, 10,2);
        self.instruction_dd_lookup[0x29] = instructions.ADD16(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_ix,15,2);
        self.instruction_dd_lookup[0x2B] = instructions.DEC_16(memory, pc_state, self._reg_wrapper_ix, 10,2);
        self.instruction_dd_lookup[0x39] = instructions.ADD16(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_sp,15,2);

        self.instruction_dd_lookup[0x21] = instructions.LD_I_nn(memory, pc_state, self._reg_wrapper_ix)
        self.instruction_dd_lookup[0x22] = instructions.LD_nn_I(memory, pc_state, self._reg_wrapper_ix)
        self.instruction_dd_lookup[0x2A] = instructions.LD_I__nn_(memory, pc_state, self._reg_wrapper_ix)
        self.instruction_dd_lookup[0x34] = instructions.INC_I_d(memory, pc_state, self._reg_wrapper_ix)
        self.instruction_dd_lookup[0x35] = instructions.DEC_I_d(memory, pc_state, self._reg_wrapper_ix)
        self.instruction_dd_lookup[0x36] = instructions.LD_I_d_n(memory, pc_state, self._reg_wrapper_ix)

        self.instruction_dd_lookup[0x46] = instructions.LD_r_I_e(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_b)
        self.instruction_dd_lookup[0x4E] = instructions.LD_r_I_e(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_c)
        self.instruction_dd_lookup[0x56] = instructions.LD_r_I_e(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_d)
        self.instruction_dd_lookup[0x5E] = instructions.LD_r_I_e(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_e)
        self.instruction_dd_lookup[0x66] = instructions.LD_r_I_e(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_h)
        self.instruction_dd_lookup[0x6E] = instructions.LD_r_I_e(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_l)
        self.instruction_dd_lookup[0x7E] = instructions.LD_r_I_e(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_a)

        self.instruction_dd_lookup[0x70] = instructions.LD_I_d_r(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_b)
        self.instruction_dd_lookup[0x71] = instructions.LD_I_d_r(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_c)
        self.instruction_dd_lookup[0x72] = instructions.LD_I_d_r(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_d)
        self.instruction_dd_lookup[0x73] = instructions.LD_I_d_r(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_e)
        self.instruction_dd_lookup[0x74] = instructions.LD_I_d_r(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_h)
        self.instruction_dd_lookup[0x75] = instructions.LD_I_d_r(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_l)
        self.instruction_dd_lookup[0x77] = instructions.LD_I_d_r(memory, pc_state, self._reg_wrapper_ix, self._reg_wrapper_a)

        self.instruction_dd_lookup[0x86] = instructions.ADDA_I_d(memory, pc_state, self._reg_wrapper_ix)
        self.instruction_dd_lookup[0x8E] = instructions.ADC_I_d(memory, pc_state, self._reg_wrapper_ix)
        self.instruction_dd_lookup[0x96] = instructions.SUB_I_d(memory, pc_state, self._reg_wrapper_ix)
        self.instruction_dd_lookup[0xA6] = instructions.AND_I_d(memory, pc_state, self._reg_wrapper_ix)
        self.instruction_dd_lookup[0xAE] = instructions.XOR_I_d(memory, pc_state, self._reg_wrapper_ix)
        self.instruction_dd_lookup[0xB6] = instructions.OR_I_d(memory, pc_state, self._reg_wrapper_ix)
        self.instruction_dd_lookup[0xBE] = instructions.CP_I_d(memory, pc_state, self._reg_wrapper_ix)

        self.instruction_dd_lookup[0xCB] = instructions.BIT_I_d(memory, pc_state, self._reg_wrapper_ix)
        self.instruction_dd_lookup[0xE1] = instructions.POP_I(memory, pc_state, self._reg_wrapper_ix)
        self.instruction_dd_lookup[0xE3] = instructions.EX_SP_I(memory, pc_state, self._reg_wrapper_ix)
        self.instruction_dd_lookup[0xE5] = instructions.PUSH_I(memory, pc_state, self._reg_wrapper_ix)
        self.instruction_dd_lookup[0xE9] = instructions.LD_PC_I(memory, pc_state, self._reg_wrapper_ix)

    def _populate_extended_cb_instruction_map(self, pc_state, memory):
        for extra in [0x0, 0x8, 0x10, 0x18, 0x20, 0x28, 0x30, 0x38]:
            self.instruction_cb_lookup[0x40 + extra] = instructions.BIT_r(memory, pc_state, self._reg_wrapper_b); # BIT r, cpu_state->B
            self.instruction_cb_lookup[0x41 + extra] = instructions.BIT_r(memory, pc_state, self._reg_wrapper_c); # BIT r, cpu_state->C
            self.instruction_cb_lookup[0x42 + extra] = instructions.BIT_r(memory, pc_state, self._reg_wrapper_d); # BIT r, cpu_state->D
            self.instruction_cb_lookup[0x43 + extra] = instructions.BIT_r(memory, pc_state, self._reg_wrapper_e); # BIT r, cpu_state->E
            self.instruction_cb_lookup[0x44 + extra] = instructions.BIT_r(memory, pc_state, self._reg_wrapper_h); # BIT r, cpu_state->H
            self.instruction_cb_lookup[0x45 + extra] = instructions.BIT_r(memory, pc_state, self._reg_wrapper_l); # BIT r, cpu_state->L
            self.instruction_cb_lookup[0x47 + extra] = instructions.BIT_r(memory, pc_state, self._reg_wrapper_a); # BIT r, cpu_state->A
            self.instruction_cb_lookup[0x46 + extra] = instructions.BIT_HL(memory, pc_state); # BIT HL
            self.instruction_cb_lookup[0x80 + extra] = instructions.RES_b_r(memory, pc_state, self._reg_wrapper_b); # RES r, cpu_state->B
            self.instruction_cb_lookup[0x81 + extra] = instructions.RES_b_r(memory, pc_state, self._reg_wrapper_c); # RES r, cpu_state->C
            self.instruction_cb_lookup[0x82 + extra] = instructions.RES_b_r(memory, pc_state, self._reg_wrapper_d); # RES r, cpu_state->D
            self.instruction_cb_lookup[0x83 + extra] = instructions.RES_b_r(memory, pc_state, self._reg_wrapper_e); # RES r, cpu_state->E
            self.instruction_cb_lookup[0x84 + extra] = instructions.RES_b_r(memory, pc_state, self._reg_wrapper_h); # RES r, cpu_state->H
            self.instruction_cb_lookup[0x85 + extra] = instructions.RES_b_r(memory, pc_state, self._reg_wrapper_l); # RES r, cpu_state->L
            self.instruction_cb_lookup[0x87 + extra] = instructions.RES_b_r(memory, pc_state, self._reg_wrapper_a); # RES r, cpu_state->A
            self.instruction_cb_lookup[0x86 + extra] = instructions.RES_b_HL(memory, pc_state); # RES b, cpu_state->HL

            self.instruction_cb_lookup[0xC0 + extra] = instructions.SET_b_r(memory, pc_state, self._reg_wrapper_b); # SET r, cpu_state->B
            self.instruction_cb_lookup[0xC1 + extra] = instructions.SET_b_r(memory, pc_state, self._reg_wrapper_c); # SET r, cpu_state->C
            self.instruction_cb_lookup[0xC2 + extra] = instructions.SET_b_r(memory, pc_state, self._reg_wrapper_d); # SET r, cpu_state->D
            self.instruction_cb_lookup[0xC3 + extra] = instructions.SET_b_r(memory, pc_state, self._reg_wrapper_e); # SET r, cpu_state->E
            self.instruction_cb_lookup[0xC4 + extra] = instructions.SET_b_r(memory, pc_state, self._reg_wrapper_h); # SET r, cpu_state->H
            self.instruction_cb_lookup[0xC5 + extra] = instructions.SET_b_r(memory, pc_state, self._reg_wrapper_l); # SET r, cpu_state->L
            self.instruction_cb_lookup[0xC7 + extra] = instructions.SET_b_r(memory, pc_state, self._reg_wrapper_a); # SET r, cpu_state->A
            self.instruction_cb_lookup[0xC6 + extra] = instructions.SET_b_HL(memory, pc_state); # SET b, cpu_state->HL

        # Non-masked op codes
        self.instruction_cb_lookup[0x00] = instructions.RLC_r(memory, pc_state, self._reg_wrapper_b); # RLC r, cpu_state->B
        self.instruction_cb_lookup[0x01] = instructions.RLC_r(memory, pc_state, self._reg_wrapper_c); # RLC r, cpu_state->C
        self.instruction_cb_lookup[0x02] = instructions.RLC_r(memory, pc_state, self._reg_wrapper_d); # RLC r, cpu_state->D
        self.instruction_cb_lookup[0x03] = instructions.RLC_r(memory, pc_state, self._reg_wrapper_e); # RLC r, cpu_state->E
        self.instruction_cb_lookup[0x04] = instructions.RLC_r(memory, pc_state, self._reg_wrapper_h); # RLC r, cpu_state->H
        self.instruction_cb_lookup[0x05] = instructions.RLC_r(memory, pc_state, self._reg_wrapper_l); # RLC r, cpu_state->L
        self.instruction_cb_lookup[0x07] = instructions.RLC_r(memory, pc_state, self._reg_wrapper_a); # RLC r, cpu_state->A
        self.instruction_cb_lookup[0x06] = instructions.RLC_HL(memory, pc_state); # RLC b, cpu_state->HL

        self.instruction_cb_lookup[0x08] = instructions.RRC_r(memory, pc_state, self._reg_wrapper_b); # RRC r, cpu_state->B
        self.instruction_cb_lookup[0x09] = instructions.RRC_r(memory, pc_state, self._reg_wrapper_c); # RRC r, cpu_state->C
        self.instruction_cb_lookup[0x0A] = instructions.RRC_r(memory, pc_state, self._reg_wrapper_d); # RRC r, cpu_state->D
        self.instruction_cb_lookup[0x0B] = instructions.RRC_r(memory, pc_state, self._reg_wrapper_e); # RRC r, cpu_state->E
        self.instruction_cb_lookup[0x0C] = instructions.RRC_r(memory, pc_state, self._reg_wrapper_h); # RRC r, cpu_state->H
        self.instruction_cb_lookup[0x0D] = instructions.RRC_r(memory, pc_state, self._reg_wrapper_l); # RRC r, cpu_state->L
        self.instruction_cb_lookup[0x0F] = instructions.RRC_r(memory, pc_state, self._reg_wrapper_a); # RRC r, cpu_state->A
        self.instruction_cb_lookup[0x0E] = instructions.RRC_HL(memory, pc_state); # RRC b, cpu_state->HL

        self.instruction_cb_lookup[0x10] = instructions.RL_r(memory, pc_state, self._reg_wrapper_b); # RL r, cpu_state->B
        self.instruction_cb_lookup[0x11] = instructions.RL_r(memory, pc_state, self._reg_wrapper_c); # RL r, cpu_state->C
        self.instruction_cb_lookup[0x12] = instructions.RL_r(memory, pc_state, self._reg_wrapper_d); # RL r, cpu_state->D
        self.instruction_cb_lookup[0x13] = instructions.RL_r(memory, pc_state, self._reg_wrapper_e); # RL r, cpu_state->E
        self.instruction_cb_lookup[0x14] = instructions.RL_r(memory, pc_state, self._reg_wrapper_h); # RL r, cpu_state->H
        self.instruction_cb_lookup[0x15] = instructions.RL_r(memory, pc_state, self._reg_wrapper_l); # RL r, cpu_state->L
        self.instruction_cb_lookup[0x17] = instructions.RL_r(memory, pc_state, self._reg_wrapper_a); # RL r, cpu_state->A

        self.instruction_cb_lookup[0x18] = instructions.RR_r(memory, pc_state, self._reg_wrapper_b); # RR r, cpu_state->B
        self.instruction_cb_lookup[0x19] = instructions.RR_r(memory, pc_state, self._reg_wrapper_c); # RR r, cpu_state->C
        self.instruction_cb_lookup[0x1A] = instructions.RR_r(memory, pc_state, self._reg_wrapper_d); # RR r, cpu_state->D
        self.instruction_cb_lookup[0x1B] = instructions.RR_r(memory, pc_state, self._reg_wrapper_e); # RR r, cpu_state->E
        self.instruction_cb_lookup[0x1C] = instructions.RR_r(memory, pc_state, self._reg_wrapper_h); # RR r, cpu_state->H
        self.instruction_cb_lookup[0x1D] = instructions.RR_r(memory, pc_state, self._reg_wrapper_l); # RR r, cpu_state->L
        self.instruction_cb_lookup[0x1F] = instructions.RR_r(memory, pc_state, self._reg_wrapper_a); # RR r, cpu_state->A

        self.instruction_cb_lookup[0x20] = instructions.SLA_r(memory, pc_state, self._reg_wrapper_b); # SLA r, cpu_state->B
        self.instruction_cb_lookup[0x21] = instructions.SLA_r(memory, pc_state, self._reg_wrapper_c); # SLA r, cpu_state->C
        self.instruction_cb_lookup[0x22] = instructions.SLA_r(memory, pc_state, self._reg_wrapper_d); # SLA r, cpu_state->D
        self.instruction_cb_lookup[0x23] = instructions.SLA_r(memory, pc_state, self._reg_wrapper_e); # SLA r, cpu_state->E
        self.instruction_cb_lookup[0x24] = instructions.SLA_r(memory, pc_state, self._reg_wrapper_h); # SLA r, cpu_state->H
        self.instruction_cb_lookup[0x25] = instructions.SLA_r(memory, pc_state, self._reg_wrapper_l); # SLA r, cpu_state->L
        self.instruction_cb_lookup[0x27] = instructions.SLA_r(memory, pc_state, self._reg_wrapper_a); # SLA r, cpu_state->A
        self.instruction_cb_lookup[0x26] = instructions.SLA_HL(memory, pc_state); # SLA b, cpu_state->HL

        self.instruction_cb_lookup[0x28] = instructions.SRA_r(memory, pc_state, self._reg_wrapper_b); # SRA r, cpu_state->B
        self.instruction_cb_lookup[0x29] = instructions.SRA_r(memory, pc_state, self._reg_wrapper_c); # SRA r, cpu_state->C
        self.instruction_cb_lookup[0x2A] = instructions.SRA_r(memory, pc_state, self._reg_wrapper_d); # SRA r, cpu_state->D
        self.instruction_cb_lookup[0x2B] = instructions.SRA_r(memory, pc_state, self._reg_wrapper_e); # SRA r, cpu_state->E
        self.instruction_cb_lookup[0x2C] = instructions.SRA_r(memory, pc_state, self._reg_wrapper_h); # SRA r, cpu_state->H
        self.instruction_cb_lookup[0x2D] = instructions.SRA_r(memory, pc_state, self._reg_wrapper_l); # SRA r, cpu_state->L
        self.instruction_cb_lookup[0x2F] = instructions.SRA_r(memory, pc_state, self._reg_wrapper_a); # SRA r, cpu_state->A
        self.instruction_cb_lookup[0x2E] = instructions.SRA_HL(memory, pc_state); # SRA b, cpu_state->HL

        self.instruction_cb_lookup[0x30] = instructions.SLL_r(memory, pc_state, self._reg_wrapper_b); # SLL r, cpu_state->B
        self.instruction_cb_lookup[0x31] = instructions.SLL_r(memory, pc_state, self._reg_wrapper_c); # SLL r, cpu_state->C
        self.instruction_cb_lookup[0x32] = instructions.SLL_r(memory, pc_state, self._reg_wrapper_d); # SLL r, cpu_state->D
        self.instruction_cb_lookup[0x33] = instructions.SLL_r(memory, pc_state, self._reg_wrapper_e); # SLL r, cpu_state->E
        self.instruction_cb_lookup[0x34] = instructions.SLL_r(memory, pc_state, self._reg_wrapper_h); # SLL r, cpu_state->H
        self.instruction_cb_lookup[0x35] = instructions.SLL_r(memory, pc_state, self._reg_wrapper_l); # SLL r, cpu_state->L
        self.instruction_cb_lookup[0x37] = instructions.SLL_r(memory, pc_state, self._reg_wrapper_a); # SLL r, cpu_state->A
        self.instruction_cb_lookup[0x36] = instructions.SLL_HL(memory, pc_state); # SLL b, cpu_state->HL

        self.instruction_cb_lookup[0x38] = instructions.SRL_r(memory, pc_state, self._reg_wrapper_b); # SRL r, cpu_state->B
        self.instruction_cb_lookup[0x39] = instructions.SRL_r(memory, pc_state, self._reg_wrapper_c); # SRL r, cpu_state->C
        self.instruction_cb_lookup[0x3A] = instructions.SRL_r(memory, pc_state, self._reg_wrapper_d); # SRL r, cpu_state->D
        self.instruction_cb_lookup[0x3B] = instructions.SRL_r(memory, pc_state, self._reg_wrapper_e); # SRL r, cpu_state->E
        self.instruction_cb_lookup[0x3C] = instructions.SRL_r(memory, pc_state, self._reg_wrapper_h); # SRL r, cpu_state->H
        self.instruction_cb_lookup[0x3D] = instructions.SRL_r(memory, pc_state, self._reg_wrapper_l); # SRL r, cpu_state->L
        self.instruction_cb_lookup[0x3F] = instructions.SRL_r(memory, pc_state, self._reg_wrapper_a); # SRL r, cpu_state->A
        self.instruction_cb_lookup[0x3E] = instructions.SRL_HL(memory, pc_state); # SRA b, cpu_state->HL

    def getInstruction(self, op_code):
      return self.instruction_lookup[op_code]

    def getExtendedCB(self, cb_op_code):
      return self.instruction_cb_lookup[cb_op_code]

    def getExtendedDD(self, dd_op_code):
      return self.instruction_dd_lookup[dd_op_code]

    def getExtendedED(self, ed_op_code):
      return self.instruction_ed_lookup[ed_op_code]

    def getExtendedFD(self, fd_op_code):
      return self.instruction_fd_lookup[fd_op_code]
