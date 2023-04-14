

from logging import Logger
import sys
import traceback

from common import ldap_helpers as ldap


def _test_port_389(logger) -> bool:
    logger.info("testing unencrypted connection...")
    try:
        with ldap.new_connection(use_ssl=False) as conn:
            pass
    except Exception as e:
        logger.error("[TEST PORT 389] failed :(")
        logger.error(f'{e}')
        logger.error(traceback.format_exc())
        return False
    else:
        logger.info("[TEST PORT 389] passed :)")
        return True


def _test_port_tls_port_636(logger) -> bool:
    logger.info("testing encrypted connection...")
    try:
        with ldap.new_connection(use_ssl=True) as conn:
            pass
    except Exception as e:
        logger.error("[TEST PORT 636] failed :(")
        logger.error(f'{e}')
        logger.error(traceback.format_exc())
        return False
    else:
        logger.info("[TEST PORT 636] passed :)")
        return True


def main(logger: Logger):
    logger.info("testing python client connectivity")
    results = [
        _test_port_389(logger),
        _test_port_tls_port_636(logger),
    ]

    if all(results):
        exit_code = 0
        logger.info("all tests pass :)")
    else:
        exit_code = 1
        logger.error("1 or more tests failed :(")

    logger.debug("bye")
    sys.exit(exit_code)
