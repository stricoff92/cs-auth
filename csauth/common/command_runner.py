
""" CommandRunner is a simple wrapper
    for running system commands.
"""

import os

from common.file_wrapper import TMPFileWrapper


class CommandRunnerError(Exception):
    pass

class NonZeroExitCodeError(CommandRunnerError):
    pass


class CommandRunner:

    def __init__(self,
        command: str,
        run_now=True,
        raise_for_non_zero_exit_codes=True,
        get_output=True,
    ):
        self._command = command
        self._raise_for_non_zero_exit_codes = raise_for_non_zero_exit_codes
        self._get_output = get_output
        self._exit_code = None
        self._out_file_wrapper = None
        self._output_available = False
        self._completed = False

        if run_now:
            self.run_command()

    def run_command(self):
        if self._completed:
            raise CommandRunnerError(
                "Command has already completed."
            )
        if self._get_output:
            self._out_file_wrapper = TMPFileWrapper()
            cmd = (
                self._command
                + ' > '
                + self._out_file_wrapper.full_path
                + ' 2>&1'
            )
            self._output_available = True
        else:
            cmd = self._command
        self._exit_code = os.system(cmd)
        self._completed = True

        if self._raise_for_non_zero_exit_codes:
            self.raise_for_exit_code()


    def raise_for_exit_code(self):
        if not self._completed:
            raise CommandRunnerError(
                "Command did not run yet."
            )
        if self._exit_code != 0:
            raise NonZeroExitCodeError

    def read_result(self) -> str:
        self._validate_can_interact_with_saved_result()
        with open(*self._out_file_wrapper.read_args) as f:
            return f.read()

    def delete_results(self) -> None:
        self._validate_can_interact_with_saved_result()
        self._out_file_wrapper.remove()
        self._output_available = False

    def _validate_can_interact_with_saved_result(self) -> None:
        if not self._completed:
            raise CommandRunnerError(
                "Command did not run yet."
            )
        if not self._get_output:
            raise CommandRunnerError(
                "cannot access command result. Command did not save output."
            )
        if not self._out_file_wrapper:
            raise NotImplementedError
        if not self._output_available:
            raise CommandRunnerError(
                "cannot access command result. File already deleted"
            )
