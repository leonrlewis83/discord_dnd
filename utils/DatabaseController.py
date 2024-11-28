import logging
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor
from psycopg2 import OperationalError, IntegrityError, DatabaseError
from typing import Any, List, Optional, Dict


logger = logging.getLogger("bot.dbcontroller")
class DatabaseController:
    def __init__(self, db_url: str, db_port: int, db_user: str, db_password: str, db_name: str, pool_size: int = 5):
        self.db_url = db_url
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.pool_size = pool_size
        self.connection_pool = None
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize the connection pool."""
        try:
            self.connection_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=self.pool_size,
                user=self.db_user,
                password=self.db_password,
                host=self.db_url,
                port=self.db_port,
                database=self.db_name
            )
            if not self.connection_pool:
                logger.error(f'Failed to initialize the connection pool.')
                raise RuntimeError("Failed to initialize the connection pool.")
            logger.info("Connection pool initialized successfully.")
        except OperationalError as e:
            logger.error(f'Error initializing connection pool. {e}')
            raise ConnectionError(f"Error initializing connection pool: {e}")

    def _get_connection(self):
        """Retrieve a connection from the pool."""
        if not self.connection_pool:
            raise RuntimeError("Connection pool is not initialized.")
        try:
            return self.connection_pool.getconn()
        except OperationalError as e:
            raise ConnectionError(f"Error retrieving connection from the pool: {e}")

    def _release_connection(self, conn):
        """Return a connection to the pool."""
        if self.connection_pool:
            self.connection_pool.putconn(conn)

    def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Fetch all rows from a query."""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                return cur.fetchall()
        except DatabaseError as e:
            logger.error(f'Database Error: {e}')
            raise RuntimeError(f"Error fetching data: {e}")
        finally:
            self._release_connection(conn)

    def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """Fetch a single row from a query."""
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                return cur.fetchone()
        except DatabaseError as e:
            logger.error(f'Database Error: {e}')
            raise RuntimeError(f"Error fetching data: {e}")
        finally:
            self._release_connection(conn)

    def execute(self, query: str, params: Optional[tuple] = None) -> None:
        """Execute a query without returning results."""
        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                conn.commit()
        except IntegrityError as e:
            conn.rollback()
            logger.error(f'Integrity Exception: {e}')
            raise ValueError(f"Data integrity error: {e}")
        except DatabaseError as e:
            conn.rollback()
            logger.error(f'Database Error: {e}')
            raise RuntimeError(f"Error executing query: {e}")
        finally:
            self._release_connection(conn)

    def insert(self, table: str, data: Dict[str, Any]) -> None:
        """Insert data into a table."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        logger.debug(f'INSERT Executing: {query}')
        self.execute(query, tuple(data.values()))

    def update(self, table: str, data: Dict[str, Any], condition: str, condition_params: tuple) -> None:
        """Update data in a table based on a condition."""
        set_clause = ', '.join([f"{col} = %s" for col in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        logger.debug(f'UPDATE Executing: {query}')
        self.execute(query, tuple(data.values()) + condition_params)

    def delete(self, table: str, condition: str, condition_params: tuple) -> None:
        """Delete data from a table based on a condition."""
        query = f"DELETE FROM {table} WHERE {condition}"
        logger.debug(f'DELETE Executing: {query}')
        self.execute(query, condition_params)

    def close_pool(self):
        """Close the connection pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Connection pool closed.")
