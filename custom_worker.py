from uvicorn.workers import UviconWorker

class WifiAdvisorUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {"proxy_headers": True}