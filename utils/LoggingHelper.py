import logging


class Whitelist(logging.Filter):
    def __init__(self, *whitelist):
        super().__init__()
        self.whitelist = [logging.Filter(name) for name in whitelist]

    def filter(self, record):
        return any(f.filter(record) for f in self.whitelist)


class Blacklist(Whitelist):
    def filter(self, record):
        return not Whitelist.filter(self, record)