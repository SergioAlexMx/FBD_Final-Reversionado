import base64
import os
from decimal import Decimal

import cx_Oracle
from flask import Flask, redirect, request, render_template, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_uploads import UploadSet, configure_uploads, patch_request_class, IMAGES
from werkzeug.urls import url_parse

import forms
from forms import LoginForm, FormUsuarios
from static.conversorBinario import convertToBinaryData
from static.eliminador_acentos import normalize
from static.users_load import get_user, users
from static.utileria import vaciar_uploads

app = Flask(__name__)
login_manager = LoginManager(app)  # Variable donde se almacenaran los parametros del usuario logueado

app.config['SECRET_KEY'] = "TJcjwUQ5tpCiOMYunv@^9NbWms3#697vdxhUtv^NfvR1ch1TIk"
connection = cx_Oracle.connect("fbd/fbd@localhost:49161/xe")

# IMAGE FOLDER STATEMENT
app.config['UPLOAD_FOLDER'] = './uploads'
login_manager = LoginManager(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'uploads')  # you'll need to create a folder named uploads

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB


@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect("/login")
    else:
        if current_user.is_admin:
            return render_template("admin/index.html")
        else:
            return render_template("index.html")


@app.route('/admin/edit_cancion/<string:id>', methods=["POST", "GET"])
@login_required
def edit_cancion(id):
    if current_user.is_admin:
        form = forms.FormCanciones()
        cur = connection.cursor()
        cur.execute("SELECT * FROM CANCIONES WHERE ID_CANCION=:1", (id,))
        dataC = cur.fetchall()[0]
        cur.close()

        # Consulta 1
        cur = connection.cursor()
        cur.execute("SELECT * FROM GENERO")
        dataG = cur.fetchall()
        cur.close()

        # Consulta 2
        cur = connection.cursor()
        cur.execute("SELECT  id_album, nombre FROM ALBUMS")
        dataA = cur.fetchall()
        cur.close()

        if form.validate_on_submit():
            id_genero = request.form["Genero"]
            id_album = request.form["Album"]
            cur = connection.cursor()
            cur.execute(
                "update CANCIONES set ID_GENERO =:1, ID_ALBUM =:2, NOMBRE =:3, PRECIO =:4 where ID_CANCION=:5",
                (id_genero, id_album, form.nombre.data, form.precio.data, id))
            cur.close()
            flash("Cancion modificada correctamente")
            return redirect("/admin/canciones")
        return render_template("/admin/editar_canciones.html", form=form, gen_data=dataG, can=dataC, alb_dat=dataA)
    else:
        return login_manager.unauthorized()


@app.route('/admin/delete_cancion/<string:id>')
@login_required
def delete_cancion(id):
    if current_user.is_admin:
        try:
            cur = connection.cursor()
            cur.execute("DELETE FROM CANCIONES WHERE ID_CANCION= :1", (id,))
            connection.commit()
            cur.close()
            flash("Cancion eliminada exitosamente")
            return redirect('/admin/canciones')
        except cx_Oracle.IntegrityError:
            return "No se puede eliminar ya que hay un registro que lo esta utilizando"
    else:
        return login_manager.unauthorized()


@app.route('/admin/canciones', methods=["POST", 'GET'])
def add_cancion():
    form = forms.FormCanciones()
    if form.validate_on_submit():
        if request.method == "POST":
            id_album = request.form["Album"]
            id_genero = request.form["Genero"]
            cur = connection.cursor()
            cur.execute("insert into CANCIONES(id_genero, id_album, nombre, precio) values (:1,:2,:3,:4)",
                        (id_genero, id_album, form.nombre.data, form.precio.data))
            connection.commit()
            cur.close()
        flash("Cancion agregada exitosamente")
    # Consulta 1
    cur = connection.cursor()
    cur.execute("SELECT * FROM GENERO")
    dataG = cur.fetchall()
    cur.close()

    # Consulta 2
    cur = connection.cursor()
    cur.execute("SELECT  id_album, nombre FROM ALBUMS")
    dataA = cur.fetchall()
    cur.close()

    # Consulta 3
    cur = connection.cursor()
    cur.execute("SELECT * FROM CANCIONES")
    dataC = cur.fetchall()
    cur.close()

    return render_template("admin/canciones.html", form=form, gen_data=dataG, can=dataC, alb_data=dataA)


@app.route('/admin/edit_album/<string:id>', methods=["GET", "POST"])
def edit_album(id):
    if current_user.is_admin:
        form = forms.FormAlbumE()
        if form.validate_on_submit():
            if form.portada.data is None:
                idA = request.form["artista"]
                cur = connection.cursor()
                cur.execute(
                    "UPDATE ALBUMS SET ALBUMS.ID_ARTISTA =:1, ALBUMS.NOMBRE=:2, ALBUMS.PRECIO=:3  WHERE ID_ALBUM=:4",
                    (idA, form.title.data, form.precio.data, id))
                connection.commit()
                cur.close()
                flash("Album editado exitosamente")
                return redirect("/admin/albums")
            else:
                idA = request.form["artista"]
                filename = forms.photos.save(form.portada.data)  # saves image
                im = convertToBinaryData("uploads/%s" % (filename))
                cur = connection.cursor()
                cur.execute("UPDATE ALBUMS SET ID_ARTISTA=:1, NOMBRE=:2,PORTADA=:3, PRECIO=:4 WHERE ID_ALBUM=:5",
                            (idA, form.title.data, im, form.precio.data, id))
                connection.commit()
                cur.close()
                flash("Album8 editado exitosamente")
                return redirect("/admin/albums")
        cur = connection.cursor()
        cur.execute("SELECT * FROM ALBUMS WHERE ID_ALBUM = :1", (id,))
        data = cur.fetchall()
        connection.commit()
        cur.close()

        cur = connection.cursor()
        cur.execute("SELECT * FROM ARTISTAS")
        art_data = cur.fetchall()
        connection.commit()
        cur.close()
        print(data)
        return render_template("admin/editar_albums.html", data=data, art_data=art_data, base64=base64, form=form)
    else:
        return login_manager.unauthorized()


@app.route('/admin/delete_album/<string:id>', methods=["GET", "POST"])
@login_required
def delete_album(id):
    if current_user.is_admin:
        try:
            cur = connection.cursor()
            cur.execute("DELETE FROM ALBUMS WHERE ID_ALBUM = :1", (id,))
            connection.commit()
            cur.close()
            flash("El album fue eliminado correctamente")
            return redirect('/admin/artistas')
        except cx_Oracle.IntegrityError:
            return "No se puede eliminar ya que hay una cancion que lo esta utilizando"
    else:
        return login_manager.unauthorized()


@app.route('/admin/albums', methods=["GET", "POST"])
@login_required
def albums():
    if current_user.is_admin:
        form = forms.FormAlbum()
        if form.validate_on_submit():
            if request.method == "POST":
                idA = request.form["artista"]
                cur = connection.cursor()
                filename = forms.photos.save(form.portada.data)  # saves image
                im = convertToBinaryData("uploads/%s" % (filename))
                precio = Decimal(form.precio.data)
                p = "%.2f" % (precio)
                cur.execute("Insert into ALBUMS(ID_ARTISTA, NOMBRE, PORTADA, PRECIO) values (:1,:2,:3,:4)",
                            (idA, form.title.data, im, p))
                connection.commit()
                cur.close()
                vaciar_uploads()
                flash("Album creado exitosamente")
                return redirect('/admin/albums')
            return "OK"
        cur = connection.cursor()
        cur.execute("SELECT * FROM ARTISTAS")
        data = cur.fetchall()
        connection.commit()
        cur.close()

        cur = connection.cursor()
        cur.execute("SELECT * FROM ALBUMS")
        dataAlbum = cur.fetchall()
        connection.commit()
        cur.close()

        if len(data) == 0:
            return "No puede añadir albumes si no hay artistas"
        return render_template("admin/albums.html", art_data=data, alb_data=dataAlbum, base64=base64, form=form)
    else:
        return login_manager.unauthorized()


@app.route('/admin/edit_artista/<string:id>', methods=["GET", "POST"])
@login_required
def edit_artists(id):
    if current_user.is_admin:
        form = forms.FormArtistaE()
        if form.validate_on_submit():
            nombre = form.nombre.data
            bio = form.bio.data
            filename = forms.photos.save(form.img.data)
            im = convertToBinaryData("uploads/%s" % filename)
            if form.img.data is None:
                cur = connection.cursor()
                cur.execute("UPDATE ARTISTAS SET NOMBRE=:1, BIOGRAFIA=:2 WHERE ID_ARTISTA=:3", (nombre, bio, id))
                connection.commit()
                cur.close()
                return redirect("/admin/artistas")
            else:
                cur = connection.cursor()
                cur.execute("UPDATE ARTISTAS SET NOMBRE=:1, BIOGRAFIA=:2, IMAGEN=:3 WHERE ID_ARTISTA=:4",
                            (nombre, bio, im, id))
                connection.commit()
                cur.close()
                return redirect("/admin/artistas")
        cur = connection.cursor()
        cur.execute("SELECT * FROM ARTISTAS WHERE ID_ARTISTA = :1", (id,))
        data = cur.fetchall()
        connection.commit()
        cur.close()
        form.bio.data = data[0][2]
        return render_template("/admin/editar_artista.html", data=data, base64=base64, form=form)
    else:
        return login_manager.unauthorized()


@app.route('/admin/delete_artista/<string:id>')
@login_required
def delete_artist(id):
    if current_user.is_admin:
        try:
            cur = connection.cursor()
            cur.execute("DELETE FROM ARTISTAS WHERE ID_ARTISTA = :1", (id,))
            connection.commit()
            cur.close()
            flash("Artista eliminado exitosamente")
            return redirect('/admin/artistas')
        except cx_Oracle.IntegrityError:
            return "No se puede eliminar ya que hay un registro que lo esta utilizando"
    else:
        return login_manager.unauthorized()


@app.route('/admin/artistas', methods=['GET', 'POST'])
@login_required
def artistas():
    if current_user.is_admin:
        form = forms.FormArtista()
        if form.validate_on_submit():
            filename = forms.photos.save(form.img.data)  # saves image

            ib = convertToBinaryData("uploads/%s" % (filename))

            # check class validations

            cur = connection.cursor()
            # empPicture = open("uploads/%s" % (filename), "rb").read()  # Converts the image to binary
            # empPicture = convertToBinaryData(empPicture)
            empPicture = convertToBinaryData("uploads/%s" % filename)
            print(normalize(form.bio.data))
            cur.execute("INSERT INTO ARTISTAS(NOMBRE, BIOGRAFIA, IMAGEN) VALUES (:2, :3, :4)",
                        (form.nombre.data, normalize(form.bio.data), empPicture))
            connection.commit()
            cur.close()
            flash("Artista añadido exitosamente.")

        # Consultar artistas
        cur = connection.cursor()
        cur.execute("SELECT * FROM ARTISTAS")
        data = cur.fetchall()
        cur.close()
        return render_template("admin/artistas.html", form=form, data=data)
    else:
        return login_manager.unauthorized()


@app.route('/admin/delete_genero/<string:id>')
@login_required
def delete_genre(id):
    if current_user.is_admin:
        cur = connection.cursor()
        cur.execute("DELETE FROM GENERO WHERE ID_GENERO = :1", (id,))
        connection.commit()
        cur.close()
        flash("El genero fue eliminado exitosamente")
        return redirect("/genres")
    else:
        return login_manager.unauthorized()


@app.route('/admin/edit_genero/<string:id>', methods=["POST", "GET"])
@login_required
def edit_genre(id):
    if current_user.is_admin:
        form = forms.FormGenres()
        cur = connection.cursor()
        cur.execute("SELECT * FROM GENERO WHERE ID_GENERO=:1", (id,))
        data = cur.fetchall()[0]
        cur.close()
        if form.validate_on_submit():
            cur = connection.cursor()
            cur.execute("update GENERO set GENERO=:1 where ID_GENERO=:2", (form.genre.data, id))
            cur.close()
            flash("Genero modificado correctamente")
            return redirect("/admin/generos")
        return render_template("/admin/editar_genero.html", form=form, gen=data)
    else:
        return login_manager.unauthorized()


@app.route('/admin/generos', methods=["POST", "GET"])
@login_required
def genres():
    if current_user.is_admin:
        form = forms.FormGenres()
        if form.validate_on_submit():
            cur = connection.cursor()
            cur.execute("Insert into GENERO(GENERO) values (:1)", (form.genre.data,))
            connection.commit()
            cur.close
            flash("GENERO CREADO EXISTOSAMENTE")
            return redirect("/admin/generos")
        cur = connection.cursor()
        cur.execute("SELECT * FROM GENERO")
        data = cur.fetchall()
        cur.close()
        return render_template("/admin/generos.html", gen=data, form=form)
    else:
        return login_manager.unauthorized()


@app.route("/create_account", methods=['GET', 'POST'])
def create_account():
    form = FormUsuarios(request.form)
    if not current_user.is_authenticated:
        if request.method == "POST":
            nombre = request.form["nombre"]
            apellidos = request.form["apellidos"]
            email = request.form["email"]
            password = request.form["password"]
            es_admin = False
            print(form.validate())
            try:
                cur = connection.cursor()
                cur.execute(
                    "INSERT INTO usuarios(NOMBRE, APELLIDO, CORREO, PASSWORD, ES_ADMIN) VALUES ('%s','%s','%s','%s','%s')" % (
                        nombre, apellidos, email, password, '0'))
                connection.commit()
                cur.close()
                flash("Usuario creado exitosamente, ahora inicie sesión")
                return redirect("/login")
            except:
                flash("Error - No se pudieron almacenar los datos, comuniquelo con el administrador")
                print("Hubo error")
                return redirect("/create_account")
    return render_template("create_account.html", form=form, flag=True)


@app.route("/admin/create_account", methods=['GET', 'POST'])
def create_account_a():
    form = FormUsuarios(request.form)
    if current_user.is_authenticated:
        if request.method == "POST":
            nombre = request.form["nombre"]
            apellidos = request.form["apellidos"]
            email = request.form["email"]
            password = request.form["password"]
            es_admin = False
            print(form.validate())
            try:
                cur = connection.cursor()
                cur.execute(
                    "INSERT INTO usuarios(NOMBRE, APELLIDO, CORREO, PASSWORD, ES_ADMIN) VALUES ('%s','%s','%s','%s','%s')" % (
                        nombre, apellidos, email, password, '0'))
                connection.commit()
                cur.close()
                flash("Usuario creado exitosamente")
                return redirect("/admin/usuarios")
            except:
                flash("Error - No se pudieron almacenar los datos, comuniquelo con el administrador")
                print("Hubo error")
                return redirect("/create_account")
    return render_template("create_account.html", form=form, flag=False)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm(request.form)
    if request.method == "POST":
        user = get_user(form.email.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = '/'
            return redirect(next_page)
        else:
            flash("Los datos no son validos")
    return render_template('Login.html', form=form)


@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if user.id == int(user_id):
            return user
    return None


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/admin/edit_usuario/<string:id>')
@login_required
def edit_user(id):
    return render_template("create_account.html")


@app.route('/admin/usuarios', methods=['POST', 'GET'])
@login_required
def usuarios():
    if current_user.is_admin:
        from static.get_db_data import get_db_users
        user = get_db_users()
        return render_template("/admin/usuarios.html", data=user)


@app.route('/admin/delete_usuario/<string:id>')
@login_required
def delete_usuario(id):
    if current_user.is_admin:
        cur = connection.cursor()
        cur.execute("DELETE FROM USUARIOS WHERE ID_USUARIO = :1", (id,))
        connection.commit()
        cur.close()
        flash("Artista eliminado exitosamente")
        return redirect('/admin/usuarios')


@app.route('/categoria/albums')
def canciones():
    cur = connection.cursor()
    cur.execute("SELECT * FROM ALBUMS")
    alb = cur.fetchall()
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT * FROM ARTISTAS")
    art = cur.fetchall()
    cur.close()

    return render_template("cat_albums.html", alb=alb, art=art, base64=base64)


@app.route('/album/<string:id>')
def vista_album(id):
    cur = connection.cursor()
    cur.execute("SELECT * FROM ALBUMS WHERE ID_ALBUM=:id", id=id)
    alb = cur.fetchall()[0]
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT NOMBRE FROM ARTISTAS WHERE ID_ARTISTA=:id", id=alb[1])
    art = cur.fetchall()[0]
    cur.close()

    cur = connection.cursor()
    cur.execute("SELECT NOMBRE FROM CANCIONES WHERE ID_ALBUM=:id", id=id)
    can = cur.fetchall()
    cur.close()

    if len(alb) > 0:
        return render_template("vista_album.html", alb=alb, base64=base64, art=art, can=can)
    else:
        render_template("error.html", error_messsage="No se encontró el album")

    return "err"


@app.route('/artistas')
def cat_artistas():
    cur = connection.cursor()
    cur.execute("SELECT * FROM ARTISTAS")
    art = cur.fetchall()
    cur.close()


    return render_template("cat_artista.html", art=art, base64=base64)

@app.route('/view/arista/<string:id>')
def view_artista():
    return "g"


if __name__ == '__main__':
    app.run()
