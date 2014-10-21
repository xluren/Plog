import re
class parse_log(object):
    def __init__(self,regex,dict_key,yield_line):
        self.regex=regex
        self.dict_key=dict_key
        self.pattern=""
        self.yield_line=yield_line
    def set_pattern(self):
        self.pattern=re.compile(r'%s' % self.regex)
    def deal_log(self):
        self.set_pattern()
        for line in self.yield_line:
            try:
                match=self.pattern.match(line)
                if match:
                    yield 0,dict(zip(self.dict_key,match.groups()))
                else :
                    yield 1,"empty"
            except:
                    yield 1,"faild"
