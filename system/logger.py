import logging


logger = logging.getLogger("fairplay-p2p-api-system")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s-%(name)s-%(levelname)s-%(message)s-%(player_payload)s-%(host_payload)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
