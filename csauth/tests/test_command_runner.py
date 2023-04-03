
import os
from unittest import TestCase

from common.command_runner import CommandRunner, NonZeroExitCodeError
import settings

class TestCommandRunner(TestCase):

    def test_command_runner_can_run_command_and_get_output(self):
        # Act
        cmd = CommandRunner("echo 'hello world'", get_output=True)
        # Assert
        self.assertEqual(cmd.read_result(), 'hello world\n')

    def test_command_runner_can_create_and_delete_tmp_files_to_hold_outputs(self):
        # Arrange
        start_file_count = len(os.listdir(settings.TMP_DIR))
        cmd = CommandRunner("echo 'hello world'", get_output=True)
        end_file_count = len(os.listdir(settings.TMP_DIR))
        # 1 file was created
        self.assertEqual(start_file_count + 1, end_file_count)
        # Act
        cmd.delete_results()
        # Assert
        # 1 file was delete
        self.assertEqual(start_file_count, len(os.listdir(settings.TMP_DIR)))

    def test_command_runner_can_raise_errors_from_non_zero_error_codes(self):
        # Arrange
        cmd = CommandRunner(
            "false", # A useless command that results in an exit code of 1.
            get_output=False,
            run_now=False,
            raise_for_non_zero_exit_codes=True,
        )
        # Act, Assert
        self.assertRaises(NonZeroExitCodeError, cmd.run_command)

    def test_command_runner_can_delay_raising_non_zero_exit_code_error(self):
        cmd = CommandRunner(
            "false", # A useless command that results in an exit code of 1.
            get_output=False,
            run_now=False,
            raise_for_non_zero_exit_codes=False,
        )
        # Act
        cmd.run_command()
        # Assert
        self.assertRaises(NonZeroExitCodeError, cmd.raise_for_exit_code)
