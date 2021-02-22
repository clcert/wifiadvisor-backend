from uvicorn.workers import UvicornWorker

class WifiAdvisorUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {"proxy_headers": True, "loop": "uvloop", "http": "httptools"}