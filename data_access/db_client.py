from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from typing import Dict, List, Tuple
from sqlalchemy.sql import text


class MysqlClient:
    """
    Mysql database client using SQLAlchemy for connection pooling.
    """

    def __init__(self, host: str, username: str, password: str, database: str, pool_size=30):
        self.engine = create_engine(
            f"mysql+pymysql://{username}:{password}@{host}/{database}",
            pool_size=pool_size,
            max_overflow=0,
            echo=True,  # Set to False in production
            future=True  # Enable SQLAlchemy 2.0 future features
        )
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)

    def exec_sql(self, sql_statement, params=None) -> Tuple[List[Dict], int]:
        session = self.Session()
        try:
            if params is not None and not isinstance(params, dict):
                raise ValueError("Parameters must be a dictionary or None")

            result = session.execute(sql_statement, params)
            session.commit()
            if result.returns_rows:
                rows = result.fetchall()
                return rows, result.rowcount
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
