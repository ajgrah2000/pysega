OBJ = z80memory.o driver.o errors.o z80core.o vdp.o joystick.o \
	sound.o soundchannel.o sega.o input.o cpustate.o LD_Instructions.o \
	instructionstore.o instruction.o instructions.o flagtables.o \
	extendedinstructions.o ports.o opcodegenerator.o
#PROFILE=-pg
CFLAGS= -Wall $(PROFILE) -ggdb `sdl-config --cflags` -O3
#CC=g++-3.4
CC=g++

driver: $(OBJ)
	$(CC) $(CFLAGS) $(OBJ) `sdl-config --cflags --libs` -lpthread -o $@ 

clean: 
	rm -f driver *.o

%.o: %.cpp
	$(CC) -c $(CFLAGS) $< -o $@ 
# DO NOT DELETE

cpustate.o: cpustate.h types.h
driver.o: sega.h z80memory.h types.h z80core.h readInterface.h
driver.o: writeInterface.h interuptor.h interupt.h cpustate.h vdp.h input.h
driver.o: joystick.h /usr/include/sys/types.h /usr/include/features.h
driver.o: /usr/include/sys/cdefs.h /usr/include/bits/wordsize.h
driver.o: /usr/include/gnu/stubs.h /usr/include/gnu/stubs-32.h
driver.o: /usr/include/bits/types.h /usr/include/bits/typesizes.h
driver.o: /usr/include/time.h /usr/include/endian.h
driver.o: /usr/include/bits/endian.h /usr/include/sys/select.h
driver.o: /usr/include/bits/select.h /usr/include/bits/sigset.h
driver.o: /usr/include/bits/time.h /usr/include/sys/sysmacros.h
driver.o: /usr/include/bits/pthreadtypes.h sound.h soundchannel.h
driver.o: /usr/include/unistd.h /usr/include/bits/posix_opt.h
driver.o: /usr/include/bits/confname.h /usr/include/getopt.h
errors.o: errors.h
extendedinstructions.o: extendedinstructions.h instruction.h cpustate.h
extendedinstructions.o: types.h instructioninterface.h z80memory.h
extendedinstructions.o: instructionstore.h
flagtables.o: flagtables.h types.h
input.o: input.h joystick.h types.h readInterface.h /usr/include/sys/types.h
input.o: /usr/include/features.h /usr/include/sys/cdefs.h
input.o: /usr/include/bits/wordsize.h /usr/include/gnu/stubs.h
input.o: /usr/include/gnu/stubs-32.h /usr/include/bits/types.h
input.o: /usr/include/bits/typesizes.h /usr/include/time.h
input.o: /usr/include/endian.h /usr/include/bits/endian.h
input.o: /usr/include/sys/select.h /usr/include/bits/select.h
input.o: /usr/include/bits/sigset.h /usr/include/bits/time.h
input.o: /usr/include/sys/sysmacros.h /usr/include/bits/pthreadtypes.h
input.o: /usr/include/unistd.h /usr/include/bits/posix_opt.h
input.o: /usr/include/bits/confname.h /usr/include/getopt.h
input.o: /usr/include/signal.h /usr/include/bits/signum.h
input.o: /usr/include/bits/siginfo.h /usr/include/bits/sigaction.h
input.o: /usr/include/bits/sigcontext.h /usr/include/bits/sigstack.h
input.o: /usr/include/bits/sigthread.h /usr/include/pthread.h
input.o: /usr/include/sched.h /usr/include/bits/sched.h
input.o: /usr/include/bits/setjmp.h
instruction.o: instruction.h cpustate.h types.h instructioninterface.h
instruction.o: z80memory.h flagtables.h
instructions.o: instructions.h cpustate.h types.h instruction.h
instructions.o: instructioninterface.h z80memory.h extendedinstructions.h
instructions.o: flagtables.h
instructionstore.o: instructionstore.h types.h instructioninterface.h
instructionstore.o: z80memory.h instructions.h cpustate.h instruction.h
instructionstore.o: extendedinstructions.h
joystick.o: joystick.h types.h readInterface.h
ports.o: ports.h readInterface.h types.h writeInterface.h
sega.o: sega.h z80memory.h types.h z80core.h readInterface.h writeInterface.h
sega.o: interuptor.h interupt.h cpustate.h vdp.h input.h joystick.h
sega.o: /usr/include/sys/types.h /usr/include/features.h
sega.o: /usr/include/sys/cdefs.h /usr/include/bits/wordsize.h
sega.o: /usr/include/gnu/stubs.h /usr/include/gnu/stubs-32.h
sega.o: /usr/include/bits/types.h /usr/include/bits/typesizes.h
sega.o: /usr/include/time.h /usr/include/endian.h /usr/include/bits/endian.h
sega.o: /usr/include/sys/select.h /usr/include/bits/select.h
sega.o: /usr/include/bits/sigset.h /usr/include/bits/time.h
sega.o: /usr/include/sys/sysmacros.h /usr/include/bits/pthreadtypes.h sound.h
sega.o: soundchannel.h ports.h
soundchannel.o: soundchannel.h types.h /usr/include/math.h
soundchannel.o: /usr/include/features.h /usr/include/sys/cdefs.h
soundchannel.o: /usr/include/bits/wordsize.h /usr/include/gnu/stubs.h
soundchannel.o: /usr/include/gnu/stubs-32.h /usr/include/bits/huge_val.h
soundchannel.o: /usr/include/bits/mathdef.h /usr/include/bits/mathcalls.h
sound.o: sound.h types.h soundchannel.h writeInterface.h
sound.o: /usr/include/assert.h /usr/include/features.h
sound.o: /usr/include/sys/cdefs.h /usr/include/bits/wordsize.h
sound.o: /usr/include/gnu/stubs.h /usr/include/gnu/stubs-32.h
sound.o: /usr/include/time.h /usr/include/bits/types.h
sound.o: /usr/include/bits/typesizes.h
vdp.o: vdp.h types.h interupt.h interuptor.h readInterface.h writeInterface.h
vdp.o: errors.h joystick.h /usr/include/stdio.h /usr/include/features.h
vdp.o: /usr/include/sys/cdefs.h /usr/include/bits/wordsize.h
vdp.o: /usr/include/gnu/stubs.h /usr/include/gnu/stubs-32.h
vdp.o: /usr/include/bits/types.h /usr/include/bits/typesizes.h
vdp.o: /usr/include/libio.h /usr/include/_G_config.h /usr/include/wchar.h
vdp.o: /usr/include/bits/stdio_lim.h /usr/include/bits/sys_errlist.h
vdp.o: /usr/include/stdlib.h /usr/include/sys/types.h /usr/include/time.h
vdp.o: /usr/include/endian.h /usr/include/bits/endian.h
vdp.o: /usr/include/sys/select.h /usr/include/bits/select.h
vdp.o: /usr/include/bits/sigset.h /usr/include/bits/time.h
vdp.o: /usr/include/sys/sysmacros.h /usr/include/bits/pthreadtypes.h
vdp.o: /usr/include/alloca.h /usr/include/assert.h
z80core.o: z80core.h readInterface.h types.h writeInterface.h interuptor.h
z80core.o: interupt.h z80memory.h cpustate.h errors.h flagtables.h ports.h
z80core.o: instructionstore.h instructioninterface.h instruction.h
z80debug.o: z80debug.h /usr/include/stdio.h /usr/include/features.h
z80debug.o: /usr/include/sys/cdefs.h /usr/include/bits/wordsize.h
z80debug.o: /usr/include/gnu/stubs.h /usr/include/gnu/stubs-32.h
z80debug.o: /usr/include/bits/types.h /usr/include/bits/typesizes.h
z80debug.o: /usr/include/libio.h /usr/include/_G_config.h
z80debug.o: /usr/include/wchar.h /usr/include/bits/stdio_lim.h
z80debug.o: /usr/include/bits/sys_errlist.h
z80memory.o: z80memory.h types.h errors.h /usr/include/stdio.h
z80memory.o: /usr/include/features.h /usr/include/sys/cdefs.h
z80memory.o: /usr/include/bits/wordsize.h /usr/include/gnu/stubs.h
z80memory.o: /usr/include/gnu/stubs-32.h /usr/include/bits/types.h
z80memory.o: /usr/include/bits/typesizes.h /usr/include/libio.h
z80memory.o: /usr/include/_G_config.h /usr/include/wchar.h
z80memory.o: /usr/include/bits/stdio_lim.h /usr/include/bits/sys_errlist.h
z80memory.o: /usr/include/assert.h
