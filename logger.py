import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FOLDER = f"{os.getcwd()}/log"
FMT = f"[%(levelname)s] %(asctime)s : %(module)s : %(funcName)s : %(lineno)d :: -  %(message)s"
DATE_FMT = '%Y-%m-%d %H:%M:%S'

class LoggerFactory:

    class CustomFormatter(logging.Formatter):
        grey = '\x1b[38;21m'
        blue = '\x1b[38;5;39m'
        yellow = '\x1b[38;5;226m'
        red = '\x1b[38;5;196m'
        bold_red = '\x1b[31;1m'
        reset = '\x1b[0m'
        green = '\x1b[38;5;46m'
        bold_green = '\x1b[32;1m'

        def __init__(self, fmt, datefmt):
            super().__init__()
            self.fmt = fmt
            self.datefmt = datefmt
            self.FORMATS = {
                logging.DEBUG: self.bold_green + self.fmt + self.reset,
                logging.INFO: self.blue + self.fmt + self.reset,
                logging.WARNING: self.yellow + self.fmt + self.reset,
                logging.ERROR: self.red + self.fmt + self.reset,
                logging.CRITICAL: self.bold_red + self.fmt + self.reset
            }

        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt, datefmt=self.datefmt)
            return formatter.format(record)

    LOG_FOLDER = LOG_FOLDER
    LOG_FILE_SIZE = 2097152
    BACKUP_COUNT = 10
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    try:
        if not os.path.exists(LOG_FOLDER):
            os.makedirs(LOG_FOLDER)
    except OSError:
        print(f"Error with Create Folder {LOG_FOLDER}")

    FORMATTER = logging.Formatter(fmt=FMT)

    STREAM_HANDLER = logging.StreamHandler()
    STREAM_HANDLER.setLevel(logging.DEBUG)
    STREAM_HANDLER.setFormatter(CustomFormatter(FMT, DATE_FMT))
    REGISTERED_LOGGER = {}

    @classmethod
    def get_logger(cls, name, log_file=None):
        """
        :param name: 로거 이름
        :param log_file: 로그 파일 이름 (기본값: name.log)
        :return: logging.Logger 객체
        """
        logger = logging.getLogger(name)
        if name in cls.REGISTERED_LOGGER:
            return logger

        if log_file is None:
            log_file = f"{name}.log"
        log_file_path = f"{cls.LOG_FOLDER}/{log_file}.log"

        file_handler = RotatingFileHandler(
            filename=log_file_path,
            maxBytes=cls.LOG_FILE_SIZE,
            backupCount=cls.BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(cls.FORMATTER)

        logger.addHandler(cls.STREAM_HANDLER)
        logger.addHandler(file_handler)
        logger.setLevel(logging.DEBUG)

        cls.REGISTERED_LOGGER[name] = logger
        return logger

    @classmethod
    def set_stream_level(cls, level):
        """스트림 핸들러의 레벨을 설정
        CRITICAL  50
        ERROR     40
        WARNING   30
        INFO      20
        DEBUG     10
        NOTSET    0
        """
        cls.STREAM_HANDLER.setLevel(level)

    @classmethod
    def change_log_file(cls, log_file):
        """모든 로거의 파일 핸들러 로그 파일 변경"""
        new_file_handler = RotatingFileHandler(
            filename=f"{cls.LOG_FOLDER}/{log_file}",
            maxBytes=cls.LOG_FILE_SIZE,
            backupCount=cls.BACKUP_COUNT,
            encoding='utf-8'
        )
        new_file_handler.setLevel(logging.DEBUG)
        new_file_handler.setFormatter(cls.FORMATTER)

        for logger in cls.REGISTERED_LOGGER.values():
            for handler in logger.handlers:
                if isinstance(handler, RotatingFileHandler):
                    logger.removeHandler(handler)
                    break
            logger.addHandler(new_file_handler)

        cls.HANDLER = new_file_handler
