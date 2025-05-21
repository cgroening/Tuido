import argparse
import logging
from app import TuidoApp


# logging_levels = [logging.WARNING, logging.DEBUG, logging.INFO,
#                   logging.CRITICAL, logging.ERROR]

# for logging_level in logging_levels:
#     logging.basicConfig(filename="info.log", filemode="w", level=logging_level,
#                         format="%(asctime)s [%(levelname)s] %(message)s")
# _ = logging.getLogger(__name__)

logging.basicConfig(filename="data/info.log", filemode="w", level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
_ = logging.getLogger(__name__)


if __name__ == '__main__':
    app = TuidoApp()
    app.run()
