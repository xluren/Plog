import ConfigParser
class read_conf(object):
    def __init__(self,config_file):
        self.config_file=config_file
    def get_option_dict(self):
        conf=ConfigParser.ConfigParser()
        conf.read(self.config_file)
        
        option_dict={}
        secs=conf.sections()
        for sec in secs:
            for option in  conf.options(sec):
                key=option
                value=conf.get(sec,key)
                option_dict[key]=value
        return option_dict
