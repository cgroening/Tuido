import logging
from app import TuidoApp


logging.basicConfig(
    filename='log/info.log',
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
_ = logging.getLogger(__name__)


if __name__ == '__main__':
    app = TuidoApp()
    app.run()
