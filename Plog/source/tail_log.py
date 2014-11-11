import sys,os,time
import logging
def get_file_inode(file):
    try:
        file_ino=os.stat(file).st_ino
    except:
        try :
            file_ino=os.stat(file).st_ino
        except:
            logging.warning(file+" dosent exist")
            file_ino=0
    return file_ino
def read_file(file):
    tmp=""
    flag=1
    file_inode=get_file_inode(file)
    with open(file,"r") as file_handle:
        file_handle.seek(0,2)
        while 1:
            line=file_handle.readline()
            if not line:
                file_inode_now=get_file_inode(file)
                if file_inode_now!=file_inode:
                    logging.warning("inode change")
                    yield 1,"inode change"
                else:
                    continue
            else:
                if not line.endswith("\n"):
                    tmp+=line
                else:
                    line=tmp+line
                    tmp=""
                    yield 0,line

def yield_line(source_option_dict):
    file=source_option_dict["source_path"]
    while 1:
        func=read_file(file)
        for status,line in  func:
            if status == 1:
                time.sleep(0.1)
                break
            else:
                yield line
