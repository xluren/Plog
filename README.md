Plog
====

Plog is short for "Parse Log ",it's based on regex and  the output  is a  dict which can ed  used to by  other process or software

====
Plog  是一个用于处理日志的脚本，解析Apache，nginx 等日志的格式，最终输出一个dict的字符串或者json的形式，用于其他的进程或者软件进行后期的数据统计。任何日志都可以解析，只要有正确的正则表达式，具体配置见conf文件


代码的思想，Apache，nginx等日志对外提供一个硬链接，然后代码读取此硬链接的信息，进行处理。这样方便简单，对外的接口唯一，只要硬连接的名字不变，后续的处理不会有变化。

代码的使用测试，目前正在进行模块的书写，已经完成了大部门的模块，还有细节的模块没有完成，比如输出到文件，代码的优化，脚本的可用性参数配置说明等 

测试过程：

1.查看test目录下的脚本，他模拟了日志的产生，日志文件的轮转，硬链接的inode改变，用来模拟线上真实日志可能产生的变化

2.demo.py 用来做各个模块的测试

下一个开发的目标：

1.完善脚本的参数配置等

2.执行tcp udp等网络投递

3.默认配置Apache nginx 等常用的配置 统计项等

4.具体的业务统计模块化，可插拔
