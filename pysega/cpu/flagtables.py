
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
      FlagTables._flagTableInc8 = [None] * MAXBYTE
      FlagTables._flagTableDec8 = [None] * MAXBYTE

      FlagTables._flagTableOr = [None] * MAXBYTE
      FlagTables._flagTableAnd = [None] * MAXBYTE

      FlagTables._flagTableAdd = [[None] * MAXBYTE] * MAXBYTE
      FlagTables._flagTableSub = [[None] * MAXBYTE] * MAXBYTE

      FlagTables._createStatusInc8Table();
      FlagTables._createStatusDec8Table();
      FlagTables._createStatusOrTable();
      FlagTables._createStatusAndTable();
      FlagTables._createStatusAddTable();
      FlagTables._createStatusSubTable();

      # Inc 8
      status = pc_state.PC_StatusFlags()
      status.value = 0

      status.status.N = 0
      status.status.C = 0

      for i in range(FlagTables.MAXBYTE):
          if (i & 0x80): # Is negative
            status.status.S  = 1 # Is negative
          else:
            status.status.S  = 0 # Is negative
          if (i==0): # Is zero
            status.status.Z  = 1 # Is zero
          else:
            status.status.Z  = 0 # Is zero
          if ((i & 0xF) == 0): # Half carry 
            status.status.H  = 1 # Half carry 
          else:
            status.status.H  = 0 # Half carry 
          if (i==0x80): # Was 7F
            status.status.PV = 1 # Was 7F
          else:
            status.status.PV = 0 # Was 7F

          FlagTables._flagTableInc8[i] = status.value

      # Dec 8
      status.value = 0
      status.status.N = 1
      status.status.C = 0 # Carry unchanged, set to 0 to allow OR 

      for i in range(FlagTables.MAXBYTE):
          if (i & 0x80): # Is negative
            status.status.S  = 1 # Is negative
          else:
            status.status.S  = 0 # Is negative
          if (i==0): # Is zero
            status.status.Z  = 1 # Is zero
          else:
            status.status.Z  = 0 # Is zero
          if ((i & 0xF) == 0xF): # Half borrow
            status.status.H  = 1 # Half borrow
          else:
            status.status.H  = 0 # Half borrow
          if (i==0x7F): # Was 80 
            status.status.PV = 1 # Was 80 
          else:
            status.status.PV = 0 # Was 80 

          FlagTables._flagTableDec8[i] = status.value;

    @staticmethod
    def _createStatusInc8Table():
      # Inc 8
      status = pc_state.PC_StatusFlags()
      status.value = 0;
  
      status.status.N = 0;
      status.status.C = 0;
  
      for i in range(FlagTables.MAXBYTE):
          if (i & 0x80): # Is negative
            status.status.S = 1 # Is negative
          else:
            status.status.S = 0 # Is negative
          if (i==0): # Is zero
            status.status.Z  = 1 # Is zero
          else:
            status.status.Z  = 0 # Is zero
          if ((i & 0xF) == 0): # Half carry 
            status.status.H  = 1 # Half carry 
          else:
            status.status.H  = 0 # Half carry 
          if (i==0x80): # Was 7F
            status.status.PV = 1 # Was 7F
          else:
            status.status.PV = 0 # Was 7F
  
          FlagTables._flagTableInc8[i] = status.value;

    @staticmethod
    def _createStatusDec8Table():
      # Inc 8
      status = pc_state.PC_StatusFlags()
      status.value = 0
  
      status.status.N = 0
      status.status.C = 0 # Carry unchanged, set to 0 to allow OR 
  
      for i in range(FlagTables.MAXBYTE):
          if (i & 0x80): # Is negative
            status.status.S  = 1 # Is negative
          else:
            status.status.S  = 0 # Is negative
          if (i==0): # Is zero
            status.status.Z  = 1 # Is zero
          else:
            status.status.Z  = 0 # Is zero
          if ((i & 0xF) == 0xF): # Half borrow
            status.status.H  = 1 # Half borrow
          else:
            status.status.H  = 0 # Half borrow
          if (i==0x7F): # Was 80 
            status.status.PV = 1 # Was 80 
          else:
            status.status.PV = 0 # Was 80 
  
          FlagTables._flagTableDec8[i] = status.value;

    # Calculate flags associated with parity
    @staticmethod
    def _createStatusOrTable():
      # Calculate a parity lookup table
      status = pc_state.PC_StatusFlags()
  
      for i in range(FlagTables.MAXBYTE):
          status.value = 0
  
          status.status.PV = FlagTables._calculateParity(i)

          if (i == 0): # Zero
            status.status.Z = 1 # Zero
          else:
            status.status.Z = 0 # Zero

          if (i & 0x80): # Sign
            status.status.S = 1 # Sign
          else:
            status.status.S = 0 # Sign
  
          FlagTables._flagTableOr[i] = status.value;

    # Calculate flags associated with parity
    @staticmethod
    def _createStatusAndTable():
      # Calculate a parity lookup table
      status = pc_state.PC_StatusFlags();
  
      for i in range(FlagTables.MAXBYTE):
          status.value = 0;
  
          status.status.H = 1;
          status.status.PV = FlagTables._calculateParity(i);
          if (i == 0):
            status.status.Z = 1 # Zero
          else:
            status.status.Z = 0 # Zero

          if (i & 0x80): # Sign
            status.status.S = 1 # Sign
          else:
            status.status.S = 0 # Sign
  
          FlagTables._flagTableAnd[i] = status.value;

    @staticmethod
    def _createStatusAddTable():
      status = pc_state.PC_StatusFlags()
      # int16 r;
      # int8 rc;
      # int8 hr;
  
      for i in range(FlagTables.MAXBYTE):
          for j in range(FlagTables.MAXBYTE):
              r  = (i & 0xFF) + (j & 0xFF) # (char) i + (char) j;
              rc = ((i & 0xFF) + (j & 0xFF)) & 0xFF
              hr = (i & 0xF) + (j & 0xF);
  
              status.value = 0; 
              if (rc & 0x80):
                  status.status.S  = 1
              else:
                  status.status.S  = 0
              if (rc == 0):    # result zero
                  status.status.Z  = 1    # result zero
              else:
                  status.status.Z  = 0    # result zero
              if (hr & 0x10):
                  status.status.H  = 1
              else:
                  status.status.H  = 0
              if (rc != r):   # overflow
                  status.status.PV = 1   # overflow
              else:
                  status.status.PV = 0   # overflow
              status.status.N  = 0;
              r  = (i & 0xFF) + (j & 0xFF) # r  = ((char) i & 0xFF) + ((char) j & 0xFF);
              
              if (r & 0x100): #  Not sure about this one
                  status.status.C  = 1
              else:
                  status.status.C  = 0
  
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
                r  = (i & 0xFF) - (j & 0xFF) #r  = (char) i - (char) j;
                rc = ((i & 0xFF) - (j & 0xFF)) & 0xFF # rc = (char) i - (char) j;
                hr  = (i & 0xF) - (j & 0xF)
                status.value = 0
                if (rc & 0x80):
                    status.status.S  = 1
                else:
                    status.status.S  = 0

                if (r == 0):    # result zero
                  status.status.Z  = 1    # result zero
                else:
                  status.status.Z  = 0    # result zero
                if (hr & 0x10):
                  status.status.H  = 1
                else:
                  status.status.H  = 0
                if (rc != r):   # overflow
                  status.status.PV = 1   # overflow
                else:
                  status.status.PV = 0   # overflow

                status.status.N  = 1

                r  = (i & 0xFF) - (j & 0xFF) # r  = ((char) i & 0xFF) - ((char) j & 0xFF);
                if (r & 0x100): # cpu_state->Borrow (?) 
                  status.status.C  = 1 # cpu_state->Borrow (?) 
                else:
                  status.status.C  = 0 # cpu_state->Borrow (?) 
    
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
      return FlagTables._flagTableAdd[value1][value2]

    @staticmethod
    def getStatusSub(value1, value2):
      return FlagTables._flagTableSub[value1][value2]

    # Determine the parity flag (even = 1, odd = 0)
    @staticmethod
    def _calculateParity(a):

      # Calculate Parity
      p = 1
      # Step through each bit in the byte
      for b in range(8):
          p = (p ^ (a >> b)) & 0x1

      return p
