import logging
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

from langchain_community.utilities import SQLDatabase

from ..config import DB_PATH

def get_sql_toolkit(llm):
    """Create and return SQLDatabaseToolkit instance."""
    try:
        # Create SQLDatabase instance using the DB_PATH
        db = SQLDatabase.from_uri(
            f"sqlite:///{DB_PATH}",
            sample_rows_in_table_info=3, 
        )
        
  
        logging.info("Successfully connected to the database and verified schema")
        return SQLDatabaseToolkit(db=db, llm=llm)
    except Exception as e:
        logging.error(f"Failed to create SQL toolkit: {str(e)}")
        raise