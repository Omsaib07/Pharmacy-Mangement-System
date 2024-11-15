import pymysql
from sqlalchemy import create_engine


def test_pymysql():
    try:
        # Test PyMySQL connection
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='Omsai7@sql',
            database='Medical'
        )
        print("PyMySQL connection successful!")
        conn.close()
    except Exception as e:
        print(f"PyMySQL connection failed: {e}")

def test_sqlalchemy():
    try:
        # Test SQLAlchemy connection
        engine = create_engine('mysql+pymysql://root:Omsai7%40sql@localhost/Medical')
        with engine.connect() as connection:
            print("SQLAlchemy connection successful!")
    except Exception as e:
        print(f"SQLAlchemy connection failed: {e}")

if __name__ == "__main__":
    print("Testing database connections...")
    test_pymysql()
    test_sqlalchemy()