

from logging import Logger
from common import ldap_helpers as ldap


def _test_port_389(logger) -> bool:
    logger.info("testing unencrypted connection...")
    try:
        with ldap.new_connection(use_ssl=False) as conn:
            pass
    except Exception as e:
        logger.error("[TEST PORT 389] failed")
        logger.error(f'{e}')
        return False
    else:
        return True


def _test_port_tls_port_636(logger) -> bool:
    logger.info("testing encrypted connection...")
    try:
        with ldap.new_connection(use_ssl=True) as conn:
            pass
    except Exception as e:
        logger.error("[TEST PORT 389] failed")
        logger.error(f'{e}')
        return False
    else:
        return True


def main(logger: Logger):
    logger.info("testing python client connectivity")
    results = [
        _test_port_389(logger),
        _test_port_tls_port_636(logger),
    ]

    if all(results):
        logger.info("all tests pass :)")
    else:
        logger.error("1 or more tests failed :(")
    logger.debug("bye")
