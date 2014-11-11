import ConfigParser
def get_option_dict(config_file):
    conf=ConfigParser.RawConfigParser()
    conf.read(config_file)
    option_dict={}
    secs=conf.sections()
    for sec in secs:
        option_dict[sec]={}
        for option in  conf.options(sec):
            key=option
            value=conf.get(sec,key)
            option_dict[sec][key]=value
    return option_dict
