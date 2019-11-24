from models import User
import cx_Oracle

#
# Este es un script que se encargará de acceder a la base de datos, leer los datos de la base y
# los datos encontrados seran cargados directamente a una variable llamada users
#


users = []


def load_users():
    connection = cx_Oracle.connect("fbd/fbd@localhost:49161/xe")
    cur = connection.cursor()
    cur.execute("SELECT * FROM USUARIOS")
    col = cur.fetchall()
    for c in col:
        id = c[0]
        name = c[1]
        lastN = c[2]
        email = c[3]
        password = c[4]
        admin = True if c[5] == "1" else False
        users.append(User(id, name, lastN, email, password, is_admin=admin))
    cur.close()
    connection.close()


def get_user(email):
    load_users()
    for user in users:
        print(user)
        if user.email == email:
            return user
    return None
