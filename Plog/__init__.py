#!/usr/bin/python 
import threading
from Queue import Queue 
import time,datetime
from Plog.read_conf import read_conf
import logging
import sys,os

def make_daemon(home_dir,umask):
    try:
        pid = os.fork()
        if pid > 0:
            logging.info("first exit from  parent")
            sys.exit(0)
    except OSError, e:
        logging.error("first fork  error")
        sys.exit(1)
    os.chdir(home_dir)
    os.setsid()
    os.umask(umask)

    try:
        pid = os.fork()
        if pid > 0:
            logging.info("second exit from  parent")
            sys.exit(0)
    except OSError, e:
        logging.error("second fork  error")
        sys.exit(1)
     
def init_log_conf(log_config_option):
    logging_format=log_config_option["logging_format"]
    logging_level=log_config_option["logging_level"]
    logging_filename=log_config_option["logging_filename"]
    logging.basicConfig(
        format=logging_format,
        level=int(logging_level),
        filename=logging_filename
    )
    logging.info("init log  conf done ")


def consume_queue_timer(sink_module,sink_option_dict,dict_queue):

    interval=int(sink_option_dict["interval"])
    current_time=time.time()
    dealing_time=current_time-current_time%interval
    calculate_dict_item=sink_module.deal_sink(sink_option_dict=sink_option_dict)
    while 1:
        current_time=time.time()

        if current_time>dealing_time+interval:
            dealing_time=current_time-current_time%interval
            calculate_dict_item(dict_item="",timeout=1)
        else :
            dict_queue_size=dict_queue.qsize()
            if dict_queue.qsize()>0:
                dict_item=dict_queue.get()
                calculate_dict_item(dict_item=dict_item,timeout=0)

def start_work(conf_file):


    option_dict=read_conf.get_option_dict(conf_file)

    '''
        daemon config
    '''
    if option_dict["pid_config"]["daemon"]=="yes":
        make_daemon(home_dir=".",umask=022)

    '''
        log config
    '''
    log_config_option=option_dict["log_config"]
    init_log_conf(log_config_option=log_config_option)

    '''
        write pid into  pid file to
    '''
    pid_file=option_dict["pid_config"]["pid_file"]
    try:
        pid_file_handle=file(pid_file,'r')
        pid=int(pid_file_handle.read().strip())
    except:
        logging.error("open pid file error")
        pid=None

    if pid:
        try:
            pgid=os.getpgid(pid)
        except OSError :
            pid=os.getpid()
            with open(pid_file,"w") as pid_file_handle:
                pid_file_handle.write(str(pid))
        else:
            message = "pidfile %d already exists. Is it already running?\n"
            logging.error(message % pid)
            sys.stderr.write(message % pid)
            sys.exit(1)
    else:
        pid=os.getpid()
        with open(pid_file,"w") as pid_file_handle:
            pid_file_handle.write(str(pid))

    source_module_name=option_dict["source"]["source_module"]
    source_module=__import__("Plog.source.%s" % source_module_name,fromlist=["Plog.source"])

    channel_module_name=option_dict["channel"]["channel_module"]
    channel_module=__import__("Plog.channel.%s" % channel_module_name,fromlist=["Plog.channel"])


    sink_module_name=option_dict["sink"]["sink_module"]
    sink_module=__import__("Plog.sink.%s" % sink_module_name,fromlist=["Plog.sink"])

    source_iter=source_module.yield_line(source_option_dict=option_dict["source"])



    dict_queue=Queue()

    produce_queue=threading.Thread(
        target=channel_module.parse_str,
        args=(source_iter,option_dict["channel"],dict_queue)
        )

    consume_queue=threading.Thread(
        target=consume_queue_timer,
        args=(sink_module,option_dict["sink"],dict_queue))

    produce_queue.start()
    consume_queue.start()
