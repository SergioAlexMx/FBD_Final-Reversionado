from flask_uploads import UploadSet, IMAGES
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField
from wtforms import validators
from wtforms.validators import DataRequired

photos = UploadSet('photos', IMAGES)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Login')


class FormArtista(FlaskForm):
    nombre = StringField("Nombre", [
        validators.required(message="El nombre es requerido"), validators.length(min=1, max=50,
                                                                                 message="Ingrese un nombre valido")])
    bio = TextAreaField("Biografia")
    img = FileField(validators=[FileAllowed(photos, "Solo fotos!"), FileRequired('File was empty!')])
    submit = SubmitField("Agregar artista")


class FormArtistaE(FlaskForm):
    nombre = StringField("Nombre", [
        validators.required(message="El nombre es requerido"), validators.length(min=1, max=50,
                                                                                 message="Ingrese un nombre valido")])
    bio = TextAreaField("Biografia")
    img = FileField(validators=[FileAllowed(photos, "Solo fotos!")])
    submit = SubmitField("Editar artista")


class FormCanciones(FlaskForm):
    nombre = StringField("Nombre", [
        validators.required(message="El nombre es requerido"), validators.length(min=1, max=25,
                                                                                 message="Ingrese un nombre valido")])
    precio = StringField("Precio", [
        validators.required(message="El nombre es requerido"), validators.length(min=1, max=25,
                                                                                 message="Es necesario el precio")])
    submit = SubmitField("Agregar cancion")


class FormGenres(FlaskForm):
    genre = StringField("Genero", [validators.required("El nombre del genero es requerido"),
                                   validators.length(min=2, max=20, message="Longitud de dato erronea")])
    submit = SubmitField("Agregar cancion")


class FormAlbum(FlaskForm):
    title = StringField("Título del album", [validators.required("El nombre del album es requerido"),
                                             validators.length(min=1, max=40, message="Ingrese un titulo valido")])
    portada = FileField(validators=[FileAllowed(photos, "Solo fotos!"), FileRequired('File was empty!')])
    precio = StringField("Precio", [validators.required("El precio es requerido")])
    submit = SubmitField("Agregar album")


class FormAlbumE(FlaskForm):
    title = StringField("Título del album", [validators.required("El nombre del album es requerido"),
                                             validators.length(min=1, max=40, message="Ingrese un titulo valido")])
    portada = FileField(validators=[FileAllowed(photos, "Solo fotos!")])
    precio = StringField("Precio", [validators.required("El precio es requerido")])
    submit = SubmitField("Agregar album")


class FormUsuarios(FlaskForm):
    nombre = StringField("Nombre", [validators.required("El campo nombre es requerido"),
                                    validators.length(min=1, max=400, message="Ingrese un nombre valido")])
    apellidos = StringField("Apellidos", [validators.required("El campo apellido es requerido"),
                                          validators.length(min=1, max=35, message="Ingrese un apellido valido")])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

