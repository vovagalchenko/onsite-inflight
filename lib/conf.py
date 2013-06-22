import os
from ConfigParser import RawConfigParser
import re

class CFG(object):
    env_conf = None
    instance = None

    def __init__(self, path_to_env_conf):
        self.env_conf = RawConfigParser()
        self.env_conf.readfp(open(path_to_env_conf))

    @staticmethod
    def get_instance():
        if CFG.instance is None:
            my_dir = os.path.dirname(__file__)
            CFG.instance = CFG(my_dir + '/../../environment.conf')
        return CFG.instance

    def get(self, name_of_section, name_of_conf):
        return self.env_conf.get(name_of_section, name_of_conf)

    def is_live(self):
        return re.match('\/var\/onsite-inflight\/', __file__)
