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

def transform_datetime(datetime_str,datetime_format):
    unix_time=datetime.datetime.strptime(datetime_str,datetime_format).timetuple()
    return time.mktime(unix_time)

def sink_deal_coroutine(sink_module,sink_option_dict,dict_queue):
    '''
        overread_list to store the data we overread
        eg:
            the queue has the following data 1,2,3,4,5,6,7
            we just want to read the data le 5,
            so when we get 6 from queue,we stop ,but 6 belongs to the data we overread,
            I store it into overread_list,and at the next time ,when we consume queue,
            we will read consume the overread_list fist
        also ,how to judge we have to stop consuming the queue? when we read more than 
        10 items that we should not read.
        eg:
            the queue has the following data 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15
            we want to read the number which is less than 2,
            at the first time ,we got 1,that is what we want ,
            at the second time ,we got 2,that isn't we want 
            .
            .
            .
            at the eleven time ,we got 11,that isn't we want 
            at the same time ,we overread 10 numbers which i dont want ,so we should stop,
            also,the overread numbers are stored in overread_list.at the next ,we should deali
            the overread_list first.
    '''
    overread_list=[]
    cur_dealing_time_list=[]

    datetime_format=sink_option_dict["datetime_format"]
    interval=int(sink_option_dict["interval"])

    while 1:
        dealing_time=(yield)
        while 1:
            if len(overread_list)<=0:
                break
            dict_item=overread_list[0]
            transformed_datetime=transform_datetime(
                datetime_str=dict_item["date_time"],
                datetime_format=datetime_format
            )
            if transformed_datetime<dealing_time+interval:
                del overread_list[0]
            elif transformed_datetime>=dealing_time+interval:
                cur_dealing_time_list.append(dict_item)
            elif transformed_datetime<dealing_time:
                del overread_list[0]  
        dict_queue_size=dict_queue.qsize()
        while dict_queue.qsize()>0:
            if len(overread_list)>=10:
                break
            dict_item=dict_queue.get()
            transformed_datetime=transform_datetime(
                datetime_str=dict_item["date_time"],
                datetime_format=datetime_format
            )
            if transformed_datetime<dealing_time+interval:
                cur_dealing_time_list.append(dict_item)
            elif transformed_datetime>=dealing_time+interval:
                overread_list.append(dict_item)
            elif transformed_datetime<dealing_time:
                pass  
        logging.info("cur_dealing_time_list length is %d " % len(cur_dealing_time_list))

        sink_module.deal_sink(
                dict_list=cur_dealing_time_list,
                sink_option_dict=sink_option_dict)
        
        del cur_dealing_time_list[:]
        #sink_module.deal_sink(dict_list)

def consume_queue_timer(sink_module,sink_option_dict,dict_queue):

    interval=int(sink_option_dict["interval"])
    sink_deal_module=sink_deal_coroutine(sink_module,sink_option_dict,dict_queue)
    sink_deal_module.next()

    current_time=time.time()
    dealing_time=current_time-current_time%interval
    while 1:
        current_time=time.time()
        if dealing_time+interval > current_time:
            time.sleep(dealing_time+interval-current_time)
        else :
            current_time=time.time()
            sink_deal_module.send(dealing_time)
            dealing_time=current_time-current_time%interval
            

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
