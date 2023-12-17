from common import getConfig, getAcl, setLogger
from service.botservice import SmartBot

setLogger()

if __name__ == '__main__':
    cfg = getConfig()
    acl = getAcl()
    sb = SmartBot(cfg, acl)
    sb.run()