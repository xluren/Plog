Plog
====

Plog 是 "Parse Log" 的缩写,是一套处理日志流的框架，日志流格式可以是Apache，nginx等常规意义的日志格式，也可以是自定义格式

受[FlumeNG](http://flume.apache.org/)的启发，我把整个工程分成了三个部分:**source**,**channel** ,**sink **,我已经完成了主体的共有的可以抽象出来的功能，比如线程的同步互斥，消息的生产消费，处理时间间隔的控制，还有一些简单的source,channel and sink函数


下面是一个简单的配置文件:
```
[source]

#source 读取文件的间隔
source_sleep_interval=5

#source的一个模块
#这里有什么，取决于你souce的逻辑函数怎么写的,但是**source_module**是必须要有的
#我写的source只需要 **source_module** 和 **source_path**
source_module=tail_log
source_path=/home/xluren/project/Plog/demo/output

#另一个例子，从管道读取数据流
#source_module=read_from_pipeline

#再或者一个从某个端口，读取数据流
#source_module=read_from_tcp
#source_port=8899

[channel]
#channel主要是用来做过滤的
#channel_module是必须要有的，指定了你写的filter 函数

#channel_filter_regex,channel_dict_key 是由于我使用了正则，把数据流组成了dict，所以这俩我得需要下
channel_module=filter_log
channel_filter_regex=([\w\d.]{0,})\s([0-9.]+)\s(\d+|-)\s(\w+)\s\[([^\[\]]+)\s\+\d+\]\s"((?:[^"]|\")+)"\s(\d{3})\s(\d+|-)\s"((?:[^"]|\")+|-)"\s"(.+|-)"\s"((?:[^"]|\")+)"\s"(.+|-)"$
#
channel_dict_key=domain_name,ip,response_time,TCP_status,date_time,request_url,response_code,size,ref,item1,agent,item2

[sink]
#sink 主要是用来做最后的数据处理的，对filter清洗后的数据做聚合，做分发等操作
#处理时间是30s，这个是必须的
interval=30


#sink存储的文件位置，
sink_file=/tmp/hello

#sink的module是什么，这个是必须要有的
sink_module=cacheL2get_monitor

#下面是一个小例子
#读日志，解析日志，聚合，通过zabbix_sender 发给zabbix server作图等
#zabbix 发送的命令zabbix_sender -s proxy_server -i zabbix_send_info
#zabbix_send_info文件的内容如下:
#<host> <key> <value>
#eg:
#cat zabbix_send_info |less
#test001 TCP_HITS 59
#test001 TCP_MISS 0

#下面都是非必须的，但是对于sender给zabbix这个操作来说这些是需要的
#数据存储问文件
sink_zabbix_send_file=/tmp/zabbix_send_info
#服务前缀，也就是zabbix monitor key的前缀，一般为服务名字，为了避免重复
sink_zabbix_monitor_service=pic_cdn_
#zabbix 监控的key
sink_zabbix_monitor_keys=TCP_HIT,TCP_MISS,TCP_ERROR
#zabbix发送命令，trapper模式，直接在Python中调用了这个命令
sink_zabbix_send_cmd=/usr/bin/zabbix_sender -s proxy_server -i

[log_config]
#日志记录的配置
#使用了的是logger
logging_format=%(asctime)s %(filename)s [funcname:%(funcName)s] [line:%(lineno)d] %(levelname)s %(message)s
```


使用了[ConfigParse](https://docs.python.org/2/library/configparser.html)来解析配置文件

####整体的设计思想
尽可能的抽象出共用的东西，让每个使用者去写自由的写自己业务需要的那一部分

整个数据的流动类似流水的过程，

水从哪里来？source 

source是什么？可以是瀑布，可以是小河，可以是大海，至于从哪里流过来，取决于你自己

水到哪里去？channel 

channel是什么？去channel干什么？ channel是渠道，水要在渠道里面流，流的过程，顺便做了个净化处理，至于怎么净化，取决于你自己

水要到哪里去？sink 

sink是什么？类似出流出的口子，可以理解成水龙头

至于水龙头，想要水怎么流出，那就不知道了，你可以把水处理后 冻成冰，你可以把水处理后，做别的操作送出去，至于怎么做，取决于你自己

整个过程水流的管理，抽象出来，写好了，使用者如果感觉别人写的可以用，那就直接用，如果不好用，那就自己写插件吧

整个东西还是很low的，但是用起来还行 :-)


####source部分的设计思路

在这一部分，我们需要处理的是数据流的来源，他可能是file，可能是socket，可能是管道，但是我不关注你的数据来源格式是什么样的，因为我无法满足这些需要各式各样的数据来源需求，而你的需要是什么样的，你最清楚，那么你只要写一个**source**的插件就可以了,名字随意你定，你需要的是把你写的那个插件的名字，写到**plog.conf**里面，具体实例如下:


```
source_module=self-define-script-name
```

在这个插件里，你需要实现一个这样的函数:

```
def yield_line(source_option_dict):
```

*   函数的输入
    *   函数只有一个参数**source_option_dict**,他是一个字典类型的变量，里面含有你在plog.conf里面source option定义配置的所有的变量.
*   函数的输出
    *   输出是一个yield iter. 类似**yield line**,line 的来源取决于你读的是文件，还是socket，还是管道


####channel部分
在这个部分,主要是对数据流的处理，你同样需要写一个 Python的脚本，名字随意你定，但是你需要写到 **plog.conf** 中，类似下方:
```
channel_module=filter_log
```
同样的你还得需要完成一个这样的函数，类似下方:
```
def parse_str(source_iter,channel_option_dict,dict_queue):
```
*   函数的输入:
    *   **source_iter**,这是有source产生的迭代器;
    *   **channel_option_dict**,这部分包含了，所有channel需要的配置信息，取决于你在Plog.conf如何配置的
    *   **dict_queue**,一个Q，存储了一些字典类型的数据，而这个字典类型的数据是对source解析的结果.

**parse_str** 会遍历source iter并对数据进行解析，解析的结果会和 **channel_dict_key**一一对应的组成一个字典放到 **dict_queue**

*   函数的输出
    *   函数的输出是一个Q，Q作为两个线程的通信工具，这是一个dict类型的Q，存储了所有的解析数据，在这个函数中你不用写return，因为dict_queue 存储了解析的数据，同时他也被作为参数传进来了

####sink 部分
在这个部分，你同样需要写一个Python脚本，他的名字同样取决于你的个人喜好，你需要的是把你写的那个插件的名字写到**plog.conf**，例如下方:
```
sink_module=cacheL2get_monitor
```
同样的你还得需要完成一个这样的函数，类似下方:
```
    def deal_sink(dict_list,sink_option_dict):
```
*   函数的输入:
    *   **dict_list** the finaly result you need to deal, like calculating it ,storing it in a file  or send it through TCP soucket,and so on.
    *   **sink_option_dict** which contains all the option you need ,also you should configue what options you need in plog.conf
*   ouput:
    *   it's up to you,in the demo,i store the final result in a file, and call '**/usr/bin/zabbix_sender -z  zabbix_server   -i  output_file**',send the calculated result to zabbix_server


####如何跑一个测试
1.git clone https://github.com/xluren/Plog

2.cd Plog,exec pwd get the current_path

3.modify the plog.conf,change **source_path** to ${current_path}/demo/output

4.run **nohup sh ./demo/create_log.sh &**

5.run sudo python plog.py -f plog.conf

6.you will see a file,its contents like followings:
```
[xluren@test Plog]$ cat /tmp/zabbix_send_info
test.145 pic_cdn_TCP_HIT 0
test.145 pic_cdn_TCP_MISS 0
test.145 pic_cdn_TCP_ERROR 0
[xluren@test Plog]$



-----

个人的感慨，哎，说多了都是泪
In  China,we name Nov 11  as "Single Day",but in the day of  Nov 11 2014,I fix the bug of plog and also restruct it . So today  I am very happy,event more than that  I have a girlfriend :-)

