import cx_Oracle

connection = cx_Oracle.connect("fbd/fbd@localhost:49161/xe")


def get_db_users():
    cur = connection.cursor()
    cur.execute("SELECT * FROM USUARIOS")
    col = cur.fetchall()
    connection.commit()
    cur.close()
    return col
