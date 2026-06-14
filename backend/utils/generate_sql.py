import sys
import os
from sqlalchemy import create_mock_engine

# Ensure models can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Base
import models # Important: import to populate Base.metadata

def dump_sql(sql, *multiparams, **params):
    # Print or write the generated SQL statements
    with open("init_schema.sql", "a") as f:
        # Convert the statement to a string, removing newlines to make it cleaner but maintaining the raw SQL
        statement = str(sql.compile(dialect=engine.dialect)).strip()
        if statement:
            try:
                table_name = sql.element.name
                if table_name:
                    f.write(f"-- Table: {table_name}\n")
            except AttributeError:
                pass
            f.write(statement + ";\n\n")

# Clear the file first
with open("init_schema.sql", "w") as f:
    f.write("-- Database Schema Generated from SQLAlchemy Models\n\n")

# Use a mock engine to generate the SQL statements instead of executing them
engine = create_mock_engine('postgresql://', dump_sql)

# Create all tables (this triggers the mock engine to call dump_sql for each table)
Base.metadata.create_all(engine, checkfirst=False)

print("✅ Successfully generated init_schema.sql")
