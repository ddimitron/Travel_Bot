import sqlite3

def prepare_database():
    connection = sqlite3.connect('sqlite3.db')
    cursor = connection.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS database (
                id INTEGER PRIMARY KEY, 
                city TEXT, 
                addition TEXT
            )
        ''')
    connection.close()

def execute_query(sql_query, data=None):

    connection = sqlite3.connect('sqlite3.db')
    cursor = connection.cursor()
    if data:
        cursor.execute(sql_query, data)
    else:
        cursor.execute(sql_query)

    connection.commit()
    connection.close()

def execute_selection_query(sql_query, data=None):

    connection = sqlite3.connect('sqlite3.db')
    cursor = connection.cursor()

    if data:
        cursor.execute(sql_query, data)
    else:
        cursor.execute(sql_query)
    rows = cursor.fetchall()
    connection.close()
    return rows