from common import getConfig, getAcl
from service.botservice import SmartBot

if __name__ == '__main__':
    cfg = getConfig()
    acl = getAcl()
    sb = SmartBot(cfg, acl)
    sb.run()