import sqlite3
from typing import List, Tuple

import pandas as pd

csv_file_path = "scripts/2023 – HPN.csv"

df = pd.read_csv(csv_file_path)

# Identify duplicate names and modify them
duplicated_names = df[df["Player"].duplicated(keep=False)]["Player"].unique()
for name in duplicated_names:
    mask = df["Player"] == name
    df.loc[mask, "Player"] = df.loc[mask, "Player"] + " (" + df.loc[mask, "TM"] + ")"

print(df.head(), df.dtypes)


def create_table(conn: sqlite3.Connection) -> None:
    """
    Create a table in the SQLite database to store AFL player ratings.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS PlayerRatings2023 (
        Player TEXT,
        TM TEXT,
        GM INTEGER,
        Off_PAV REAL,
        Def_PAV REAL,
        Mid_PAV REAL,
        Total_PAV REAL,
        Off_mPAV REAL,
        Def_mPAV REAL,
        Mid_mPAV REAL,
        Total_mPAV REAL
    );
    """
    )
    conn.commit()


def insert_data(conn: sqlite3.Connection, data: List[Tuple]) -> None:
    """
    Insert the player ratings data into the SQLite database.
    """
    cursor = conn.cursor()
    cursor.executemany(
        """
    INSERT INTO PlayerRatings2023 (
        Player, TM, GM, Off_PAV, Def_PAV, Mid_PAV, Total_PAV, Off_mPAV, Def_mPAV, Mid_mPAV, Total_mPAV
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """,
        data,
    )
    conn.commit()


# Connect to the SQLite database (it will be created if it doesn't exist)
db_path = "HPN_Data.db"
conn = sqlite3.connect(db_path)

# Create the table
create_table(conn)

# Prepare the data for insertion
data_to_insert = [tuple(row) for row in df.itertuples(index=False)]

# Insert the data into the database
insert_data(conn, data_to_insert)

# Close the database connection
conn.close()
