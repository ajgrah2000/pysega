""" Entry point for the sega emulator.
    Intended to work with python3, python2, pypy, pygame, pyglet, cyglfw.
"""

import argparse
from . import sega

# Possible audio drivers
audio_options = {
    'pygame':      'from pysega.audio.pygameaudio import PygameSound as AudioDriver',
    }

# Possible graphics drivers
graphics_options = {
    'pygame': 'from pysega.graphics.pygamevdp import PygameVDP as Graphics',
    'cyglfw': 'from pysega.graphics.cyglfwvdp import CyglfwVDP as Graphics',
    'pyglet': 'from pysega.graphics.pygletvdp import PygletVDP as Graphics'
    }

# Possible graphics drivers
cpu_options = {
    'cpu': 'import pysega.cpu as cpu'
    }

def config(graphics_selection, audio_selection, cpu_selection):
    # Use some questionable code to perform driver selection.
    # Imports only occur 'on-demand' so missing dependencies cause issues
    # unless you attempt to use them.
    exec_locals= {}
    exec(audio_options[audio_selection], {}, exec_locals)
    exec(graphics_options[graphics_selection], {}, exec_locals)
    exec(cpu_options[cpu_selection], {}, exec_locals)

    return (exec_locals['Graphics'], 
            exec_locals['AudioDriver'], 
            exec_locals['cpu'])

def run(args):
    (video, audio, cpu) = config(args.graphics_driver, args.audio_driver, args.cpu_driver)

    sms = sega.Sega(video, audio, cpu)

    sms.set_palette(args.palette)
    sms.insert_cartridge(args.cartridge_name)

    sms.power_on(args.stop_clock, args.no_delay, args.debug)

def get_pysega_argparser():
    parser = argparse.ArgumentParser(description='Sega emulator', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    populate_pysega_argparser(parser)
    return parser 

def populate_pysega_argparser(parser):
    parser.add_argument('cartridge_name',            action='store')
    parser.add_argument('-d', dest='debug',          action='store_true')
    parser.add_argument('-r', '--replay_file', dest='replay_file', type=str,
                              help="Json file to save/restore state. Triggered via '[',']' keys")
    parser.add_argument('-s', dest='stop_clock',     type=int, default=0,
                              help="Set a clock time to stop (useful for profiling), setting to '0' is disable stop")
    parser.add_argument('-p', dest='palette', 
                              choices=['ntsc', 'pal'], 
                              default='ntsc',
                              help="Select the palette to use (only changes color, not timing).")
    parser.add_argument('-g', dest='graphics_driver', 
                              choices=graphics_options.keys(), 
                              default='pygame',
                              help="Select an alternate to graphics module")
    parser.add_argument('--cpu', dest='cpu_driver', 
                              choices=cpu_options.keys(), 
                              default='cpu',
                              help="Select an alternate CPU emulation, primarily to allow trying different optimisations.")
    parser.add_argument('-a', dest='audio_driver', 
                              choices=audio_options.keys(), 
                              default='pygame',
                              help="Select an alternate CPU emulation, primarily to allow trying different optimisations.")
    parser.add_argument('-n', dest='no_delay',       action='store_true',
                              help="Wishful flag for when the emulator runs too fast.")

def main():
    parser = get_pysega_argparser()

    args = parser.parse_args()

    print(args)
                      
    run(args)

if __name__=='__main__':
    main()
