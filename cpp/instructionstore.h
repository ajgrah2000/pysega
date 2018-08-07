#ifndef INSTRUCTIONSTORE_H
#define INSTRUCTIONSTORE_H

#include <map>
#include "types.h"
#include "instructioninterface.h"

// Bit fields for register encoding.
#define REGISTER_A 111
#define REGISTER_B 000
#define REGISTER_C 001
#define REGISTER_D 010
#define REGISTER_E 011
#define REGISTER_H 100
#define REGISTER_L 101

typedef std::map<Byte, InstructionInterface *> InstructionMap;


class InstructionStore
{
    public:
         virtual ~InstructionStore();

         static InstructionStore *instance();
         InstructionInterface *getInstruction(const Byte *instructionAddress);
         InstructionInterface *getExtendedCB(const Byte *instructionAddress);
         InstructionInterface *getExtendedED(const Byte *instructionAddress);
         InstructionInterface *getExtendedDD(const Byte *instructionAddress);
         InstructionInterface *getExtendedFD(const Byte *instructionAddress);

         void dump();

    private:
        InstructionStore();

        static InstructionStore *self;
        virtual void initialiseRegisterLookup();
        virtual void initialise();
        virtual void initialiseExtendedFD();
        virtual void initialiseExtendedED();
        virtual void initialiseExtendedDD();
        virtual void initialiseExtendedCB();

        InstructionInterface** instructions;
        InstructionInterface** extendedEDInstructions;
        InstructionInterface** extendedDDInstructions;
        InstructionInterface** extendedCBInstructions;
        InstructionInterface** extendedFDInstructions;
        InstructionMap instruction_map;

        std::map<Byte, uint8 *> register_lookup;
        typedef std::map<Byte, uint8 *> register_lookup_Type;
        
        std::map<int, int> decode_map;
        uint32 totalMissing;
};

#endif 
