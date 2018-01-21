from proxy_coro.driver import Driver
from proxy_coro.connector import Connector
import util.log_util as lu
import util.config_util as cu
import time
from selectors2 import DefaultSelector

def loop(selector):
    while True:
        events = selector.select()
        for event_key, event_mask in events:
            callback = event_key.data
            callback()
def main():
    configs = cu.get_config(__file__)
    cu.set_main_log(__file__)
    logger = lu.get_logger(__file__)
    selector = DefaultSelector()
    connector = Connector(configs, selector)
    logger.info('Starting the proxy')
    logger.info('logger name: {}'.format(cu.MAIN_LOG))
    Driver(connector.forward())
    loop(selector)

if __name__ == "__main__":
    main()