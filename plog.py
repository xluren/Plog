from Plog import start_work
from optparse import OptionParser
import os,sys
import signal


def signal_handler(sig, frame):
    a=os.getpid()
    print "kill ",a
    os.kill(a, signal.SIGQUIT)

if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = OptionParser() 
    parser.add_option("-f", "--file", dest="config_filename",
                            help="config file for parse log")
    (options, args) = parser.parse_args()
    if options.config_filename is None :
        print "config  file is none"
        sys.exit(1)
    else :
        config_file=options.config_filename


    start_work(config_file)
