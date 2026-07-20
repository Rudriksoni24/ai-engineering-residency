import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

console = logging.StreamHandler()
console.setFormatter(formatter)

log_file_path = Path(__file__).resolve().parents[1] / "app.log"
file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
file_handler.setFormatter(formatter)

logger.addHandler(console)
logger.addHandler(file_handler)

logger.info("Logger initialized successfully.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")

