import psycopg2
import time
import os
from dotenv import load_dotenv

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
        print("Insert ok:", id_counter)
    except:
        print("Insert error:", id_counter)
def select_records(cur):
    try:
        """Select the latest 10 records from the tmp table."""
        cur.execute("SELECT * FROM tmp ORDER BY id DESC LIMIT 10")
        rows = cur.fetchall()
        return rows
    except:
        print("Select error")

id_counter = 1
timer = 0
interval = 0.5
select_interval = 5

# create_table(cur)
# delete_rows(cur)
try:
    while True:
        try:
            # Increment id counter
            id_counter += 1
            print('start')
            
            # Database connection settings
            conn = psycopg2.connect(
                host=os.getenv('DATABASE_HOST'),
                port=os.getenv('DATABASE_PORT'),
                database=os.getenv('DATABASE_NAME'),
                user=os.getenv('DATABASE_USER'),
                password=os.getenv('DATABASE_PASSWORD'),
            )
            cur = conn.cursor()

            print('end')
            # Insert a new record
            insert_record(cur, conn, id_counter)
            

            if timer % select_interval == 0:
                # Select and print the latest records
                rows = select_records(cur)
                # print("Latest records:")
                # for row in rows:
                #     print(row)
                # print("====================")
                
            

            time.sleep(interval)
            timer += interval
        except: 
            print("Connection error")
except KeyboardInterrupt:
    print("Process interrupted by user.")
finally:
    # Close the cursor and connection
    cur.close()
    conn.close()