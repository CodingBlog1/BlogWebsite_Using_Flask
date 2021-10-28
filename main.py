import json
import os
import math
from flask import Flask, render_template, request, session, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

local_server = True
with open("config.json", 'r') as c:
    parameter = json.load(c)["parameter"]
app = Flask(__name__)
app.config['SECRET_KEY'] = 'H1p2p'
app.config['UPLOAD_FOLDER'] = parameter['UPLOAD_FILE_LOC']
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/codingblog'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
SQLALCHEMY_TRACK_MODIFICATIONS = False
db = SQLAlchemy(app)


class Contact(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)
    message = db.Column(db.Text, nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    subtitle = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    date = db.Column(db.String(12), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    example1 = db.Column(db.String(120), nullable=False)
    content1 = db.Column(db.String(120), nullable=False)
    example2 = db.Column(db.String(120), nullable=False)
    content2 = db.Column(db.String(120), nullable=False)
    img_file = db.Column(db.String(120), nullable=False)


@app.route("/")
def main():
    post = Posts.query.filter_by().all()
    last = math.ceil(len(post) / int(parameter['no_of_post']))

    page = request.args.get('page')
    if not str(page).isnumeric():
        page = 1
    page = int(page)
    post = post[(page - 1) * int(parameter['no_of_post']): (page - 1) * int(parameter['no_of_post']) + int(
        parameter['no_of_post'])]

    if page == 1:
        prev = "#"
        nex = "/?page=" + str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        nex = "#This_is_last_page"
    else:
        prev = "/?page=" + str(page - 1)
        nex = "/?page=" + str(page + 1)

    return render_template('index.html', parameter=parameter, post=post, prev=prev, nex=nex)


@app.route("/index.html")
def home():
    post = Posts.query.filter_by().all()[0:parameter['no_of_post']]
    return render_template('index.html', parameter=parameter, post=post)


@app.route("/about.html")
def about():
    return render_template('about.html', parameter=parameter)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', parameter=parameter, post=post)


# @app.route("/post.html")
# def post():
#     posting = Posts.query.filter_by().all()
#     return render_template('post.html', parameter=parameter, posting=posting)


@app.route("/contact.html")
def contact():
    return render_template('contact.html', parameter=parameter)


@app.route("/sign.html", methods=['GET', 'POST'])
def sign():
    return render_template('sign.html', parameter=parameter)


@app.route("/Edit.html")
def Edit():
    if 'user' in session and session['user'] == parameter['admin']:
        post = Posts.query.filter_by().all()
        return render_template('Edit.html', parameter=parameter, post=post)
    return render_template('sign.html', parameter=parameter)

@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == parameter['admin']:
        if request.method == 'POST':
            title = request.form.get('title')
            subtitle = request.form.get('subtitle')
            slug = request.form.get('slug')
            name = request.form.get('name')
            date = request.form.get('date')
            content = request.form.get('content')
            example1 = request.form.get('example1')
            content1 = request.form.get('content1')
            example2 = request.form.get('example2')
            content2 = request.form.get('content2')
            img_file = request.form.get('img_file')

            if sno == '0':
                post = Posts(title=title,
                             subtitle=subtitle,
                             slug=slug,
                             name=name,
                             date=date,
                             content=content,
                             example1=example1,
                             content1=content1,
                             example2=example2,
                             content2=content2,
                             img_file=img_file
                             )
                db.session.add(post)
                db.session.commit()

            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = title
                post.subtitle = subtitle
                post.slug = slug
                post.name = name
                post.date = date
                post.content = content
                post.example1 = example1
                post.content1 = content1
                post.example2 = example2
                post.content2 = content2
                post.img_file = img_file
                db.session.commit()
                return redirect('/edit/' + sno)
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('editpost.html', parameter=parameter, post=post, sno=sno)


@app.route("/dashboard.html", methods=['GET', 'POST'])
def dashboard():
    if 'user' in session and session['user'] == parameter['admin']:
        post = Posts.query.all()
        return render_template('/dashboard.html', parameter=parameter, post=post)
    if request.method == 'POST':
        name = request.form.get("name")
        password = request.form.get("password")
        if name == parameter['admin'] and password == parameter['password']:
            session['user'] = name
            post = Posts.query.all()
            return render_template('dashboard.html', parameter=parameter, post=post)
    return render_template('sign.html', parameter=parameter)


@app.route("/Contact", methods=['GET', 'POST'])
def con():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        message = request.form.get('message')

        entry = Contact(
            name=name,
            phone=phone,
            email=email,
            message=message
        )
        db.session.add(entry)
        db.session.commit()

        return render_template('contact.html', parameter=parameter)


@app.route("/addpost.html")
def addpost():
    if 'user' in session and session['user'] == parameter['admin']:
        return render_template('/addpost.html')
    return render_template("sign.html",parameter=parameter)

@app.route("/logout")
def Logout():
    session.pop('user')
    return redirect('/sign.html')


@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if "user" in session and session['user'] == parameter['admin']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/editpost.html")


@app.route("/uploader", methods=['GET', 'POST'])
def Upload():
    if request.method == 'POST':
        f = request.files['File1']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        return render_template("addpost.html", parameter=parameter)


@app.route("/Addpost", methods=['GET', 'POST'])
def addp():
    if 'user' in session and session['user'] == parameter['admin']:
        if request.method == 'POST':
            title = request.form.get('title')
            subtitle = request.form.get('subtitle')
            slug = request.form.get('slug')
            name = request.form.get('name')
            date = request.form.get('date')
            content = request.form.get('content')
            example1 = request.form.get('example1')
            content1 = request.form.get('content1')
            example2 = request.form.get('example2')
            content2 = request.form.get('content2')
            img_file = request.form.get('img_file')

            entry = Posts(
                title=title,
                subtitle=subtitle,
                slug=slug,
                name=name,
                date=date,
                content=content,
                example1=example1,
                content1=content1,
                example2=example2,
                content2=content2,
                img_file=img_file

            )
            db.session.add(entry)
            db.session.commit()
            return render_template('addpost.html')
    return render_template('sign.html', parameter=parameter)


if __name__ == "__main__":
    app.run(debug=True)
