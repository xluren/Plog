from tail_file.tail_file import tail_log
from parse_log.parse_log import parse_log
from read_conf.read_conf import read_conf
import datetime
import time


def transform_datetime(datetime_str,datetime_format):
    unix_time=datetime.datetime.strptime(datetime_str,datetime_format).timetuple()
    return time.mktime(unix_time)

def yield_output_inteval(inteval,line_iter,output):
    while 1:
        dealing_time=time.time()-time.time()%inteval
        output_dict={}
        log_time=0
        output_dict[dealing_time]=[]
        for status,output in line_iter:
            if status == 0:
                log_time=transform_datetime(output["date_time"],datetime_format)
                if  dealing_time < log_time < dealing_time+inteval+1:
                    output_dict[dealing_time].append(output)
                else:
                    #print "#"*5
                    #print "output_dict keys is :",output_dict.keys()
                    yield dealing_time,output_dict[dealing_time]
                    del output_dict[dealing_time]
                    dealing_time=time.time()-time.time()%inteval
                    output_dict[dealing_time]=[]
                    #print "#"*5
            else:
                now_time=time.time()
                if now_time > dealing_time+inteval+1:
                    #print "#"*5
                    #print "output_dict keys is :",output_dict.keys()
                    yield dealing_time,output_dict
                    del output_dict[dealing_time]
                    dealing_time=time.time()-time.time()%inteval
                    output_dict[dealing_time]=[]
                    #print "#"*5

'''
    paese config log
    log_file        :   the file we read and parse
    dict_key        :   the iterm's value  we parse from each line of the log_parse
    regex           :   the regex we used to parse log to get value
    datetime_format :   the datetime's format in in the log 
    inteval         :   the inteval between each output
'''
config_option_dict=read_conf(config_file="./log_parse.conf").get_option_dict()
log_file=config_option_dict["log_file"]
dict_key=config_option_dict['dict_key'].split(',')
regex=config_option_dict['regex']
datetime_format=config_option_dict['datetime_format']
inteval=float(config_option_dict['inteval'])

'''
    get a tail_log object
    and get  the line  iter which tail_log yield
'''
log_tail=tail_log(log_file=log_file)
yield_line=log_tail.read_log()

''' 
    get  a  parse_log object 
    log_parse.deal_log() return iter 
'''
log_parse=parse_log(regex=regex,dict_key=dict_key,yield_line=yield_line)

'''put out the result''' 
dict_iter=yield_output_inteval(inteval=inteval,line_iter=log_parse.deal_log(),output="./tmp/hello")
from plugin_module import apache_mod 
apache_mod.calculte_iterm(dict_iter,"hello")
'''for key,value in dict_iter:
    print "##########"*10
    print key,value
    print "##########"*10
'''
