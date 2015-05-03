Plog
====

Plog 是 "Parse Log" 的缩写,是一套处理日志流的框架，日志流格式可以是Apache，nginx等常规意义的日志格式，也可以是自定义格式

受[FlumeNG](http://flume.apache.org/)的启发，我把整个工程分成了三个部分:**source**,**channel** ,**sink**,我已经完成了主体的共有的可以抽象出来的功能，比如线程的同步互斥，消息的生产消费，处理时间间隔的控制，还有一些简单的source,channel and sink函数


下面是一个简单的配置文件:
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
logging_filename=/tmp/plog.Log

```


使用了[ConfigParse](https://docs.python.org/2/library/configparser.html)来解析配置文件


####source部分的设计思路

在这一部分，我们需要处理的是数据流的来源，他可能是file，可能是socket，可能是管道，但是我不关注你的数据来源格式是什么样的，因为我无法满足这些需要各式各样的数据来源需求，而你的需要是什么样的，你最清楚，那么你只要写一个**source**的插件就可以了,名字随意你定，你需要的是把你写的那个插件的名字，写到**plog.conf**里面，具体实例如下:


```
source_module=self-define-script-name
```
自定义source的具体实现，参看source module下的**plog/source/youself_define_source.py**

####channel部分
在这个部分,主要是对数据流的处理，你同样需要写一个 Python的脚本，名字随意你定，但是你需要写到 **plog.conf** 中，类似下方:
```
channel_module=filter_log
```
同样的你需要实现的channel可以参见 **plog/channel/youself_define_channel.py**


####sink 部分
在这个部分，你同样需要写一个Python脚本，他的名字同样取决于你的个人喜好，你需要的是把你写的那个插件的名字写到**plog.conf**，例如下方:
```
sink_module=cacheL2get_monitor
```
同样的你需要完成的脚本可以参见**plog/sink/youself_define_sink.py**


####如何跑一个测试
1.git clone https://github.com/xluren/Plog

2.cd ./Plog/demo && nohup sh gen_log.sh & 

3.cd .. && python plog.py -f plog.conf

4.you will see a file**/tmp/zabbix_send_info_cacheL2**,its contents like followings:
```
[xluren@test Plog]$ cat /tmp/zabbix_send_info_cacheL2 
test.145 cacheL2_200 57.000000
```



-----

个人的感慨，哎，说多了都是泪

In  China,we name Nov 11  as "Single Day",but in the day of  Nov 11 2014,I fix the bug of plog and also restruct it . So today  I am very happy,event more than that  I have a girlfriend :-)

