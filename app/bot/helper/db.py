import sqlite3

from app.bot.helper.dbupdater import check_table_version, update_table

DB_URL = 'app/config/app.db'
DB_TABLE = 'clients'
DB_WAITING = 'waiting'

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Connected to db")
    except Error as e:
        print("error in connecting to db")
    finally:
        if conn:
            return conn

def checkTableExists(dbcon, tablename):
    dbcur = dbcon.cursor()
    dbcur.execute("""SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{0}';""".format(tablename.replace('\'', '\'\'')))
    if dbcur.fetchone()[0] == 1:
        dbcur.close()
        return True
    dbcur.close()
    return False

conn = create_connection(DB_URL)

# Checking if table exists
if checkTableExists(conn, DB_TABLE):
	print('Table exists.')
else:
    conn.execute(
    '''CREATE TABLE "clients" (
    "id"	INTEGER NOT NULL UNIQUE,
    "discord_username"	TEXT NOT NULL UNIQUE,
    "plex_email"	TEXT,
    "jellyfin_username" TEXT,
    "emby_username" TEXT,
    "created_at TEXT DEFAULT CURRENT_TIMESTAMP",
    "invited_at TEXT DEFAULT CURRENT_TIMESTAMP",
    "invited_to" TEXT,    
    PRIMARY KEY("id" AUTOINCREMENT)
    );''')

update_table(conn, DB_TABLE)

# Checking if the waiting table exists
if checkTableExists(conn, DB_WAITING):
	print('Table exists.')
else:
    conn.execute(
    '''CREATE TABLE "waiting" (
    "id"	INTEGER NOT NULL UNIQUE,
    "discord_username"	TEXT NOT NULL UNIQUE,
    "platform"	TEXT,
    "created_at TEXT DEFAULT CURRENT_TIMESTAMP", 
    PRIMARY KEY("id" AUTOINCREMENT)
    );''')


def save_user(discord_username, platform_username, platform):
    if discord_username and platform_username:
 
        if platform == 'plex':          
            conn.execute(f"""
                INSERT INTO clients (discord_username, plex_email) VALUES ('{discord_username}', '{platform_username}')
                ON CONFLICT(discord_username) DO UPDATE SET plex_email='{platform_username}'
            """)
        elif platform == 'jellyfin':
            conn.execute(f"""
                INSERT INTO clients (discord_username, jellyfin_username) VALUES ('{discord_username}', '{platform_username}')
                ON CONFLICT(discord_username) DO UPDATE SET jellyfin_username='{platform_username}'
            """)
        elif platform == 'emby':
            conn.execute(f"""
                INSERT INTO clients (discord_username, emby_username) VALUES ('{discord_username}', '{platform_username}')
                ON CONFLICT(discord_username) DO UPDATE SET emby_username='{platform_username}'
            """)            
        conn.commit()
        print("User added to db.")
    else:
        return (f"Discord and '{platform}' usernames cannot be empty")
    

def save_user_all(username, email, jellyfin_username, emby_username):
    if username and email and jellyfin_username:
        conn.execute(f"""
            INSERT OR UPDATE INTO clients(discord_username, email, jellyfin_username)
            VALUES('{username}', '{email}', '{jellyfin_username}')
        """)
        conn.commit()
        print("User added to db.")
    elif username and email:
        save_user_email(username, email)
    elif username and jellyfin_username:
        save_user_jellyfin(username, jellyfin_username)
    elif username and emby_username:
        save_user_emby(username, emby_username)        
    elif username:
        save_user(username)
    else:
        return "Discord username must all be provided"


def save_waiting(discord_username, platform):
        #first we delete the record if it exists so we can reset the waiting position
        conn.execute('DELETE from waiting where discord_username="{}";'.format(discord_username))
        conn.commit()

        conn.execute(f"""
            INSERT INTO waiting(discord_username, platform)
            VALUES('{discord_username}', '{platform}')
        """)
        conn.commit()
        print("User added to db.")   

def get_waiting_place(discord_username):
    select = conn.execute('SELECT count(id)+1 FROM waiting WHERE id < (SELECT id FROM waiting WHERE discord_username = "{}") AND platform = (SELECT platform FROM waiting WHERE discord_username = "{}");'.format(discord_username, discord_username))
    
    for row in select:
        for elem in row:
            place = elem
    
    if(place):
        return place
    else:
        return "You're not on the waiting list"    



def get_username(username, platform):
        
    if username and platform:
        try:
            if platform == "plex":
                cursor = conn.execute('SELECT discord_username, plex_username from clients where discord_username="{}";'.format(username))
            elif platform == "jellyfin":
                cursor = conn.execute('SELECT discord_username, jellyfin_username from clients where discord_username="{}";'.format(username))
            elif platform == "emby":
                cursor = conn.execute('SELECT discord_username, emby_username from clients where discord_username="{}";'.format(username))
            for row in cursor:
                pt_username = row[1]
            if pt_username:
                return pt_username
            else:
                return "No users found"
        except:
            return "error in fetching from db"        
    else:
        return "username and platform cannot be empty"        
   
def remove_username(username, platform):
    """
    Sets username of discord user to null in database
    """
    if username:
        if platform == "plex":
            conn.execute(f"UPDATE clients SET plex_email = null WHERE discord_username = '{username}'")
        elif platform == "jellyfin":
            conn.execute(f"UPDATE clients SET jellyfin_username = null WHERE discord_username = '{username}'")
        elif platform == "emby":
            conn.execute(f"UPDATE clients SET emby_username = null WHERE discord_username = '{username}'")
        conn.commit()
        print(f"{platform} username removed from user {username} in database")
        return True
    else:
        print(f"Username cannot be empty.")
        return False

def delete_user(username):
    if username:
        try:
            conn.execute('DELETE from clients where discord_username="{}";'.format(username))
            conn.commit()
            return True
        except:
            return False
    else:
        return "username cannot be empty"
    

def delete_user_waiting(username):
    if username:
        try:
            conn.execute('DELETE from waiting where discord_username="{}";'.format(username))
            conn.commit()
            return True
        except:
            return False
    else:
        return "username cannot be empty"   

def cleanup_users():

    try:
        conn.execute("DELETE from clients where plex_email IS NULL AND jellyfin_username IS NULL AND emby_username IS NULL")
        conn.commit()
        print(f"Cleanup done.")
        return True
    except:
        return False

def read_all():
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients")
    rows = cur.fetchall()
    all = []
    for row in rows:
        #print(row[1]+' '+row[2])
        all.append(row)
    return all
