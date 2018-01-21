from proxy_coro.driver import Driver
from proxy_coro.connector import Connector
import util.log_util as lu
import util.config_util as cu
import time


def main():
    configs = cu.get_config(__file__)
    cu.set_main_log(__name__)
    logger = lu.get_logger(__file__)
    connector = Connector(configs)
    Driver(connector.forward())
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()