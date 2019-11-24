class Usuarios:
    def __init__(self, nombre, apellidos, correo, password, es_admin):
        self.__nombre = nombre
        self.__apellido = apellidos
        self.__correo = correo
        self.__password = password
        self.__es_admin = True if es_admin == '1' else False

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, nombre):
        self.__nombre = nombre

    @property
    def apellido(self):
        return self.__apellido

    @apellido.setter
    def apellido(self, apellido):
        self.__apellido = apellido

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, correo):
        self.__correo = correo

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, password):
        self.__password = password

    @property
    def es_admin(self):
        return self.__es_admin

    @es_admin.setter
    def es_admin(self, es_admin):
        self.__es_admin = es_admin
