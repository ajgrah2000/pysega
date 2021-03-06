# Collection is absed on:
# python -m cProfile -o profile.txt pysega.py ../atari2600/roms/Pitfall\!.bin 
#
# Collect stats with this script via:
# python -m pysega.python profile <pysega args>
#
# Results via:
#
# python -m pysega.python report [-c] [-t]
#

import cProfile
import pysega
import argparse
import pstats
import sys

def profile(profile_args):
  """ Run the c profiler using the specified arguments. 
  """

  cProfile.runctx('pysega.run(profile_args)', 
                  globals={'pysega':pysega}, 
                  locals={'profile_args':profile_args}, 
                  filename=profile_args.profile_filename)

def report(profile_args):
  """ Generate a profile report. 
  """

  p = pstats.Stats(profile_args.profile_filename)
  if profile_args.cumulative:
    p.sort_stats('cumulative').print_stats()

  if profile_args.tottime:
    p.sort_stats('tottime').print_stats()

def main():
  parser = argparse.ArgumentParser(description='Profiles the emulator. ', 
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('--filename', dest='profile_filename', action='store', default='profile.stats',
                      help="Name of the profile data file to create/read.")
  
  sub_parsers = parser.add_subparsers(help='Subparser commands.')
  report_args_parser  = sub_parsers.add_parser('report',  help='Display profile report data (-h for sub-command help)')

  profile_args_parser = sub_parsers.add_parser('profile', help='Generate new profile data.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # Populate the pysega sub command arguments.
  pysega.populate_pysega_argparser(profile_args_parser)

  report_args_parser.add_argument('-t', dest='tottime', action='store_true', default=False,
                            help="Output ordered by total time per function.")
  report_args_parser.add_argument('-c', dest='cumulative', action='store_true', default=False,
                            help="Output ordered by cumulative time per function.")

  # The command to execute is selected by setting a different default function
  # per command, to a common function name. 
  profile_args_parser.set_defaults(func=profile, stop_clock=8000000)

  report_args_parser.set_defaults(func=report)
  
  profiler_args = parser.parse_args()
  profiler_args.func(profiler_args) 

if __name__=='__main__':
  main()
