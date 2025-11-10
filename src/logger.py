import logging

# Setup logging
logging.basicConfig(
    filename='log/info.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
_ = logging.getLogger(__name__)