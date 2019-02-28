import logging


class Logger:
    def __init__(self, level):
        self.logger = logging.getLogger("resources")
        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s:\n%(message)s"
        )
        # Handlers
        fh = logging.FileHandler("resources.log")
        fh.setFormatter(formatter)
        sh = logging.StreamHandler("ext://sys.stdout")  # Default is stderr
        sh.setFormatter(formatter)
        #
        self.logger.addHandler(sh)
        self.logger.addHandler(fh)
        self.logger.setLevel(level)

    def process_resource(self, req, resp, resource, params):
        resource.logger = logging.getLogger("resources")

    def process_response(self, req, resp, resource, req_succeeded):
        pass
