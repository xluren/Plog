from tail_file.tail_file import tail_log
from parse_log.parse_log import parse_log
from read_conf.read_conf import read_conf
import datetime
import time


def transform_datetime(datetime_str,datetime_format):
    unix_time=datetime.datetime.strptime(datetime_str,datetime_format).timetuple()
    return time.mktime(unix_time)

def yield_output_inteval(inteval,line_iter,output):
    temp_time=time.time()
    dealing_time=temp_time-temp_time%inteval
    output_dict={}
    log_time=0
    output_dict[dealing_time]=[]
    for status,output in line_iter:
        if status == 0:
            log_time=transform_datetime(output["date_time"],datetime_format)
            if  dealing_time  <= log_time  <  dealing_time+inteval:
                output_dict[dealing_time].append(output)
            else :
                output_list=output_dict[dealing_time]
                yield dealing_time,output_list
                del output_dict[dealing_time]
                temp_time=time.time()
                dealing_time=temp_time-temp_time%inteval
                output_dict[dealing_time]=[]
                output_dict[dealing_time].append(output)
        else:
            now_time=time.time()
            if now_time >dealing_time+inteval+1:

                output_list=output_dict[dealing_time]
                yield dealing_time,output_list
                del output_dict[dealing_time]
                temp_time=time.time()
                dealing_time=temp_time-temp_time%inteval
                output_dict[dealing_time]=[]
                output_dict[dealing_time].append(output)



#with multiprocess and coroutine 
import multiprocessing
def receive():
    while 1:
        n=(yield)
        print  "i got you message ,i know u  have wrote result to  file"
        print  "i will  send with zabbix_send plugin_module"
        from plugin_module import zabbix_send
        zabbix_send.zabbix_send("hello")
        

def produce(q,inteval):
    #get  a  parse_log object log_parse.deal_log() return iter 
    log_parse=parse_log(regex=regex,dict_key=dict_key,yield_line=yield_line)

    #put out the result
    dict_iter=yield_output_inteval(inteval=inteval,line_iter=log_parse.deal_log(),output="./tmp/hello")
    i=0
    for key,value in  dict_iter:
        q.put((key,value))

def consume(q,inteval):

    r=receive()
    r.next()
    from plugin_module import apache_mod 
    key,value=q.get()
    apache_mod.calculte_iterm((key,value),"hello")
    r.send(key)

if __name__=="__main__":
    
    import sys
    run_mode="single"
    if len(sys.argv)==2:
        if sys.argv[1]=="multi":
            run_mode="multi"
    else :
        pass 

    config_option_dict=read_conf(config_file="./log_parse.conf").get_option_dict()
    log_file=config_option_dict["log_file"]
    dict_key=config_option_dict['dict_key'].split(',')
    regex=config_option_dict['regex']
    datetime_format=config_option_dict['datetime_format']
    inteval=float(config_option_dict['inteval'])

    #get a tail_log object and get  the line  iter which tail_log yield
    log_tail=tail_log(log_file=log_file)
    yield_line=log_tail.read_log()
    
    if run_mode=="single":
        #####with single thread##############################################################################

        #get  a  parse_log object log_parse.deal_log() return iter 
        log_parse=parse_log(regex=regex,dict_key=dict_key,yield_line=yield_line)

        #put out the result
        
        dict_iter=yield_output_inteval(inteval=inteval,line_iter=log_parse.deal_log(),output="./tmp/hello")
        from plugin_module import apache_mod 
        for key ,value in dict_iter: 
            print key,len(value)
            apache_mod.calculte_iterm((key,value),"hello")
        #####################################################################################################
    
    if run_mode=="multi":
        ##with multiprocessing###############################################################################
        q=multiprocessing.JoinableQueue()

        consumeQ=multiprocessing.Process(target=consume,args=(q,inteval))
        consumeQ.start()

        produceQ=multiprocessing.Process(target=produce,args=(q,inteval))
        produceQ.start()

        consumeQ.join()
        produceQ.join()
