import sys,time,os,signal
def yield_line(source_option_dict):
    source_sleep_interval=int(source_option_dict["source_sleep_interval"])
    while 1:
        try:
            line=raw_input()
            if line:
                yield line
            else:
                time.sleep(source_sleep_interval)
        except EOFError:
            pid=os.getpid()
            os.kill(pid, signal.SIGQUIT)
            print "end of the file"
