import logging
import re
from datetime import datetime

import celery
import numpy as np
import pandas as pd
import requests
import sqlalchemy as sa

import models
from constants import HISTORY_COLUMNS, OPTION_CODE, CALL_MONTH, PUT_MONTH
from models import History, Securities
from worker import app

from .base import Task

logger = logging.getLogger("my_celery")


def to_date(date):
    return pd.to_datetime(date).to_pydatetime()


# Price date for tradedate

url_history = (
    "https://iss.moex.com/iss/history/engines/{engine}/markets/{market}/securities.json"
)
url_security = "https://iss.moex.com/iss/securities/{security}.json"


@app.task(
    bind=True,
    name="fetch_history_page",
    autoretry_for=(TimeoutError, requests.ConnectionError),
    retry_kwargs={"max_retries": 5, "countdown": 2},
)
def fetch_history_page(self, url: str, payload: dict, start: int):
    payload.update({"start": start, "iss.only": "history"})
    response = requests.get(url, params=payload, timeout=5)
    if not response.ok:
        raise requests.ConnectionError
    return response.json()["history"]["data"]


@app.task(name="transform_history_tradedate")
def transform_history_tradedate(rows, date, group, names):
    if not len(rows):
        return None
    data = np.vstack(rows)
    data = pd.DataFrame(data, columns=names)
    data.astype(HISTORY_COLUMNS)
    f = lambda x: {  # NOQA: E731
        "secid": x["secid"],
        "tradedate": date,
        "group": group,
        "data": x.drop("secid").to_dict(),
    }
    data = data.apply(f, axis=1).to_list()
    return data


@app.task(bind=True, name="insert_to_database", base=Task)
def insert_to_database(self, data, mapper_name: str):
    if data is None:
        return
    elif isinstance(data, pd.DataFrame):
        mappings = data.to_dict("records")
    elif isinstance(data, list) and all({isinstance(d, dict) for d in data}):
        mappings = data
    else:
        raise NotImplementedError
    mapper = getattr(models, mapper_name)
    self.session.bulk_insert_mappings(mapper, mappings)
    self.session.commit()


@app.task(
    bind=True,
    base=Task,
    name="get_history_tradedate",
    autoretry_for=(TimeoutError,),
    retry_kwargs={"max_retries": 5, "countdown": 2},
)
def get_history_tradedate(self, engine: str, market: str, date):
    # Check if date is in store
    date = to_date(date)
    group = f"{engine}_{market}"
    filled = self.session.query(
        sa.sql.exists().where(History.group == group).where(History.tradedate == date)
    ).scalar()
    if filled:
        msg = f"{group}:{date} already exists"
        return msg
    # Local params
    column_names_upper = list(map(lambda x: x.upper(), HISTORY_COLUMNS.keys()))
    column_names_lower = list(map(lambda x: x.lower(), HISTORY_COLUMNS.keys()))
    # Initialize payload with extraction params
    # Send GET request for total rows count to determine pages count
    url = url_history.format(engine=engine, market=market)
    payload = {
        "date": date.strftime("%Y-%m-%d"),
        "numtrades": 1,
        "iss.meta": "off",
        "iss.only": "history.cursor",
        "history.columns": ",".join(column_names_upper),
    }
    response = requests.get(url, params=payload, timeout=5)
    if not response.ok:
        raise requests.ConnectionError
    index, total, step = response.json()["history.cursor"]["data"][0]
    # Generate task for every page
    extract_jobs = celery.group(
        fetch_history_page.s(url, payload, i) for i in range(index, total, step)
    )
    # Now run data ETL pipeline
    pipeline = celery.chain(
        extract_jobs,
        transform_history_tradedate.s(date=date, group=group, names=column_names_lower),
        insert_to_database.s(mapper_name="History"),
    )
    # Run
    pipeline.apply_async()


@app.task(name="get_history_daterange")
def get_history_daterange(engine: str, market: str, fromdate, todate):
    date_range = pd.date_range(fromdate, todate).to_pydatetime()
    jobs = celery.group(
        fetch_history_tradedate.si(engine=engine, market=market, date=date)
        for date in date_range
    )
    # Run
    jobs.apply_async()


@app.task(
    bind=True,
    name="fetch_security",
    autoretry_for=(TimeoutError, requests.ConnectionError),
    retry_kwargs={"max_retries": 5, "countdown": 2},
)
def fetch_security(self, security: str):
    url = url_security.format(security=security)
    payload: dict = {
        "description.columns": "name,value,type",
        "boards.columns": "",
        "iss.meta": "off",
        "iss.only": "description",
    }
    response = requests.get(url, params=payload, timeout=10)
    if not response.ok:
        raise requests.ConnectionError
    data: list = response.json()["description"]["data"]

    sec = {}
    for key, val, tip in data:
        key = key.lower()  # lowercase attr
        if tip == "date":
            sec[key] = datetime.strptime(val, "%Y-%m-%d")
        elif tip == "number":
            sec[key] = int(val)
        elif tip == "string":
            sec[key] = str(val)
        else:
            sec[key] = val
            logger.warning("Unknown type %s for param %s", tip, key)
    # Check required columns
    if "secid" not in sec.keys():
        raise ValueError(f"No SECID for {security}")
    # Extract option specific info from secid
    if sec["group"] == "futures_options":
        match_obj = re.match(OPTION_CODE, sec["secid"], re.X)
        if match_obj:
            match_obj = match_obj.groupdict()
            sec.update(match_obj)
            try:
                sec["settlement_month"] = CALL_MONTH.index(sec["settlement_month"])
                sec["option_type"] = "call"
            except ValueError:
                sec["settlement_month"] = PUT_MONTH.index(sec["settlement_month"])
                sec["option_type"] = "put"
        else:
            logger.error("Unable to parse ticker %s", str(sec))
    return sec


@app.task(bind=True, base=Task, name="get_securities")
def get_securities(self):
    # Get missing securities
    missing = (
        self.session.query(History.secid, Securities.secid)
        .outerjoin(Securities)
        .filter(Securities.secid.is_(None))
    )
    return list(missing)
    fetch_jobs = celery.group(fetch_security.si())
