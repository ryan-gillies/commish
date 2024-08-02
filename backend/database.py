from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create an engine
engine = create_engine('postgresql://retool:ZHVhmOA2Tb4i@ep-icy-salad-54868721.us-west-2.retooldb.com/retool?sslmode=require')

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use the SessionLocal class to create a new session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db = get_db()