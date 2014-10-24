Plog
====

Plog is short for "Parse Log", it's based on regex and the output is a dict which can be used to by other process or software

====

Plog is designed for handling and analyzing log file generated from Apache, nginx etc. The output can be either in dictionary format or json format and it can be used by other programs to do some statistical staff. With proper regular expression, Plog can analyze any kinds of log file. For more detials, please check log_parse.conf.


The idea is that Apache or nginx provide a hard link of log file to outside. Plog will use this hard link to read, handle the log files. This can be very easy to use: since the link given to us is single, we do not need to change anything as long as the hard link remains unchanged.

How to test:

1. Check the script under folder /test. It simulates some situations that may occur in a production environment.

2. demo.py is to test all the modules.

To do list:

1. Complete the configuration for scripts.

2. Output to remote host through tcp/udp etc. 

3. Default configuration for apache and nginx.

4. Compitablity of third party plugins, let programmers customize their own modules.

about the demo:

demo  simulate a real station that  

1. read log

2. parse log 

3. calculate log  

4. write  to file 

5. zabbix sender from the file i wrote 

you can  use single process or multi process and coroutine ,

with single process  you can run as following 
```
(pythonenv)[xluren@test Plog]$ python demo.py 
calculte iterm.......
1414136460.0 {1414136519.9999979: []}
write result to file......
i got you message ,i know u  have wrote result to  file
i will  send with zabbix_send plugin_module
zabbix send begin .......
zabbix_send end......
^CError in atexit._run_exitfuncs:
Traceback (most recent call last):
```

with multi process ,run as following:
```
(pythonenv)[xluren@test Plog]$ python demo.py multi
calculte iterm.......
1414136460.0 {1414136519.9999979: []}
write result to file......
i got you message ,i know u  have wrote result to  file
i will  send with zabbix_send plugin_module
zabbix send begin .......
zabbix_send end......
^CError in atexit._run_exitfuncs:
```
the demo just to test  my idea,i need to  make it more perfect :-)

