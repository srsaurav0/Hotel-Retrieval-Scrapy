from sqlalchemy import inspect
from database import engine

inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Existing tables: {tables}")
