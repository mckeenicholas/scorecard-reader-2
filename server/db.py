import sqlite3
from enum import Enum


class Event(str, Enum):
    TWO_TWO_TWO = "222"
    THREE_THREE_THREE = "333"
    THREE_THREE_THREE_BF = "333bf"
    THREE_THREE_THREE_FM = "333fm"
    THREE_THREE_THREE_MBF = "333mbf"
    THREE_THREE_THREE_OH = "333oh"
    FOUR_FOUR_FOUR = "444"
    FOUR_FOUR_FOUR_BF = "444bf"
    FIVE_FIVE_FIVE = "555"
    FIVE_FIVE_FIVE_BF = "555bf"
    SIX_SIX_SIX = "666"
    SEVEN_SEVEN_SEVEN = "777"
    CLOCK = "clock"
    MINX = "minx"
    PYRAM = "pyram"
    SKEWB = "skewb"


class Status(str, Enum):
    SCANNED = "scanned"
    SUBMITTED = "submitted"
    DOUBLECHECKED = "doublechecked"


class CompetitionDatabase:
    def __init__(self, db_name="competition.db"):
        self.db_name = db_name
        self.create_database()

    def get_connection(self, dict_factory=False):
        conn = sqlite3.connect(self.db_name)
        if dict_factory:
            conn.row_factory = sqlite3.Row  # Return results as dictionaries
        return conn

    def create_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitorID INTEGER,
                round INTEGER,
                event TEXT CHECK (event IN ('222', '333', '333bf', '333fm', '333mbf', '333oh', '444', '444bf', '555', '555bf', '666', '777', 'clock', 'minx', 'pyram', 'skewb') OR event IS NULL),        
                time1 INTEGER,
                time2 INTEGER,
                time3 INTEGER,
                time4 INTEGER,
                time5 INTEGER,
                time6 INTEGER,
                status TEXT NOT NULL CHECK (status IN ('scanned', 'submitted', 'doublechecked'))
            )
            """
        )
        conn.commit()
        conn.close()

    def clear_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS results")
        conn.commit()
        conn.close()
        print("Database reset.")

    def add_result(self, competitor_id, round_num, event, times, status=Status.SCANNED):
        conn = self.get_connection()
        cursor = conn.cursor()

        times += [0] * (6 - len(times))

        time1, time2, time3, time4, time5, time6 = times
        try:
            cursor.execute(
                """
                INSERT INTO results (competitorID, round, event, time1, time2, time3, time4, time5, time6, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    competitor_id,
                    round_num,
                    event,
                    time1,
                    time2,
                    time3,
                    time4,
                    time5,
                    time6,
                    status,
                ),
            )
            conn.commit()
            result_id = cursor.lastrowid
            return result_id
        except sqlite3.Error as e:
            print(f"Error adding result: {e}")
        finally:
            conn.close()

    def fetch_next_scanned_result(self):
        conn = self.get_connection(dict_factory=True)
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT * FROM results
                WHERE status = 'scanned'
                ORDER BY id ASC
                LIMIT 1
                """
            )
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching result: {e}")
        finally:
            conn.close()

    def update_result_to_submitted(self, pk):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE results
                SET status = 'submitted'
                WHERE id = ?
                """,
                (pk,),
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating result: {e}")
        finally:
            conn.close()

    def get_all(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """SELECT competitorID, round, event FROM results WHERE status = 'scanned' """
            )
            cursor.row_factory = sqlite3.Row
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
            return result

        except sqlite3.Error as e:
            print(f"Error fetching result: {e}")
            return []
        finally:
            conn.close()

    def manual_query(self, query):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            for row in results:
                print(row)
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
        finally:
            conn.close()


if __name__ == "__main__":
    db = CompetitionDatabase()
    while True:
        print("\nOptions:")
        print("1. Reset database")
        print("2. Run SQL query")
        print("3. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            db.clear_database()
        elif choice == "2":
            query = input("Enter SQL query: ")
            db.manual_query(query)
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
