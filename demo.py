from tail_file.tail_file import tail_log
from parse_log.parse_log import parse_log
from read_conf.read_conf import read_conf
import datetime
import time


def transform_datetime(datetime_str,datetime_format):
    unix_time=datetime.datetime.strptime(datetime_str,datetime_format).timetuple()
    return time.mktime(unix_time)

config_option_dict=read_conf(config_file="./log_parse.conf").get_option_dict()
log_file=config_option_dict["log_file"]
dict_key=config_option_dict['dict_key'].split(',')
regex=config_option_dict['regex']
datetime_format=config_option_dict['datetime_format']

log_tail=tail_log(log_file=log_file)
yield_line=log_tail.read_log()

log_parse=parse_log(regex=regex,
                    dict_key=dict_key,
                    yield_line=yield_line)

for status,output in log_parse.deal_log():
    if status == 0:
        print transform_datetime(output["date_time"],datetime_format)

