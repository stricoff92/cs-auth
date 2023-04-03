
import os
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory for temporary files.
TMP_DIR = os.path.join(BASE_DIR, 'tmp')

# Directory for log files.
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Directory for generated reports.
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')

# Flag to indicate if the environment is unit testing.
IS_TEST = 'ISTEST' in os.environ
