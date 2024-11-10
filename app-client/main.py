import psycopg2
import time
import os
from dotenv import load_dotenv
from datetime import datetime


# Load environment variables from .env file
load_dotenv()


def create_table(cur):
    try:
        """Create table if not exist."""
        cur.execute("CREATE TABLE tmp (id int primary key)")
        conn.commit()
    except:
        print("Table is exist")

def delete_rows(cur):
    try:
        """Delete all rows."""
        cur.execute("DELETE FROM tmp")
        conn.commit()
    except:
        print("Delete error")

def insert_record(cur, conn, id_counter):
    try:
        """Insert a new record into the tmp table."""
        cur.execute("INSERT INTO tmp (id) VALUES (%s)", (id_counter,))
        conn.commit()
        current_time = datetime.now().strftime("%H:%M:%S")
        print("Insert ok:", id_counter, '(' + current_time + ')')
    except:
        print("Insert error:", id_counter)
def select_records(cur):
    try:
        """Select the latest 10 records from the tmp table."""
        cur.execute("SELECT COUNT(*) FROM tmp")
        rows = cur.fetchall()
        current_time = datetime.now().strftime("%H:%M:%S")
        print(rows, current_time)
    except Exception as e:
        print(e)
        print("Select error")

id_counter = 1
timer = 0
interval = 0.25
select_interval = 5
created = True
db_conn = None
deleted = True


try:
    while True:
        try:
            
            # Database connection settings
            start_time = time.time()
            
            conn = psycopg2.connect(
                host=os.getenv('DATABASE_HOST'),
                port=os.getenv('DATABASE_PORT'),
                database=os.getenv('DATABASE_NAME'),
                user=os.getenv('DATABASE_USER'),
                password=os.getenv('DATABASE_PASSWORD'),
            )
            cur = conn.cursor()

            if not created:
                create_table(cur)
                created = True
            elif not deleted: 
                delete_rows(cur)
                deleted = True
            # Insert a new record
            # insert_record(cur, conn, id_counter)
            select_records(cur)
            timer += interval

            # Increment id counter
            id_counter += 1
            
        except: 
            print("Connection error")
        finally:
            time.sleep(interval)
except KeyboardInterrupt:
    print("Process interrupted by user.")
finally:
    # Close the cursor and connection
    cur.close()
    conn.close()