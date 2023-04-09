
from logging import Logger, DEBUG, INFO
from unittest import TestCase

from common import script_logger as sl

class TestScriptLogger(TestCase):

    def test_debug_logger_is_created_with_1_debug_handler(self):
        # Act.
        logger = sl.get_console_logger('test-debug-logger')
        # Assert.
        self.assertIsInstance(logger, Logger)
        self.assertEqual(len(logger.handlers), 1)
        self.assertEqual(logger.handlers[0].level, DEBUG)
        self.assertEqual(logger.name, 'test-debug-logger')

    def test_task_logger_is_created_with_3_handlers(self):
        # Act.
        logger = sl.get_task_logger('test-task-logger')
        # Assert.
        self.assertIsInstance(logger, Logger)
        self.assertEqual(len(logger.handlers), 3)
        self.assertEqual(logger.handlers[0].level, DEBUG)
        self.assertEqual(logger.handlers[1].level, INFO)
        self.assertEqual(logger.handlers[2].level, INFO)
