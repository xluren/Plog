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