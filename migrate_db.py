import sqlite3

DB_PATH = "database/data_source.db"

def migrate():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    
    # Check if column exists
    cur.execute("PRAGMA table_info(dm_participants)")
    columns = [row[1] for row in cur.fetchall()]
    
    if 'lastRead' not in columns:
        print("Adding lastRead column to dm_participants...")
        cur.execute("ALTER TABLE dm_participants ADD COLUMN lastRead DATETIME")
        con.commit()
        print("Migration successful!")
    else:
        print("lastRead column already exists. No migration needed.")
    
    con.close()

if __name__ == "__main__":
    migrate()