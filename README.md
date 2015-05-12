Plog
====

Plog is short for "Parse Log", it's a log-handle framework  designed for handling and analyzing log file generated from Apache, nginx etc.

Inspired by [FlumeNG](http://flume.apache.org/), I divied the project into four parts:**source**,**channel** ,**sink** and **common**. and I have complete the core the project  like the deal-interval-control,the thread-control ,also have completed some simple functions of source,channel and sink.

The following is a demo  configuration file.

```
[source]

source_module=file_source
source_file=./test/plog_demo.log 
source_interval=5


[channel]

channel_module=regrex_channel
channel_filter_regex=([\w\d.\s,]{0,})\s([0-9.]+)\s(\d+|-)\s(\w+)\s\[([^\[\]]+)\s\+\d+\]\s"((?:[^"]|\")+)"\s(\d{3})\s(\d+|-)\s"((?:[^"]|\")+|-)"\s"(.+|-)"\s"((?:[^"]|\")+)"\s"(.+|-)"$
channel_dict_key=domain_name,ip,response_time,TCP_status,date_time,request_url,response_code,size,ref,item1,agent,item2

[sink]

interval=60

sink_module=zabbix_sink
sink_service=cacheL2

sink_zabbix_send_file=/tmp/zabbix_send_info
sink_zabbix_sender=/usr/bin/zabbix_sender
sink_zabbix_conf=/etc/zabbix/zabbix_agentd.conf

[log_config]
logging_format=%(asctime)s %(filename)s [funcname:%(funcName)s] [line:%(lineno)d] %(levelname)s %(message)s
logging_level=20
logging_filename=/tmp/plog.log


```

I use [ConfigParse](https://docs.python.org/2/library/configparser.html) to parse the configue file.

####The Part of Source
In this part,we  deal with the input ,its type may be file ,exec,TCP socket ,and so on ,but I don't care about the type of ur input,you just need to complete a python script,and its name depends on ur inteest,what you need is to write the name in **plog.conf**,like following:
```
source_module=self-define-script-name
```
you  can read **plog/source/youself_define_source.py** to see what you should complete


####The Part of Channel
In this part,we deal with parsing log into some groups of value.you also need to complete a python script,and its name also depends on your interest,what you need is to write the name in **plog.conf**,like following:
```
channel_module=filter_log
```
also,you can read  **plog/channel/youself_define_channel.py** to get to know what you should complete


####The Part of Sink
In this part,you also need to complete a python script,and its name also depends on your interest,what you need is to write the name in **plog.conf**,like following:
```
sink_module=cacheL2get_monitor
```
you can read  **plog/sink/youself_define_sink.py** to get to know what you should complete


####How  To Run A Demo
1.git clone https://github.com/xluren/Plog

2.cd ./Plog/test 

3.nohup sh gen_log.sh & 

4.cd .. && python plog.py -c plog.conf

5.you will see a file**/tmp/zabbix_send_info_cacheL2**,its contents like followings:
```
[xluren@test Plog]$ cat /tmp/zabbix_send_info_cacheL2 
test.145 cacheL2_200 57.000000
```


-----

In  China,we name Nov 11  as "Single Day",but in the day of  Nov 11 2014,I fix the bug of plog and also restruct it . So today  I am very happy,event more than that  I have a girlfriend :-)

