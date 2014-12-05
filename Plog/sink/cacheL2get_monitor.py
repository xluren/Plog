import logging
import platform
import commands
def deal_sink(sink_option_dict):

    sink_zabbix_monitor_keys=sink_option_dict['sink_zabbix_monitor_keys']
    service=sink_option_dict['sink_zabbix_monitor_service']
    sum_keys=sink_zabbix_monitor_keys.split(',')
    sink_zabbix_send_file=sink_option_dict['sink_zabbix_send_file']
    sink_zabbix_send_cmd=sink_option_dict['sink_zabbix_send_cmd']

    sum_dict={}
    for key in sum_keys:
        sum_dict[str(key)]=0
    
    total_count=[0]

    def deal_dict_item(dict_item,timeout):

        if timeout ==0:
            total_count[0]+=1
            #your code here to  calculate or do other thing 

        else:
            #your code here 
            logging.info(total_count[0])
            total_count[0]=0
            hostname=platform.uname()[1]

            with open(sink_zabbix_send_file,"w") as file_handle:
                for key in  sum_dict:
                    info="%s %s%s %d\n" % (hostname,service,str(key),sum_dict[key])
                    file_handle.write(info)

            zabbix_send_cmd="%s %s" % (sink_zabbix_send_cmd,sink_zabbix_send_file)
            status,output=commands.getstatusoutput(zabbix_send_cmd)
            logging.info("%d--%s" %(status,output))

    return  deal_dict_item
