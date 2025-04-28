from logging import INFO, getLogger, Formatter, StreamHandler
from logging.handlers import RotatingFileHandler
from os.path import join
from data.config import ENV

class LoggerService:
    """Telegram bot uchun rivojlangan log xizmati."""

    _instance = None  # Singletonni yaratish uchun o'zgaruvchi

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, log_dir="LoggingService", log_file="app.log", log_level=INFO, max_bytes=1000000, backup_count=5, log_format=None):
        """Logger xizmati uchun sozlamalar."""
        if hasattr(self, 'logger'):
            return  # Logni faqat bir marta sozlash uchun
        log_file_path = join(log_dir, log_file)
        self.logger = getLogger("TestLogger")
        self.logger.setLevel(log_level)

        # Log formatini sozlash
        log_format = log_format or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = Formatter(log_format)

        # Fayl rotatsiyasi uchun handler
        handler = RotatingFileHandler(log_file_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        handler.setLevel(log_level)
        handler.setFormatter(formatter)

        # Yangi handlerlar faqat bir marta qo‘shilishi uchun tekshiruv
        if not self.logger.handlers:
            self.logger.addHandler(handler)

        # Konsolga chiqish loglari (faqat ishlab chiqish muhiti uchun)
        if ENV == "development":  # Muhitni o‘zgartirish uchun `ENV` o'zgaruvchisini qo'llash
            console_handler = StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def get_logger(self):
        """Logger ob'ektini qaytaradi."""
        return self.logger

    def set_log_level(self, level):
        """Log darajasini sozlash funksiyasi."""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)

    @staticmethod
    def log_exception(exc: Exception, message: str = "Exception occurred"):
        """Istisno hodisalarini logga yozish uchun yordamchi funksiyasi."""
        logger = LoggerService().get_logger()
        logger.error(f"{message}: {exc}", exc_info=True)
