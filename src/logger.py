import logging
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent

# Setup logging
logging.basicConfig(
    filename=f'{SCRIPT_DIR}/log/info.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
_ = logging.getLogger(__name__)