import sqlite3

CURRENT_VERSION = 'Membarr V1.2'

table_history = {
    'Invitarr V1.0': [
        (0, 'id', 'INTEGER', 1, None, 1),
        (1, 'discord_username', 'TEXT', 1, None, 0),
        (2, 'email', 'TEXT', 1, None, 0),
    ],
    'Membarr V1.2': [
        (0, 'id', 'INTEGER', 1, None, 1),
        (1, 'discord_username', 'TEXT', 1, None, 0),
        (2, 'plex_email', 'TEXT', 0, None, 0),
        (3, 'jellyfin_username', 'TEXT', 0, None, 0),
        (4, 'emby_username', 'TEXT', 0, None, 0),
        (5, 'created_at', 'TEXT', 0, 'CURRENT_TIMESTAMP', 0),
        (6, 'invited_at', 'TEXT', 0, 'CURRENT_TIMESTAMP', 0),
        (7, 'invited_to', 'TEXT', 0, None, 0),
    ]
    
}

def check_table_version(conn, tablename):
    dbcur = conn.cursor()
    dbcur.execute(f"PRAGMA table_info({tablename})")
    table_format = dbcur.fetchall()
    for app_version in table_history:
        if table_history[app_version] == table_format:
            return app_version
    raise ValueError("Could not identify database table version.")

def update_table(conn, tablename):
    version = check_table_version(conn, tablename)
    print('------')
    print(f'DB table version: {version}')
    if version == CURRENT_VERSION:
        print('DB table up to date!')
        print('------')
        return

    # Table NOT up to date.
    # Update to Membarr V1.2 table
    if version == 'Invitarr V1.0':
        print("Upgrading DB table from Invitarr v1.0 to Membarr V1.2")
        # Create temp table
        conn.execute(
        '''CREATE TABLE "membarr_temp_upgrade_table" (
        "id"	INTEGER NOT NULL UNIQUE,
        "discord_username"	TEXT NOT NULL UNIQUE,
        "email"	TEXT,
        "jellyfin_username" TEXT,
        "emby_username" TEXT,
        "created_at TEXT DEFAULT CURRENT_TIMESTAMP",
        "invited_at TEXT DEFAULT CURRENT_TIMESTAMP",
        "invited_to" TEXT,
        PRIMARY KEY("id" AUTOINCREMENT)
        );''')
        conn.execute(f'''
        INSERT INTO membarr_temp_upgrade_table(id, discord_username, email)
        SELECT id, discord_username, email
        FROM {tablename};
        ''')
        conn.execute(f'''
        DROP TABLE {tablename};
        ''')
        conn.execute(f'''
        ALTER TABLE membarr_temp_upgrade_table RENAME TO {tablename}
        ''')
        conn.commit()
        version = 'Membarr V1.2'

    print('------')
    
