import falcon
import json
import time

from tasks import iss


class TestResource:
    def on_post(self, req: falcon.Request, resp: falcon.Response):
        """Run custom task"""
        if "method" in req.params:
            self.logger.info("Start task by params:\n%s" % ", ".join(req.params))
            method = getattr(iss, req.params.pop("method"))
            kwargs = req.params
            result = method.apply_async(kwargs=kwargs)
            #
            while not result.ready():
                time.sleep(1)
            resp.status = falcon.HTTP_201
            resp.body = json.dumps(
                {
                    "id": f"{result}",
                    "result": f"{result.result}",
                    "state": f"{result.state}",
                    "kwargs": kwargs,
                }
            )

