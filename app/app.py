import argparse
import os
import logging
import falcon
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from middleware import SQLAlchemySessionManager, Logger
from resources import TestResource


def create():
    # SQLAlchemy
    engine = sqlalchemy.create_engine(os.environ["DATABASE_URL"], echo=True)
    session_factory = sessionmaker(bind=engine)
    # App
    app = falcon.API(
        middleware=[Logger(logging.DEBUG), SQLAlchemySessionManager(session_factory)]
    )
    # Routes
    app.add_route("/test", TestResource())
    return app


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="Run debug server", action="store_true")
    args = parser.parse_args()
    app = create()
    if args.debug:
        from werkzeug.serving import run_simple

        run_simple("0.0.0.0", 8000, app, use_debugger=True, use_reloader=True)
    else:
        from werkzeug.serving import run_simple

        run_simple("0.0.0.0", 8000, app, use_debugger=False, use_reloader=True)
