from plog.sink.base import sink_base
from plog.sink.base import sink_base
import os
import time
import commands

class sink(sink_base):

    def __init__(self,sink_dict):

        self.service            = sink_dict['sink_service']
        self.send_dict          = {}
        
        self.zabbix_send_file   = "_".join((sink_dict['sink_zabbix_send_file'],self.service))
        self.zabbix_sender      = sink_dict['sink_zabbix_sender']
        self.zabbix_conf        = sink_dict['sink_zabbix_conf']

        self.dealed_total       = 0
    
    def calculate_item(self,item):

        response_code   = item['response_code']
        response_time   = int(item['response_time'])
        
        '''
        try:
            request_url=item["request_url"].split()[1].split('/')[1]
        except:
            request_url="others"

        response_code       = response_code[0:1]+"xx"     
        
        total_count         = "count"
        avgrt               = "avgrt"
        total_time          = "total_time"
        

        url_count           = request_url+"_count"
        url_total_time      = request_url+"_total_time"
        url_avgrt           = request_url+"_avgrt"
        url_response_code   = "_".join((url,response_code))
        '''
        sum_key_list=[response_code]

        for key in sum_key_list:
            if key not in self.send_dict:
                self.send_dict[key]=0
            else :
                self.send_dict[key]+=1
                print self.send_dict
    
    def deal_sink(self):
        import platform
        hostname=platform.uname()[1]
        with open(self.zabbix_send_file,"w") as file_handle:
            for key in  self.send_dict:
                info="%s %s_%s %f\n" % (hostname,self.service,str(key),self.send_dict[key])
                print info
                file_handle.write(info)
                self.send_dict[key]=0

        cmd="%s -c %s -i %s" % (self.zabbix_sender,self.zabbix_conf,self.zabbix_send_file)
        status,output=commands.getstatusoutput(cmd)
