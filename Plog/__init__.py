#!/usr/bin/python 
import threading
from Queue import Queue 
import time,datetime
from Plog.read_conf import read_conf
import logging
import sys,os
import smtplib,signal
from email.mime.text import MIMEText

def send_mail(mail_config_option,mail_content):
    
    mail_user=mail_config_option["mail_user"]
    mail_postfix=mail_config_option["mail_postfix"]
    mail_subject=mail_config_option["mail_subject"]
    mail_host=mail_config_option["mail_host"]
    mail_pass=mail_config_option["mail_pass"]
    mailto_list=mail_config_option["mailto_list"]

    mail_from = mail_user + "<"+mail_user+"@"+mail_postfix+">"
    try:
        msg = MIMEText(mail_content,_charset="utf-8")
        msg['Subject'] = mail_subject
        msg['From'] = mail_from
        msg['To'] = mailto_list
        send_smtp = smtplib.SMTP()
        send_smtp.connect(mail_host)
        send_smtp.login(mail_user, mail_pass)
        send_smtp.sendmail(mail_from, mailto_list,msg.as_string())
        send_smtp.close()
        return True
    except Exception, e:
        print str(e)
        return False

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

    mail_config_option=option_dict["mail_config"]

    source_module_name=option_dict["source"]["source_module"]
    source_module=__import__("Plog.source.%s" % source_module_name,fromlist=["Plog.source"])

    channel_module_name=option_dict["channel"]["channel_module"]
    channel_module=__import__("Plog.channel.%s" % channel_module_name,fromlist=["Plog.channel"])


    sink_module_name=option_dict["sink"]["sink_module"]
    sink_module=__import__("Plog.sink.%s" % sink_module_name,fromlist=["Plog.sink"])

    source_iter=source_module.yield_line(source_option_dict=option_dict["source"])

    dict_queue=Queue()
    thread_dict={}
    produce_queue=threading.Thread(
        target=channel_module.parse_str,
        args=(source_iter,option_dict["channel"],dict_queue)
        )

    consume_queue=threading.Thread(
        target=consume_queue_timer,
        args=(sink_module,option_dict["sink"],dict_queue))

    thread_dict["produce_queue"]=produce_queue
    thread_dict["consume_queue"]=consume_queue

    produce_queue.start()
    consume_queue.start()

    retry_time=10

    while 1:
        if len(threading.enumerate())!=3:
            retry_time-=1
            if retry_time == 0:
                pid=os.getpid()
                os.kill(pid,signal.SIGQUIT)
                send_mail(mail_config_option,"sth error,more than 10 times, so we kill it ")
            send_mail(mail_config_option,"sth error,check the log file to find out the reasone")
            if thread_dict["produce_queue"].isAlive()!=1:
                produce_queue=threading.Thread(
                    target=channel_module.parse_str,
                    args=(source_iter,option_dict["channel"],dict_queue)
                    )
                thread_dict["produce_queue"]=produce_queue
                produce_queue.start()
            if thread_dict["consume_queue"].isAlive()!=1:
                consume_queue=threading.Thread(
                    target=consume_queue_timer,
                    args=(sink_module,option_dict["sink"],dict_queue))
                thread_dict["consume_queue"]=consume_queue 
                consume_queue.start()
        else:
            time.sleep(120)
