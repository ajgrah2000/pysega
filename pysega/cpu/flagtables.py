from . import pc_state

def signed_char_to_int(value):
    result = value
    if (value & 0x80):
        result = value + 0xFF00
    return result

class FlagTables(object):
    MAXBYTE = 256
#    _flagTableInc8[MAXBYTE];
#    _flagTableDec8[MAXBYTE];
#
#    _flagTableOr[MAXBYTE];
#    _flagTableAnd[MAXBYTE];
#
#    _flagTableAdd[MAXBYTE][MAXBYTE];
#    _flagTableSub[MAXBYTE][MAXBYTE];

    @staticmethod
    def init():
      FlagTables._flagTableInc8 = [None] * FlagTables.MAXBYTE
      FlagTables._flagTableDec8 = [None] * FlagTables.MAXBYTE

      FlagTables._flagTableOr = [None] * FlagTables.MAXBYTE
      FlagTables._flagTableAnd = [None] * FlagTables.MAXBYTE

      FlagTables._flagTableAdd = [[None for i in range(FlagTables.MAXBYTE)] for j in range(FlagTables.MAXBYTE)]
      FlagTables._flagTableSub = [[None for i in range(FlagTables.MAXBYTE)] for j in range(FlagTables.MAXBYTE)]

      FlagTables._createStatusInc8Table();
      FlagTables._createStatusDec8Table();
      FlagTables._createStatusOrTable();
      FlagTables._createStatusAndTable();
      FlagTables._createStatusAddTable();
      FlagTables._createStatusSubTable();

      # Inc 8
      status = pc_state.PC_StatusFlags()
      status.value = 0

      status.N = 0
      status.C = 0

      for i in range(FlagTables.MAXBYTE):
          if (i & 0x80): # Is negative
            status.S  = 1 # Is negative
          else:
            status.S  = 0 # Is negative
          if (i==0): # Is zero
            status.Z  = 1 # Is zero
          else:
            status.Z  = 0 # Is zero
          if ((i & 0xF) == 0): # Half carry 
            status.H  = 1 # Half carry 
          else:
            status.H  = 0 # Half carry 
          if (i==0x80): # Was 7F
            status.PV = 1 # Was 7F
          else:
            status.PV = 0 # Was 7F

          FlagTables._flagTableInc8[i] = status.value

      # Dec 8
      status.value = 0
      status.N = 1
      status.C = 0 # Carry unchanged, set to 0 to allow OR 

      for i in range(FlagTables.MAXBYTE):
          if (i & 0x80): # Is negative
            status.S  = 1 # Is negative
          else:
            status.S  = 0 # Is negative
          if (i==0): # Is zero
            status.Z  = 1 # Is zero
          else:
            status.Z  = 0 # Is zero
          if ((i & 0xF) == 0xF): # Half borrow
            status.H  = 1 # Half borrow
          else:
            status.H  = 0 # Half borrow
          if (i==0x7F): # Was 80 
            status.PV = 1 # Was 80 
          else:
            status.PV = 0 # Was 80 

          FlagTables._flagTableDec8[i] = status.value;

    @staticmethod
    def _createStatusInc8Table():
      # Inc 8
      status = pc_state.PC_StatusFlags()
      status.value = 0;
  
      status.N = 0;
      status.C = 0;
  
      for i in range(FlagTables.MAXBYTE):
          if (i & 0x80): # Is negative
            status.S = 1 # Is negative
          else:
            status.S = 0 # Is negative
          if (i==0): # Is zero
            status.Z  = 1 # Is zero
          else:
            status.Z  = 0 # Is zero
          if ((i & 0xF) == 0): # Half carry 
            status.H  = 1 # Half carry 
          else:
            status.H  = 0 # Half carry 
          if (i==0x80): # Was 7F
            status.PV = 1 # Was 7F
          else:
            status.PV = 0 # Was 7F
  
          FlagTables._flagTableInc8[i] = status.value;

    @staticmethod
    def _createStatusDec8Table():
      # Inc 8
      status = pc_state.PC_StatusFlags()
      status.value = 0
  
      status.N = 0
      status.C = 0 # Carry unchanged, set to 0 to allow OR 
  
      for i in range(FlagTables.MAXBYTE):
          if (i & 0x80): # Is negative
            status.S  = 1 # Is negative
          else:
            status.S  = 0 # Is negative
          if (i==0): # Is zero
            status.Z  = 1 # Is zero
          else:
            status.Z  = 0 # Is zero
          if ((i & 0xF) == 0xF): # Half borrow
            status.H  = 1 # Half borrow
          else:
            status.H  = 0 # Half borrow
          if (i==0x7F): # Was 80 
            status.PV = 1 # Was 80 
          else:
            status.PV = 0 # Was 80 
  
          FlagTables._flagTableDec8[i] = status.value;

    # Calculate flags associated with parity
    @staticmethod
    def _createStatusOrTable():
      # Calculate a parity lookup table
      status = pc_state.PC_StatusFlags()
  
      for i in range(FlagTables.MAXBYTE):
          status.value = 0
  
          status.PV = FlagTables.calculateParity(i)

          if (i == 0): # Zero
            status.Z = 1 # Zero
          else:
            status.Z = 0 # Zero

          if (i & 0x80): # Sign
            status.S = 1 # Sign
          else:
            status.S = 0 # Sign
  
          FlagTables._flagTableOr[i] = status.value;

    # Calculate flags associated with parity
    @staticmethod
    def _createStatusAndTable():
      # Calculate a parity lookup table
      status = pc_state.PC_StatusFlags();
  
      for i in range(FlagTables.MAXBYTE):
          status.value = 0;
  
          status.H = 1;
          status.PV = FlagTables.calculateParity(i);
          if (i == 0):
            status.Z = 1 # Zero
          else:
            status.Z = 0 # Zero

          if (i & 0x80): # Sign
            status.S = 1 # Sign
          else:
            status.S = 0 # Sign
  
          FlagTables._flagTableAnd[i] = status.value;

    @staticmethod
    def _createStatusAddTable():
      status = pc_state.PC_StatusFlags()
  
      for i in range(FlagTables.MAXBYTE):
          for j in range(FlagTables.MAXBYTE):
              if (i & 0x80):
                a = i | 0xF00
              else:
                a = i
              if (j & 0x80):
                b = j | 0xF00
              else:
                b = j

              # overflow
              r = ((a & 0xFFF) + (b & 0xFFF)) & 0xFFF
              if (((r & 0x180) != 0) and 
                   (r & 0x180) != 0x180): # Overflow
                  status.PV = 1
              else:
                  status.PV = 0

              rc = ((i & 0xFF) + (j & 0xFF)) & 0xFF
              hr = (i & 0xF) + (j & 0xF);
  
              status.value = 0; 
              if (rc & 0x80):
                  status.S  = 1
              else:
                  status.S  = 0
              if (rc == 0):    # result zero
                  status.Z  = 1    # result zero
              else:
                  status.Z  = 0    # result zero
              if (hr & 0x10):
                  status.H  = 1
              else:
                  status.H  = 0

              status.N  = 0;
              r  = (i & 0xFF) + (j & 0xFF) # r  = ((char) i & 0xFF) + ((char) j & 0xFF);
              
              if (r & 0x100): #  Not sure about this one
                  status.C  = 1
              else:
                  status.C  = 0

#              print "%x %x, r=%x, rc=%x %s"%(i, j, r, rc, status)
  
              FlagTables._flagTableAdd[i][j] = status.value;

    # Calculate flags associated with subtraction
    # flagTableSub[cpu_state->A][cpu_state->B], represents cpu_state->A - cpu_state->B
    #
    @staticmethod
    def _createStatusSubTable():
        status = pc_state.PC_StatusFlags()
        #char rc;
        #int r;
        #int hr;
    
        for i in range(FlagTables.MAXBYTE):
            for j in range(FlagTables.MAXBYTE):
                r  = (signed_char_to_int(i & 0xFF) - signed_char_to_int(j & 0xFF)) & 0xFFFF#r  = (char) i - (char) j;
                rc = (signed_char_to_int(i & 0xFF) - signed_char_to_int(j & 0xFF)) & 0xFF # rc = (char) i - (char) j;
                hr  = (i & 0xF) - (j & 0xF)
                status.value = 0
                if (rc & 0x80):
                    status.S  = 1
                else:
                    status.S  = 0

                if (r == 0):    # result zero
                  status.Z  = 1    # result zero
                else:
                  status.Z  = 0    # result zero
                if (hr & 0x10):
                  status.H  = 1
                else:
                  status.H  = 0

                # overflow
                status.PV = 0
                if ((i < 0) and (j > 0)):
                    if (j >= (0x80 - (i ^ 0xff))):
                        status.PV = 1

                if ((i >= 0) and (j < 0)):
                    if ((i + 1) >= (((0x80 - (j ^ 0xff))) & 0xFF)):
                        status.PV = 1

                status.N  = 1

                r  = (i & 0xFF) - (j & 0xFF) # r  = ((char) i & 0xFF) - ((char) j & 0xFF);
                if (r & 0x100): # cpu_state->Borrow (?) 
                  status.C  = 1 # cpu_state->Borrow (?) 
                else:
                  status.C  = 0 # cpu_state->Borrow (?) 
    
                FlagTables._flagTableSub[i][j] = status.value

    @staticmethod
    def getStatusInc8(value):
      return FlagTables._flagTableInc8[value]

    @staticmethod
    def getStatusDec8(value):
      return FlagTables._flagTableDec8[value]

    @staticmethod
    def getStatusOr(value):
      return FlagTables._flagTableOr[value]

    @staticmethod
    def getStatusAnd(value):
      return FlagTables._flagTableAnd[value]

    @staticmethod
    def getStatusAdd(value1, value2):
      return FlagTables._flagTableAdd[int(value1)][int(value2)]

    @staticmethod
    def getStatusSub(value1, value2):
      return FlagTables._flagTableSub[int(value1)][int(value2)]

    # Determine the parity flag (even = 1, odd = 0)
    @staticmethod
    def calculateParity(a):

      # Calculate Parity
      p = 1
      # Step through each bit in the byte
      for b in range(8):
          p = (p ^ (a >> b)) & 0x1

      return p

