import sqlalchemy
from sqlalchemy import create_engine, inspect, text
from ..core.config import DBSettings
from ..core.logger import log

class DBManager:
    def __init__(self, db_config: DBSettings):
        try:
            db_uri = self._get_db_uri(db_config)
            self.engine = create_engine(db_uri)
            self.schema_info = self._get_schema_info()
            log.info(f"DBManager connected to {db_config.db_type} and loaded schema.")
        except Exception as e:
            log.error(f"Failed to initialize DBManager: {e}")
            raise

    def _get_db_uri(self, config: DBSettings) -> str:
        if config.db_type == 'sqlite':
            return f"sqlite:///{config.dbname}"
        elif config.db_type == 'postgresql':
            driver = "psycopg2"
            return f"{config.db_type}+{driver}://{config.user}:{config.password}@{config.host}:{config.port}/{config.dbname}"
        elif config.db_type == 'mysql':
            driver = "mysqlclient"
            return f"{config.db_type}+{driver}://{config.user}:{config.password}@{config.host}:{config.port}/{config.dbname}"
        else:
            raise ValueError(f"Unsupported database type: {config.db_type}")

    def _get_schema_info(self) -> str:
        try:
            inspector = inspect(self.engine)
            schema_parts = []
            for table_name in inspector.get_table_names():
                columns = [f"{col['name']} ({str(col['type'])})" for col in inspector.get_columns(table_name)]
                schema_parts.append(f"Table '{table_name}' has columns: {', '.join(columns)}.")
            return "\n".join(schema_parts)
        except Exception as e:
            log.error(f"Failed to retrieve database schema: {e}")
            return "Error: Could not retrieve schema."

    def execute_query(self, sql_query: str):
        log.info(f"Executing SQL query: {sql_query}")
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(sql_query))
                if result.returns_rows:
                    rows = [dict(row._mapping) for row in result]
                    return {"status": "success", "data": rows}
                else:
                    return {"status": "success", "message": f"Operation successful. {result.rowcount} rows affected."}
        except sqlalchemy.exc.SQLAlchemyError as e:
            log.error(f"SQL execution error: {e}")
            return {"status": "error", "message": str(e)}
