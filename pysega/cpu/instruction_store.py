from . import instructions
import addressing

class InstructionStore(object):
    def __init__(self, clocks, pc_state, instruction_exe):
        self.clocks = clocks
        self.pc_state = pc_state
        self.instruction_exe = instruction_exe
#        self.instruction_lookup = [instructions.Instruction(self.clocks, self.pc_state, self.instruction_exe)] * 256
        self.instruction_lookup = [None] * 256
        self.instruction_cb_lookup = [instructions.Instruction(self.clocks, self.pc_state, self.instruction_exe)] * 256
        self.instruction_dd_lookup = [instructions.Instruction(self.clocks, self.pc_state, self.instruction_exe)] * 256
        self.instruction_ed_lookup = [instructions.Instruction(self.clocks, self.pc_state, self.instruction_exe)] * 256
        self.instruction_fd_lookup = [instructions.Instruction(self.clocks, self.pc_state, self.instruction_exe)] * 256

    def populate_instruction_map(self, clocks, pc_state, memory):
        self._reg_wrapper_a = addressing.RegWrapper_A(pc_state)
        self._reg_wrapper_b = addressing.RegWrapper_B(pc_state)
        self._reg_wrapper_c = addressing.RegWrapper_C(pc_state)
        self._reg_wrapper_d = addressing.RegWrapper_D(pc_state)
        self._reg_wrapper_e = addressing.RegWrapper_E(pc_state)
        self._reg_wrapper_h = addressing.RegWrapper_H(pc_state)
        self._reg_wrapper_l = addressing.RegWrapper_L(pc_state)
        self._reg_wrapper_sp = addressing.RegWrapper_SP(pc_state)
        self._reg_wrapper_bc = addressing.RegWrapper_BC(pc_state)
        self._reg_wrapper_de = addressing.RegWrapper_DE(pc_state)
        self._reg_wrapper_hl = addressing.RegWrapper_HL(pc_state)
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
        self.instruction_lookup[0x00] = instructions.Noop(pc_state);
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
 
        self.instruction_lookup[0xD3] = instructions.OUT_n_A(pc_state); # OUT (n), cpu_state->A
        self.instruction_lookup[0xD2] = instructions.JPNC(pc_state); # JP NC
        self.instruction_lookup[0xD9] = instructions.EXX(pc_state); # EXX
        self.instruction_lookup[0xDA] = instructions.JPCnn(pc_state); # JP C, nn
 
        self.instruction_lookup[0xE6] = instructions.AND_n(pc_state); # AND n
        self.instruction_lookup[0xFE] = instructions.CP_n(pc_state); # CP n
# 
#     DEC_R dec_r;
#     dec_r.reg8 = 0x05;
# 
#     LD_R_MEM ld_r_hl;
#     ld_r_hl.reg8 = 0x46;
# 
#     LD_R_MEM ld_r_n;
#     ld_r_n.reg8 = 0x06;
# 
#     register_lookup_Type::iterator it_r1 = register_lookup.begin();
#     for (it_r1 = register_lookup.begin();
#          it_r1 != register_lookup.end();
#          ++it_r1)
#     {
#         dec_r.r = it_r1->first;
#         ld_r_hl.r = it_r1->first;
#         ld_r_n.r = it_r1->first;
#         instructions[dec_r.reg8] = new DEC_r(*(it_r1->second)); // DEC r
#         instructions[ld_r_hl.reg8] = new LD_r_mem(*(it_r1->second), CPUState::instance()->HL); // LD r, (HL)
#         instructions[ld_r_n.reg8] = new LD_r(*(it_r1->second)); // LD C, n
#     }
# 
#     // Generate all of the standard register load instructions
#     //
#     // LD r, r'
#     //
#     LD_Struct ld;
#     ld.reg8 = 0x40;
# 
#     it_r1 = register_lookup.begin();
#     register_lookup_Type::iterator it_r2 = register_lookup.begin();
#     for (it_r1 = register_lookup.begin();
#          it_r1 != register_lookup.end();
#          ++it_r1)
#     {
#         for (it_r2 = register_lookup.begin();
#              it_r2 != register_lookup.end();
#              ++it_r2)
#         {
#             ld.r1 = it_r1->first;
#             ld.r2 = it_r2->first;
# 
#             int instruction_code = ld.reg8;
# 
#             instructions[instruction_code] = new LD_r_r(*(it_r1->second), *(it_r2->second));
#         }
#     }
# 
# 
#     instructions[0xC9] = new RET(); // RET
# 
#     initialiseExtendedFD();
#     initialiseExtendedED();
#     initialiseExtendedDD();
#     initialiseExtendedCB();
# }
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
      if dd_op_code in self.instruction_dd_lookup:
          instruction = self.instruction_dd_lookup[dd_op_code]
      return instruction

    def getExtendedED(self, ed_op_code):
      instruction = None
      if ed_op_code in self.instruction_ed_lookup:
          instruction = self.instruction_ed_lookup[ed_op_code]
      return instruction

    def getExtendedFD(self, fd_op_code):
      instruction = None
      if fd_op_code in self.instruction_fd_lookup:
          instruction = self.instruction_fd_lookup[fd_op_code]
      return instruction
