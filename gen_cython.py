import argparse
import subprocess
import os

def main():
    args = parse_args()

    try:
        os.mkdir(args.output_dir)
    except:
        pass

    src_dir = os.path.dirname(os.path.abspath(__file__))

    os.chdir(args.output_dir)

    p = subprocess.Popen(['cythonize','-b', '%s/run_pysega.py'%(src_dir),'%s/**/*.py'%(src_dir)])
    
    p.communicate()
    print "."
    
    for dirpath, dirnames, filenames in os.walk('pysega/'):
        p = subprocess.Popen(['touch','%s/__init__.py'%(dirpath)])
        for d in dirnames:
            p = subprocess.Popen(['touch','%s/%s/__init__.py'%(dirpath, d)])

def parse_args():
    parser = argparse.ArgumentParser(description='Sega emulator', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('output_dir', action='store')

    return parser.parse_args()

if __name__=='__main__':
    main()
