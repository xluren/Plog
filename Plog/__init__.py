#!/usr/bin/python 
import multiprocessing
import time,datetime
from Plog.read_conf import read_conf
import logging

def init_log_conf(log_config_option):
    logging_format=log_config_option["logging_format"]
    logging_level=log_config_option["logging_level"]
    logging_filename=log_config_option["logging_filename"]
    logging.basicConfig(
        format=logging_format,
        level=int(logging_level),
        filename=logging_filename
    )
    logging.warning("hello")

def transform_datetime(datetime_str,datetime_format):
    unix_time=datetime.datetime.strptime(datetime_str,datetime_format).timetuple()
    return time.mktime(unix_time)

def sink_deal_coroutine(sink_module,sink_option_dict,dict_queue):
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
            if dealing_time<=transformed_datetime<dealing_time+interval:
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
            if dealing_time<=transformed_datetime<dealing_time+interval:
                cur_dealing_time_list.append(dict_item)
            elif transformed_datetime>=dealing_time+interval:
                overread_list.append(dict_item)
            elif transformed_datetime<dealing_time:
                pass  
        logging.info("cur_dealing_time_list length is %d " % len(cur_dealing_time_list))
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
    log_config_option=option_dict["log_config"]
    init_log_conf(log_config_option=log_config_option)

    source_module_name=option_dict["source"]["source_module"]
    source_module=__import__("Plog.source.%s" % source_module_name,fromlist=["Plog.source"])

    channel_module_name=option_dict["channel"]["channel_module"]
    channel_module=__import__("Plog.channel.%s" % channel_module_name,fromlist=["Plog.channel"])


    sink_module_name=option_dict["sink"]["sink_module"]
    sink_module=__import__("Plog.sink.%s" % sink_module_name,fromlist=["Plog.sink"])

    source_iter=source_module.yield_line(source_option_dict=option_dict["source"])
    dict_queue=multiprocessing.JoinableQueue()

    produce_queue=multiprocessing.Process(
        target=channel_module.parse_str,
        args=(source_iter,option_dict["channel"],dict_queue)
        )

    consume_queue=multiprocessing.Process(
        target=consume_queue_timer,
        args=(sink_module,option_dict["sink"],dict_queue))

    produce_queue.start()
    consume_queue.start()
    produce_queue.join()
    consume_queue.join()
