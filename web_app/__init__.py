# web_app/__init__.py
import os
from pathlib import Path
import logging

# Configurar logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('web_app.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Garantir que o diretório static existe
static_dir = Path(__file__).parent / 'static'
if not static_dir.exists():
    static_dir.mkdir(parents=True)
    logger.info(f"Static directory created at: {static_dir.resolve()}")
else:
    logger.info(f"Static directory ensured at: {static_dir.resolve()}")