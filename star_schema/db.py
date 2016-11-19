"""This module contains the code that touches the database directly

All of the code in other modules interfaces with the database through the
classes and functions in this module."""
from typing import (
    Dict,
    List,
    Union
)

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists
from sqlalchemy.sql import (
    Delete,
    Insert,
    Select,
    Update
)

from star_schema.config import cfg
from logger import rotating_log
from star_schema.utilities import pprint_sql

logger = rotating_log('db')


def get_engine():
    engine = create_engine(cfg.app.db_path, echo=False)
    if not database_exists(engine.url):
        if 'sqlite' in cfg.app.db_path:
            from star_schema import md
            md.create_all(engine)
        else:
            logger.error(
                'get_engine: The database at path {} could not be found.'
                .format(cfg.app.db_path)
            )
    return engine


class Transaction:
    def __init__(self) -> None:
        self.logger = rotating_log('db.Transaction')

        self.connection = get_engine().connect() #eng.connect()
        self.transaction = self.connection.begin()
        self.rows_added = 0
        self.rows_deleted = 0
        self.rows_updated = 0

    def execute(self, cmd: Union[Delete, Insert, Update]):
        self.logger.debug('execute:\n{}'.format(pprint_sql(cmd)))
        try:
            result = self.connection.execute(cmd)
            if type(cmd) == Delete:
                self.rows_deleted += 1
                return 0
            elif type(cmd) == Insert:
                self.rows_added += 1
                return result.inserted_primary_key[0]
            elif type(cmd) == Update:
                self.rows_updated += 1
                return 0
            return 0
        except:
            self.transaction.rollback()
            self.connection.close()
            raise

    def commit(self) -> Dict[str, int]:
        self.transaction.commit()
        self.connection.close()
        return {
            'rows_added':   self.rows_added,
            'rows_deleted': self.rows_deleted,
            'rows_updated': self.rows_updated
        }


def fetch(qry: Select) -> List[str]:
    con = get_engine().connect()
    try:
        logger.debug('fetch:\n{}'.format(pprint_sql(qry)))
        return con.execute(qry).fetchall()
    except:
        raise
    finally:
        con.close()

