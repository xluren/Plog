import os 
import time 
class tail_log(object):
    """
        readme
    """
    def __init__(self,log_file):
        self.log_file=log_file

        self.log_inode=0
        self.exit_code=0

    def set_log_inode(self):
        self.log_inode=os.stat(self.log_file).st_ino
        
    def yield_line(self):
        with open(self.log_file,'r') as f:
            """
                some setting
                1.read start from the end of file
                2.set inode 
                3.reset exit_code 
            """
            f.seek(0,2)
            self.set_log_inode()
            self.exit_code=0

            while True:
                line=f.readline()
                if not line:
                    log_inode_new=os.stat(self.log_file).st_ino 
                    if log_inode_new!=self.log_inode:
                        print time.ctime()
                        self.exit_code=1
                        break
                    time.sleep(0.1)
                    continue
                yield line

    def read_log(self):
        while 1:
            for line in  self.yield_line():
                if self.exit_code==1:
                    time.sleep(0.1)
                    break
                yield line
#log_tail=tail_log(log_file='/home/xluren/project/python/cacheL2/test/output',interval=0)
#for i in log_tail.read_log():
#    print i
