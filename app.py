from flask_modus import Modus
from flask import redirect, render_template, request, url_for
from cfg import app, db
from User import User
from Message import Message
import os

modus = Modus(app)
DIR_IMAGES = "static/img/"


@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        if 'image_path' in request.files:
            file = request.files['image_path']
            if file.filename:
                image_name = file.filename
                images_dir = DIR_IMAGES + request.form['first_name']
                os.makedirs(images_dir, exist_ok=True)
                file_path = os.path.join(images_dir, image_name)
                file.save(file_path)
            else:
                file_path = "no_image"
        db.session.add(User(request.form['first_name'],
                            request.form['last_name'], file_path))
        db.session.commit()
        return redirect(url_for('index'))
    return (render_template('index.html', users=User.query.all(),
            messages=[i for i in db.session.execute("""
            SELECT messages.id, content, CONCAT(CONCAT(first_name, ' '),\
            last_name) as user\
            FROM users JOIN messages ON users.id = messages.user_id
            """)]))


@app.route('/user')
def show_all():

    return redirect(url_for('index'))


@app.route('/user/new')
def new():

    return render_template('new_user.html')


@app.route('/user/<int:id_s>', methods=['GET', 'PATCH', 'DELETE'])
def show(id_s):

    if request.method == b'PATCH':

        user_toedit = User.query.get(id_s)
        user_toedit.first_name = request.form['first_name']
        user_toedit.last_name = request.form['last_name']
        if 'image_path' in request.files:
            file = request.files['image_path']
            if file.filename:
                image_name = file.filename
                images_dir = DIR_IMAGES + request.form['first_name']
                os.makedirs(images_dir, exist_ok=True)
                file_path = os.path.join(images_dir, image_name)
                file.save(file_path)
                if user_toedit.image_name != file_path:
                    if user_toedit.image_name != "no_image":
                        os.remove(user_toedit.image_name)
                    user_toedit.image_name = file_path
        db.session.add(user_toedit)
        db.session.commit()
        return redirect(url_for('index'))

    if request.method == b'DELETE':

        Message.query.filter_by(user_id=id_s).delete()
        user_to = User.query.get(id_s)
        if user_to.image_name != "no_image":
            os.remove(user_to.image_name)
            os.rmdir(DIR_IMAGES + user_to.first_name)
        db.session.delete(user_to)
        db.session.commit()
        return redirect(url_for('index'))

    return (render_template('show.html', user=User.query.get(id_s),
            messages=[m for m in Message.query.filter_by(user_id=id_s)]))


@app.route('/user/<int:id_s>/edit')
def edit(id_s):

    return render_template('edit_user.html', user=User.query.get(id_s))


@app.route('/user/<int:id_s>/messages/<int:id_m>/edit')
def edit_message(id_s, id_m):

    return (render_template('edit_message.html',
                            message=Message.query.get(id_m),
                            user=User.query.get(id_s)))


@app.route('/user/<int:id_s>/messages/<int:id_m>', methods=['DELETE', 'PATCH'])
def messages(id_s, id_m):

    if request.method == b'DELETE':

        db.session.delete(Message.query.get(id_m))
        db.session.commit()

    elif request.method == b'PATCH':

        mess_toedit = Message.query.get(id_m)
        mess_toedit.content = request.form['content']
        db.session.add(mess_toedit)
        db.session.commit()

    return redirect(url_for('show', id_s=id_s))


@app.route('/user/<int:id_s>/messages/new',  methods=['POST'])
def new_message(id_s):

    db.session.add(Message(request.form['content'], id_s))
    db.session.commit()
    return redirect(url_for('show', id_s=id_s))


@app.errorhandler(404)
def not_found(e):

    return render_template("404.html")
