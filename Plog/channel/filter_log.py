import re
import logging
def parse_str(source_iter,channel_option_dict,dict_queue):
    channel_regex=channel_option_dict["channel_filter_regex"]
    channel_dict_key=channel_option_dict["channel_dict_key"].split(",")
    pattern=re.compile(channel_regex)
    for line  in source_iter:
        try:
            match=pattern.match(line)
            if match:
                dict_queue.put(dict(zip(channel_dict_key,match.groups())))
            else :
                logging.warning( line + "not match pattern")
        except:
            logging.error("source iter error")   
