from datetime import datetime

from tasks import iss


class Test_fetch_history_page:
    def test_success(self):
        url = iss.url_history.format(engine="futures", market="forts")
        payload = {
            "date": "2018-02-14",
            "numtrades": 1,
            "iss.meta": "off",
            "iss.only": "history",
            "history.columns": "SECID,CLOSE",
        }
        task = iss.fetch_history_page.s(url=url, payload=payload, start=0).apply()
        assert task.state == "SUCCESS"
        assert isinstance(task.result, list)
