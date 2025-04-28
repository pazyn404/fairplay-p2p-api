from os import environ


SYSTEM_ENDPOINT = f"http://{environ['SYSTEM_DOMAIN']}/{{path}}"
