import logging
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent
LOG_DIR = SCRIPT_DIR / 'log'
LOG_FILE = LOG_DIR / 'info.log'

# Make sure that LOG_DIR exists
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging (the log file is automatically created if it doens't exist)
logging.basicConfig(
    filename=LOG_FILE,
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
_ = logging.getLogger(__name__)