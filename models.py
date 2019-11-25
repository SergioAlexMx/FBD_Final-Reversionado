from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


#
# Esta clase contiene el modelo de usuarios que podran iniciar sesión en nuestro servidor
#

class User(UserMixin):
    def __init__(self, id, name, lastName, email, password, is_admin=False):
        self.id = id
        self.name = name
        self.lastName = lastName
        self.email = email
        self.password = generate_password_hash(password)
        self.is_admin = is_admin

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_admin(self):
        return self.is_admin

    def __repr__(self):
        return '<User {}>'.format(self.email)
