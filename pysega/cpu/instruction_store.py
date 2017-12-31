from . import instructions
import addressing

class InstructionStore(object):
    def __init__(self, clocks, pc_state, ports, instruction_exe):
        self.clocks          = clocks
        self.pc_state        = pc_state
        self.ports           = ports
        self.instruction_exe = instruction_exe
#        self.instruction_lookup = [instructions.Instruction(self.clocks, self.pc_state, self.instruction_exe)] * 256
        self.instruction_lookup = [None] * 256
        self.instruction_cb_lookup = [None] * 256
        self.instruction_dd_lookup = [None] * 256
        self.instruction_ed_lookup = [None] * 256
        self.instruction_fd_lookup = [None] * 256

    def populate_instruction_map(self, clocks, pc_state, memory):
        self._initialise_register_wrappers(pc_state)

        self._populate_core_instruction_map(clocks, pc_state, memory)
        self._populate_extended_fd_instruction_map(clocks, pc_state, memory)
        self._populate_extended_ed_instruction_map(clocks, pc_state, memory)
        self._populate_extended_dd_instruction_map(clocks, pc_state, memory)
        self._populate_extended_cb_instruction_map(clocks, pc_state, memory)

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

    def _populate_core_instruction_map(self, clocks, pc_state, memory):

        self._instruction_exec = instructions.InstructionExec(pc_state)
        self.instruction_lookup[0xC3] = instructions.JumpInstruction(clocks, pc_state)
        self.instruction_lookup[0x31] = instructions.LD_16_nn(self.pc_state, self._reg_wrapper_sp); # LD DE, nn

# {
#     // Initialise the maps used to generate the register lookup.
#     initialiseRegisterLookup();
# 
#     instructions = new InstructionInterface *[0xff];
#     extendedFDInstructions = new InstructionInterface *[0xff];
#     extendedEDInstructions = new InstructionInterface *[0xff];
#     extendedDDInstructions = new InstructionInterface *[0xff];
#     extendedCBInstructions = new InstructionInterface *[0xff];
# 
#     for (int i = 0; i < 0xff; i++)
#     {
#         instructions[i] = NULL;
#         extendedFDInstructions[i] = NULL;
#         extendedEDInstructions[i] = NULL;
#         extendedDDInstructions[i] = NULL;
#         extendedCBInstructions[i] = NULL;
#     }
# 
        self.instruction_lookup[0x00] = instructions.Noop(self.clocks, pc_state);
        self.instruction_lookup[0x01] = instructions.Load16BC(pc_state, self._reg_wrapper_bc);
        self.instruction_lookup[0x02] = instructions.LD_mem_r(pc_state, self._reg_wrapper_bc, self._reg_wrapper_a); # LD (BC), A
        self.instruction_lookup[0x03] = instructions.INC_BC(pc_state); # INC cpu_state->BC
        self.instruction_lookup[0x04] = instructions.INC_r(pc_state, self._reg_wrapper_b); # INC cpu_state->B
        self.instruction_lookup[0x06] = instructions.LD_r(pc_state, self._reg_wrapper_b);
        self.instruction_lookup[0x07] = instructions.RLCA(pc_state);  #RLCA
        self.instruction_lookup[0x09] = instructions.ADD16(pc_state, self._reg_wrapper_hl,
                                       self._reg_wrapper_bc,11);
        self.instruction_lookup[0x0A] = instructions.LD_r_mem(pc_state, self._reg_wrapper_a, self._reg_wrapper_bc); # LD A, (BC)
        self.instruction_lookup[0x0B] = instructions.DEC_16(pc_state, self._reg_wrapper_bc, 6);
        self.instruction_lookup[0x0C] = instructions.INC_r(pc_state, self._reg_wrapper_c); # INC C
        self.instruction_lookup[0x0E] = instructions.LD_r(pc_state, self._reg_wrapper_c); # LD C, n
        self.instruction_lookup[0x0F] = instructions.RRCA(pc_state);
        self.instruction_lookup[0x10] = instructions.DJNZ(pc_state); # DJNZ n
        self.instruction_lookup[0x11] = instructions.LD_16_nn(pc_state, self._reg_wrapper_de); # LD DE, nn
        self.instruction_lookup[0x12] = instructions.LD_mem_r(pc_state, self._reg_wrapper_de, self._reg_wrapper_a); # LD (DE), A
        self.instruction_lookup[0x21] = instructions.LD_16_nn(pc_state, self._reg_wrapper_hl); # LD HL, nn
        self.instruction_lookup[0x2A] = instructions.LD_r16_mem(pc_state, self._reg_wrapper_hl); # LD HL, (nn)
        self.instruction_lookup[0x31] = instructions.LD_16_nn(pc_state, self._reg_wrapper_sp); # LD DE, nn
        self.instruction_lookup[0x13] = instructions.INC_16(pc_state, self._reg_wrapper_de, 6);
        self.instruction_lookup[0x14] = instructions.INC_r(pc_state, self._reg_wrapper_d); # INC D
        self.instruction_lookup[0x16] = instructions.LD_r(pc_state, self._reg_wrapper_d); # LD D, n
        self.instruction_lookup[0x19] = instructions.ADD16(pc_state, self._reg_wrapper_hl,
                                       self._reg_wrapper_de,11);
        self.instruction_lookup[0x1A] = instructions.LD_r_mem(pc_state, self._reg_wrapper_a, self._reg_wrapper_de); # LD A, (DE)
        self.instruction_lookup[0x1B] = instructions.DEC_16(pc_state, self._reg_wrapper_de, 6);
 
        self.instruction_lookup[0x1C] = instructions.INC_r(pc_state, self._reg_wrapper_e); # INC E
        self.instruction_lookup[0x1E] = instructions.LD_r(pc_state, self._reg_wrapper_e); # LD E, n
 
        self.instruction_lookup[0x20] = instructions.JRNZe(pc_state); # JR NZ, e
 
        self.instruction_lookup[0x23] = instructions.INC_16(pc_state, self._reg_wrapper_hl, 6);
 
        self.instruction_lookup[0x24] = instructions.INC_r(pc_state, self._reg_wrapper_h); # INC H
        self.instruction_lookup[0x26] = instructions.LD_r(pc_state, self._reg_wrapper_h); # LD H, n
        self.instruction_lookup[0x28] = instructions.JRZe(pc_state); # JR Z, e
        self.instruction_lookup[0x29] = instructions.ADD16(pc_state, self._reg_wrapper_hl,
                                       self._reg_wrapper_hl,11);
        self.instruction_lookup[0x2B] = instructions.DEC_16(pc_state, self._reg_wrapper_hl, 6);
 
        self.instruction_lookup[0x2C] = instructions.INC_r(pc_state, self._reg_wrapper_l); # INC L
        self.instruction_lookup[0x2E] = instructions.LD_r(pc_state, self._reg_wrapper_l); # LD L, n
        self.instruction_lookup[0x33] = instructions.INC_16(pc_state, self._reg_wrapper_sp, 6);
        self.instruction_lookup[0x34] = instructions.INC_HL(pc_state); # INC HL
        self.instruction_lookup[0x35] = instructions.DEC_HL(pc_state); # DEC HL
 
        self.instruction_lookup[0x36] = instructions.LD_mem_n(pc_state, self._reg_wrapper_hl); # LD (HL), n
 
        self.instruction_lookup[0x39] = instructions.ADD16(pc_state, self._reg_wrapper_hl,
                                       self._reg_wrapper_sp,11);
 
        self.instruction_lookup[0x3A] = instructions.LD_r8_mem(pc_state, self._reg_wrapper_a); # LD A, (n)
        self.instruction_lookup[0x3B] = instructions.DEC_16(pc_state, self._reg_wrapper_sp, 6);
        self.instruction_lookup[0x3C] = instructions.INC_r(pc_state, self._reg_wrapper_a); # INC A
        self.instruction_lookup[0x3E] = instructions.LD_r(pc_state, self._reg_wrapper_a); # LD A, n
 
        self.instruction_lookup[0x70] = instructions.LD_mem_r(pc_state, self._reg_wrapper_hl, self._reg_wrapper_b); # LD (HL), B
        self.instruction_lookup[0x71] = instructions.LD_mem_r(pc_state, self._reg_wrapper_hl, self._reg_wrapper_c); # LD (HL), C
        self.instruction_lookup[0x72] = instructions.LD_mem_r(pc_state, self._reg_wrapper_hl, self._reg_wrapper_d); # LD (HL), D
        self.instruction_lookup[0x73] = instructions.LD_mem_r(pc_state, self._reg_wrapper_hl, self._reg_wrapper_e); # LD (HL), E
        self.instruction_lookup[0x74] = instructions.LD_mem_r(pc_state, self._reg_wrapper_hl, self._reg_wrapper_h); # LD (HL), H
        self.instruction_lookup[0x75] = instructions.LD_mem_r(pc_state, self._reg_wrapper_hl, self._reg_wrapper_l); # LD (HL), L
        self.instruction_lookup[0x77] = instructions.LD_mem_r(pc_state, self._reg_wrapper_hl, self._reg_wrapper_a); # LD (HL), A
 
        self.instruction_lookup[0x80] = instructions.ADD_r(pc_state, self._reg_wrapper_b); # ADD r, cpu_state->A
        self.instruction_lookup[0x81] = instructions.ADD_r(pc_state, self._reg_wrapper_c); # ADD r, cpu_state->A
        self.instruction_lookup[0x82] = instructions.ADD_r(pc_state, self._reg_wrapper_d); # ADD r, cpu_state->A
        self.instruction_lookup[0x83] = instructions.ADD_r(pc_state, self._reg_wrapper_e); # ADD r, cpu_state->A
        self.instruction_lookup[0x84] = instructions.ADD_r(pc_state, self._reg_wrapper_h); # ADD r, cpu_state->A
        self.instruction_lookup[0x85] = instructions.ADD_r(pc_state, self._reg_wrapper_l); # ADD r, cpu_state->A
        self.instruction_lookup[0x87] = instructions.ADD_r(pc_state, self._reg_wrapper_a); # ADD r, cpu_state->A
 
        self.instruction_lookup[0xA0] = instructions.AND_r(pc_state, self._reg_wrapper_b); # AND r, cpu_state->A
        self.instruction_lookup[0xA1] = instructions.AND_r(pc_state, self._reg_wrapper_c); # AND r, cpu_state->A
        self.instruction_lookup[0xA2] = instructions.AND_r(pc_state, self._reg_wrapper_d); # AND r, cpu_state->A
        self.instruction_lookup[0xA3] = instructions.AND_r(pc_state, self._reg_wrapper_e); # AND r, cpu_state->A
        self.instruction_lookup[0xA4] = instructions.AND_r(pc_state, self._reg_wrapper_h); # AND r, cpu_state->A
        self.instruction_lookup[0xA5] = instructions.AND_r(pc_state, self._reg_wrapper_l); # AND r, cpu_state->A
        self.instruction_lookup[0xA7] = instructions.AND_r(pc_state, self._reg_wrapper_a); # AND r, cpu_state->A
 
        self.instruction_lookup[0xA8] = instructions.XOR_r(pc_state, self._reg_wrapper_b); # XOR r, cpu_state->A
        self.instruction_lookup[0xA9] = instructions.XOR_r(pc_state, self._reg_wrapper_c); # XOR r, cpu_state->A
        self.instruction_lookup[0xAA] = instructions.XOR_r(pc_state, self._reg_wrapper_d); # XOR r, cpu_state->A
        self.instruction_lookup[0xAB] = instructions.XOR_r(pc_state, self._reg_wrapper_e); # XOR r, cpu_state->A
        self.instruction_lookup[0xAC] = instructions.XOR_r(pc_state, self._reg_wrapper_h); # XOR r, cpu_state->A
        self.instruction_lookup[0xAD] = instructions.XOR_r(pc_state, self._reg_wrapper_l); # XOR r, cpu_state->A
        self.instruction_lookup[0xAF] = instructions.XOR_r(pc_state, self._reg_wrapper_a); # XOR r, cpu_state->A
 
        self.instruction_lookup[0xB0] = instructions.OR_r(pc_state, self._reg_wrapper_b); # OR r, cpu_state->A
        self.instruction_lookup[0xB1] = instructions.OR_r(pc_state, self._reg_wrapper_c); # OR r, cpu_state->A
        self.instruction_lookup[0xB2] = instructions.OR_r(pc_state, self._reg_wrapper_d); # OR r, cpu_state->A
        self.instruction_lookup[0xB3] = instructions.OR_r(pc_state, self._reg_wrapper_e); # OR r, cpu_state->A
        self.instruction_lookup[0xB4] = instructions.OR_r(pc_state, self._reg_wrapper_h); # OR r, cpu_state->A
        self.instruction_lookup[0xB5] = instructions.OR_r(pc_state, self._reg_wrapper_l); # OR r, cpu_state->A
        self.instruction_lookup[0xB7] = instructions.OR_r(pc_state, self._reg_wrapper_a); # OR r, cpu_state->A
 
        self.instruction_lookup[0xB8] = instructions.CP_r(pc_state, self._reg_wrapper_b); # CP r, cpu_state->A
        self.instruction_lookup[0xB9] = instructions.CP_r(pc_state, self._reg_wrapper_c); # CP r, cpu_state->A
        self.instruction_lookup[0xBA] = instructions.CP_r(pc_state, self._reg_wrapper_d); # CP r, cpu_state->A
        self.instruction_lookup[0xBB] = instructions.CP_r(pc_state, self._reg_wrapper_e); # CP r, cpu_state->A
        self.instruction_lookup[0xBC] = instructions.CP_r(pc_state, self._reg_wrapper_h); # CP r, cpu_state->A
        self.instruction_lookup[0xBD] = instructions.CP_r(pc_state, self._reg_wrapper_l); # CP r, cpu_state->A
        self.instruction_lookup[0xBF] = instructions.CP_r(pc_state, self._reg_wrapper_a); # CP r, cpu_state->A
 
        self.instruction_lookup[0xD3] = instructions.OUT_n_A(pc_state, self.ports); # OUT (n), cpu_state->A
        self.instruction_lookup[0xD2] = instructions.JPNC(pc_state); # JP NC
        self.instruction_lookup[0xD9] = instructions.EXX(pc_state); # EXX
        self.instruction_lookup[0xDA] = instructions.JPCnn(pc_state); # JP C, nn
 
        self.instruction_lookup[0xE6] = instructions.AND_n(pc_state); # AND n
        self.instruction_lookup[0xFE] = instructions.CP_n(pc_state); # CP n

        self.instruction_lookup[0x05] = instructions.DEC_r(pc_state, self._reg_wrapper_b); # DEC B
        self.instruction_lookup[0x0d] = instructions.DEC_r(pc_state, self._reg_wrapper_c); # DEC C
        self.instruction_lookup[0x15] = instructions.DEC_r(pc_state, self._reg_wrapper_d); # DEC D
        self.instruction_lookup[0x1d] = instructions.DEC_r(pc_state, self._reg_wrapper_e); # DEC E
        self.instruction_lookup[0x25] = instructions.DEC_r(pc_state, self._reg_wrapper_h); # DEC H
        self.instruction_lookup[0x2d] = instructions.DEC_r(pc_state, self._reg_wrapper_l); # DEC L
        self.instruction_lookup[0x3d] = instructions.DEC_r(pc_state, self._reg_wrapper_a); # DEC A
# 
#     LD_R_MEM ld_r_hl;
#     ld_r_hl.reg8 = 0x46;
        self.instruction_lookup[0x46] = instructions.LD_r_mem(pc_state, self._reg_wrapper_b, self._reg_wrapper_hl); # LD_r_mem B
        self.instruction_lookup[0x4e] = instructions.LD_r_mem(pc_state, self._reg_wrapper_c, self._reg_wrapper_hl); # LD_r_mem C
        self.instruction_lookup[0x56] = instructions.LD_r_mem(pc_state, self._reg_wrapper_d, self._reg_wrapper_hl); # LD_r_mem D
        self.instruction_lookup[0x5e] = instructions.LD_r_mem(pc_state, self._reg_wrapper_e, self._reg_wrapper_hl); # LD_r_mem E
        self.instruction_lookup[0x66] = instructions.LD_r_mem(pc_state, self._reg_wrapper_h, self._reg_wrapper_hl); # LD_r_mem H
        self.instruction_lookup[0x6e] = instructions.LD_r_mem(pc_state, self._reg_wrapper_l, self._reg_wrapper_hl); # LD_r_mem L
        self.instruction_lookup[0x7e] = instructions.LD_r_mem(pc_state, self._reg_wrapper_a, self._reg_wrapper_hl); # LD_r_mem A
# 
#     LD_R_MEM ld_r_n;
#     ld_r_n.reg8 = 0x06;
        self.instruction_lookup[0x06] = instructions.LD_r(pc_state, self._reg_wrapper_b); # LD_r B
        self.instruction_lookup[0x0e] = instructions.LD_r(pc_state, self._reg_wrapper_c); # LD_r C
        self.instruction_lookup[0x16] = instructions.LD_r(pc_state, self._reg_wrapper_d); # LD_r D
        self.instruction_lookup[0x1e] = instructions.LD_r(pc_state, self._reg_wrapper_e); # LD_r E
        self.instruction_lookup[0x26] = instructions.LD_r(pc_state, self._reg_wrapper_h); # LD_r H
        self.instruction_lookup[0x2e] = instructions.LD_r(pc_state, self._reg_wrapper_l); # LD_r L
        self.instruction_lookup[0x3e] = instructions.LD_r(pc_state, self._reg_wrapper_a); # LD_r A

        for (i1, r1) in [(0, self._reg_wrapper_b), (1, self._reg_wrapper_c), (2, self._reg_wrapper_d), (3, self._reg_wrapper_e), (4, self._reg_wrapper_h), (5, self._reg_wrapper_l), (7, self._reg_wrapper_a)]:
          for (i2, r2) in [(0, self._reg_wrapper_b), (1, self._reg_wrapper_c), (2, self._reg_wrapper_d), (3, self._reg_wrapper_e), (4, self._reg_wrapper_h), (5, self._reg_wrapper_l), (7, self._reg_wrapper_a)]:
            self.instruction_lookup[0x40 + i1 + (i2 * 8)] = instructions.LD_r_r(pc_state, r2, r1) 

        self.instruction_lookup[0xC9] = instructions.RET(pc_state); # RET

    def _populate_extended_fd_instruction_map(self, clocks, pc_state, memory):
        self.instruction_fd_lookup[0x09] = instructions.ADD16(pc_state, self._reg_wrapper_iy,
                                       self._reg_wrapper_bc,15,2);
        self.instruction_fd_lookup[0x19] = instructions.ADD16(pc_state, self._reg_wrapper_iy,
                                       self._reg_wrapper_de,15,2);
        self.instruction_fd_lookup[0x23] = instructions.INC_16(pc_state, self._reg_wrapper_iy,
                                       10,2);
        self.instruction_fd_lookup[0x29] = instructions.ADD16(pc_state, self._reg_wrapper_iy,
                                       self._reg_wrapper_iy,15,2);
        self.instruction_fd_lookup[0x2B] = instructions.DEC_16(pc_state, self._reg_wrapper_iy, 10,2);
        self.instruction_fd_lookup[0x39] = instructions.ADD16(pc_state, self._reg_wrapper_iy,
                                       self._reg_wrapper_sp,15,2);

    def _populate_extended_ed_instruction_map(self, clocks, pc_state, memory):
        pass

    def _populate_extended_dd_instruction_map(self, clocks, pc_state, memory):
        self.instruction_dd_lookup[0x09] = instructions.ADD16(pc_state, self._reg_wrapper_ix,
                                       self._reg_wrapper_bc,15,2);
        self.instruction_dd_lookup[0x19] = instructions.ADD16(pc_state, self._reg_wrapper_ix,
                                       self._reg_wrapper_de,15,2);
        self.instruction_dd_lookup[0x23] = instructions.INC_16(pc_state, self._reg_wrapper_ix,
                                       10,2);
        self.instruction_dd_lookup[0x29] = instructions.ADD16(pc_state, self._reg_wrapper_ix,
                                       self._reg_wrapper_ix,15,2);
        self.instruction_dd_lookup[0x2B] = instructions.DEC_16(pc_state, self._reg_wrapper_ix, 10,2);
        self.instruction_dd_lookup[0x39] = instructions.ADD16(pc_state, self._reg_wrapper_ix,
                                       self._reg_wrapper_sp,15,2);

    def _populate_extended_cb_instruction_map(self, clocks, pc_state, memory):
        pass

    def getInstruction(self, op_code):
      instruction = None
      if self.instruction_lookup[op_code]:
          instruction = self.instruction_lookup[op_code]
      return instruction

    def getExtendedCB(self, cb_op_code):
      instruction = None
      if cb_op_code in self.instruction_cb_lookup:
          instruction = self.instruction_cb_lookup[cb_op_code]
      return instruction


    def getExtendedDD(self, dd_op_code):
      instruction = None
      if self.instruction_dd_lookup[dd_op_code]:
          instruction = self.instruction_dd_lookup[dd_op_code]
      return instruction

    def getExtendedED(self, ed_op_code):
      instruction = None
      if self.instruction_ed_lookup[ed_op_code]:
          instruction = self.instruction_ed_lookup[ed_op_code]
      return instruction

    def getExtendedFD(self, fd_op_code):
      instruction = None
      if self.instruction_ed_lookup[fd_op_code]:
          instruction = self.instruction_fd_lookup[fd_op_code]
      return instruction
