# pysega
python based sega master system  emulator

Python sega emulator
=========================

Sega Master System emulator written in Python.

Module dependencies:
   pygame (1.9.4) or cyglfw or pyglet
   numpy (optional)

usage: __main__.py [-h] [-d] [-r REPLAY_FILE] [-s STOP_CLOCK] [-p {ntsc,pal}]
                   [-g {pygame,cyglfw,pyglet}] [--cpu {cpu}]
                   [-a {sounddevice,pygame}] [-n]
                   cartridge_name

Sega emulator

positional arguments:
  cartridge_name

optional arguments:
  -h, --help            show this help message and exit
  -d
  -r REPLAY_FILE, --replay_file REPLAY_FILE
                        Json file to save/restore state. Triggered via '[',']'
                        keys (default: None)
  -s STOP_CLOCK         Set a clock time to stop (useful for profiling),
                        setting to '0' is disable stop (default: 0)
  -p {ntsc,pal}         Select the palette to use (only changes color, not
                        timing). (default: ntsc)
  -g {pygame,cyglfw,pyglet}
                        Select an alternate to graphics module (default:
                        pygame)
  --cpu {cpu}           Select an alternate CPU emulation, primarily to allow
                        trying different optimisations. (default: cpu)
  -a {sounddevice,pygame}
                        Select an alternate CPU emulation, primarily to allow
                        trying different optimisations. (default: pygame)
  -n                    Wishful flag for when the emulator runs too fast.
                        (default: False)

Keys
====
arrow keys - move
z - Fire A
x - Fire B
r - Reset

Example startup
===============
Examples (pygame audio by default, I struggle to get non-flakey audio, but pygame 1.9.4 on generates reasonable sound.):

python -m pysega myrom.sms

Issues:

TODO:
    - Improve Audio with python. With this chip, pygame produces reasonable
      results.  There's a trade between lag and buffer size. (pygame 1.9.1
      segfaults with audio, not sure if there's something wrong in my usage,
      but 1.9.4 appears ok).
    - Check instruction cycles (emulation appears tollerant to errors in cycles
      for each instruction, but would be good to get correct).
    - Add more regression tests
    - Add profiling tests
    - Add travis-ci, coverage checks.
