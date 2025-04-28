import logging


logger = logging.getLogger("fairplay-p2p-api-host")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s-%(name)s-%(levelname)s-%(message)s-%(system_payload)s-%(user_payload)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
