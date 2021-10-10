"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485
import os
import shutil
import tempfile
import uuid
import hashlib
from functools import wraps


def sha256sum(filename):
    """Return sha256 hash of file content, similar to UNIX sha256sum."""
    content = open(filename, 'rb').read()
    sha256_obj = hashlib.sha256(content)
    return sha256_obj.hexdigest()

def generate_password(password):
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    return "$".join([algorithm, salt, password_hash])

def check_password(password,password_db_string):
    [algorithm, salt, password_hash] = password_db_string.split("$")
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    return hash_obj.hexdigest() == password_hash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not flask.session.get('logged_in'):
            return flask.redirect(flask.url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def fetch_file(filename):
    dest = os.path.join(
         os.path.dirname(os.path.dirname(os.path.realpath(__file__)))[:-9],
        'var', 'uploads', filename
    )
    if not os.path.isfile(dest):
        source = os.path.join(
            insta485.app.config["UPLOAD_FOLDER"],
            filename
        )
        shutil.copyfile(source, dest)

@insta485.app.route('/', methods=['GET', 'POST'])
@login_required
def show_index():
    """Display / route."""
    db = insta485.model.get_db()

    if flask.request.method == 'POST':
        if "like" in flask.request.form:
            try:
                db.execute("INSERT INTO likes(owner,postid) VALUES (?,?)",(flask.session["username"],flask.request.form["postid"],))
            except:
                pass
        elif "unlike" in flask.request.form:
            try:
                db.execute("DELETE FROM likes WHERE owner=? AND postid=?",(flask.session["username"],flask.request.form["postid"],))
            except:
                pass
        elif "comment" in flask.request.form:
            try:
                db.execute("INSERT INTO comments(owner,postid,text) VALUES (?,?,?)",\
                    (flask.session["username"],flask.request.form["postid"],flask.request.form["text"],))
            except:
                pass
    
    cur = db.execute("SELECT postid, filename, owner, created FROM posts WHERE owner=? OR " 
        "owner IN (SELECT username2 FROM following WHERE username1=?)",(flask.session["username"],flask.session["username"],))
    posts = list(cur.fetchall())
    # 待会弄懂
    for post in posts:
        fetch_file(post['filename'])
    
    for post in posts:
        cur = db.execute("SELECT filename FROM users WHERE username=?",(post["owner"],))
        post["owner_img_url"] = cur.fetchall()[0]["filename"]
        fetch_file(post["owner_img_url"])
        cur = db.execute("SELECT COUNT(*) AS num FROM likes WHERE postid=?",(post["postid"],))
        post["likes"] = cur.fetchall()[0]["num"]
        cur = db.execute("SELECT owner, text FROM comments WHERE postid=?",(post["postid"],))
        post["comments"] = list(cur.fetchall())
        cur = db.execute("SELECT COUNT(*) AS num FROM likes WHERE postid=? AND owner=?",(post["postid"],flask.session["username"],))
        post["like"] = cur.fetchall()[0]["num"]>0

    context = {"logname":flask.session['username'], "posts":posts}
    return flask.render_template("index.html", **context)


@insta485.app.route('/u/<username>/', methods=['GET', 'POST'])
@login_required
def show_user(username):
    db = insta485.model.get_db()

    if flask.request.method == 'POST':
        if "follow" in flask.request.form:
            try:
                db.execute("INSERT INTO following(username1, username2) VALUES (?,?)",\
                    (flask.session["username"],flask.request.form["target"],))
            except:
                pass
        elif "unfollow" in flask.request.form:
            try:
                db.execute("DELETE FROM following WHERE username1=? AND username2=?",\
                    (flask.session["username"],flask.request.form["target"],))
            except:
                pass
        elif "create_post" in flask.request.form and "file" in flask.request.files:
            # Save POST request's file object to a temp file
            dummy, temp_filename = tempfile.mkstemp()
            file = flask.request.files["file"]
            file.save(temp_filename)

            # Compute filename
            hash_txt = sha256sum(temp_filename)
            dummy, suffix = os.path.splitext(file.filename)
            hash_filename_basename = hash_txt + suffix
            
            try:
                db.execute("INSERT INTO posts(filename, owner) VALUES (?,?)",\
                    (hash_filename_basename,flask.session["username"],))
            except:
                pass

            hash_filename = os.path.join(
                insta485.app.config["UPLOAD_FOLDER"],
                hash_filename_basename
            )

            # Move temp file to permanent location
            shutil.move(temp_filename, hash_filename)



    context = {"logname":flask.session['username'], "username":username}

    cur = db.execute("SELECT COUNT(*) AS num FROM following WHERE username1=? AND username2=?",\
        (flask.session['username'],username,))
    context["logname_follows_username"] = cur.fetchall()[0]["num"]>0

    cur = db.execute("SELECT postid, filename AS img_url FROM posts WHERE owner=?",(username,))
    context["posts"] = list(cur.fetchall())
    for post in context["posts"]:
        fetch_file(post['img_url'])

    context["total_posts"] = len(context["posts"])

    cur = db.execute("SELECT COUNT(*) AS num FROM following WHERE username2=?",(username,))
    context["followers"] = cur.fetchall()[0]["num"]

    cur = db.execute("SELECT COUNT(*) AS num FROM following WHERE username1=?",(username,))
    context["following"] = cur.fetchall()[0]["num"]
    
    cur = db.execute("SELECT fullname, filename FROM users WHERE username=?",(username,))
    extra = cur.fetchall()[0]

    return flask.render_template("user.html", **context, **extra)


@insta485.app.route('/u/<username>/followers/', methods=['GET', 'POST'])
@login_required
def show_followers(username):
    db = insta485.model.get_db()
    context = {"logname":flask.session['username']}

    if flask.request.method == 'POST':
        if "follow" in flask.request.form:
            try:
                db.execute("INSERT INTO following(username1, username2) VALUES (?,?)",\
                    (flask.session["username"],flask.request.form["target"],))
            except:
                pass
        elif "unfollow" in flask.request.form:
            try:
                db.execute("DELETE FROM following WHERE username1=? AND username2=?",\
                    (flask.session["username"],flask.request.form["target"],))
            except:
                pass

    cur = db.execute("SELECT username1 AS username FROM following WHERE username2=?",(username,))
    context["followers"] = list(cur.fetchall())
    for follower in context["followers"]:
        cur = db.execute("SELECT filename AS user_img_url FROM users WHERE username=?",(follower["username"],))
        follower["user_img_url"] = cur.fetchall()[0]["user_img_url"]
        fetch_file(follower["user_img_url"])
        cur = db.execute("SELECT COUNT(*) AS num FROM following WHERE username1=? AND username2=?",\
            (flask.session['username'],follower["username"],))
        follower["logname_follows_username"] = cur.fetchall()[0]["num"]>0

    return flask.render_template("followers.html", **context)


@insta485.app.route('/u/<username>/following/', methods=['GET', 'POST'])
@login_required
def show_following(username):
    db = insta485.model.get_db()
    context = {"logname":flask.session['username']}

    if flask.request.method == 'POST':
        if "follow" in flask.request.form:
            try:
                db.execute("INSERT INTO following(username1, username2) VALUES (?,?)",\
                    (flask.session["username"],flask.request.form["target"],))
            except:
                pass
        elif "unfollow" in flask.request.form:
            try:
                db.execute("DELETE FROM following WHERE username1=? AND username2=?",\
                    (flask.session["username"],flask.request.form["target"],))
            except:
                pass

    cur = db.execute("SELECT username2 AS username FROM following WHERE username1=?",(username,))
    context["following"] = list(cur.fetchall())
    for f in context["following"]:
        cur = db.execute("SELECT filename AS user_img_url FROM users WHERE username=?",(f["username"],))
        f["user_img_url"] = cur.fetchall()[0]["user_img_url"]
        fetch_file(f["user_img_url"])
        cur = db.execute("SELECT COUNT(*) AS num FROM following WHERE username1=? AND username2=?",\
            (flask.session['username'],f["username"],))
        f["logname_follows_username"] = cur.fetchall()[0]["num"]>0

    return flask.render_template("following.html", **context)


@insta485.app.route('/explore/', methods=['GET', 'POST'])
@login_required
def show_explore():
    db = insta485.model.get_db()
    context = {"logname":flask.session['username']}

    if flask.request.method == 'POST':
        if "follow" in flask.request.form:
            try:
                db.execute("INSERT INTO following(username1, username2) VALUES (?,?)",\
                    (flask.session["username"],flask.request.form["target"],))
            except:
                pass

    cur = db.execute("""SELECT username, filename AS user_img_url FROM users WHERE 
    username NOT IN (SELECT username2 FROM following WHERE username1=?) AND username!=?
        """,(flask.session["username"],flask.session["username"],))
    
    context["not_following"] = list(cur.fetchall())

    for user in context["not_following"]:
        fetch_file(user["user_img_url"])
    
    return flask.render_template("explore.html", **context)


@insta485.app.route('/p/<postid>/', methods=['GET', 'POST'])
@login_required
def show_post(postid):
    db = insta485.model.get_db()

    if flask.request.method == 'POST':
        if "delete" in flask.request.form:
            try:
                db.execute("DELETE FROM comments WHERE commentid=? AND owner=?",\
                    (flask.request.form["target"],flask.session["username"],))
            except:
                pass
        elif "like" in flask.request.form:
            try:
                db.execute("INSERT INTO likes(owner,postid) VALUES (?,?)",(flask.session["username"],flask.request.form["postid"],))
            except:
                pass
        elif "unlike" in flask.request.form:
            try:
                db.execute("DELETE FROM likes WHERE owner=? AND postid=?",(flask.session["username"],flask.request.form["postid"],))
            except:
                pass
        elif "comment" in flask.request.form:
            try:
                db.execute("INSERT INTO comments(owner,postid,text) VALUES (?,?,?)",\
                    (flask.session["username"],flask.request.form["postid"],flask.request.form["text"],))
            except:
                pass
        elif "delete_post" in flask.request.form:
            try:
                cur = db.execute("SELECT filename FROM posts WHERE postid=? AND owner=?",(postid,flask.session["username"],))
                filename = cur.fetchall()[0]["filename"]
                path1 = os.path.join(
                    insta485.app.config["UPLOAD_FOLDER"],
                    filename
                )
                path2 = os.path.join(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                    'static', 'uploads', filename
                )
                os.remove(path1)
                os.remove(path2)
                db.execute("DELETE FROM posts WHERE postid=? AND owner=?",\
                    (flask.request.form["postid"],flask.session["username"],))
                return flask.redirect("/u/{}/".format(flask.session["username"]))
            except:
                pass

    context = {"logname":flask.session['username'],"postid":postid}
    cur = db.execute("SELECT filename AS img_url, owner, created AS timestamp FROM posts WHERE postid=?",(postid,))
    extra = cur.fetchall()[0]
    fetch_file(extra["img_url"])
    cur = db.execute("SELECT filename FROM users WHERE username=?",(extra["owner"],))
    extra["owner_img_url"] = cur.fetchall()[0]["filename"]
    fetch_file(extra["owner_img_url"])
    cur = db.execute("SELECT COUNT(*) AS num FROM likes WHERE postid=?",(postid,))
    extra["likes"] = cur.fetchall()[0]["num"]
    cur = db.execute("SELECT COUNT(*) AS num FROM likes WHERE postid=? AND owner=?",(postid,flask.session["username"],))
    extra["like"] = cur.fetchall()[0]["num"]>0
    cur = db.execute("SELECT commentid, owner, text FROM comments WHERE postid=?",(postid,))
    extra["comments"] = list(cur.fetchall())

    return flask.render_template("post.html", **context, **extra)



@insta485.app.route('/accounts/login/', methods=['GET', 'POST'])
def login():
    if flask.session.get('logged_in'):
        return flask.redirect(flask.url_for('show_index'))
    else:
        context = {}
        if flask.request.method == 'GET':
            return flask.render_template("login.html")
        else:
            db = insta485.model.get_db()
            cur = db.execute("SELECT password FROM users WHERE username=?",(flask.request.form["username"],))
            res = list(cur.fetchall())
            if res and check_password(flask.request.form["password"],res[0]['password']):
                flask.session['logged_in'] = True
                flask.session['username'] = flask.request.form["username"]
                return flask.redirect(flask.url_for('show_index'))
            else:
                flask.flash('Fail to login!')
                # return flask.render_template("login.html")
                flask.abort(403)


@insta485.app.route('/accounts/logout/')
def logout():
    if flask.session.get('logged_in'):
        flask.session.clear()
    
    return flask.redirect(flask.url_for('login'))


@insta485.app.route('/accounts/create/', methods=['GET', 'POST'])
def create():
    if flask.session.get('logged_in'):
        return flask.redirect(flask.url_for('index'))
    else:
        context = {}
        if flask.request.method == 'GET':
            return flask.render_template("create.html")
        else:
            db = insta485.model.get_db()
            if not flask.request.form["password"]:
                flask.abort(400)
            
            cur = db.execute("SELECT COUNT(*) AS num FROM users WHERE username=?",(flask.request.form["username"],))
            if cur.fetchall()[0]['num'] != 0:
                flask.abort(409)

            if "file" in flask.request.files:
                # Save POST request's file object to a temp file
                dummy, temp_filename = tempfile.mkstemp()
                file = flask.request.files["file"]
                file.save(temp_filename)

                # Compute filename
                hash_txt = sha256sum(temp_filename)
                dummy, suffix = os.path.splitext(file.filename)
                hash_filename_basename = hash_txt + suffix
            
                try:
                    db.execute("INSERT INTO users(username,fullname,email,filename,password) VALUES (?,?,?,?,?)",\
                        (flask.request.form["username"],flask.request.form["fullname"],flask.request.form["email"],\
                            hash_filename_basename, generate_password(flask.request.form["password"]),))
                except:
                    pass

                hash_filename = os.path.join(
                    insta485.app.config["UPLOAD_FOLDER"],
                    hash_filename_basename
                )

                # Move temp file to permanent location
                shutil.move(temp_filename, hash_filename)
            else:
                flask.abort(400)

            cur = db.execute("SELECT password FROM users WHERE username=?",(flask.request.form["username"],))
            res = list(cur.fetchall())
            if res and check_password(flask.request.form["password"],res[0]['password']):
                flask.session['logged_in'] = True
                flask.session['username'] = flask.request.form["username"]
                return flask.redirect(flask.url_for('show_index'))
            else:
                flask.flash('Fail to login!')
                flask.abort(403)

@insta485.app.route('/accounts/edit/', methods=['GET', 'POST'])
@login_required
def edit():
    db = insta485.model.get_db()

    if flask.request.method == 'POST':
        cur = db.execute("""UPDATE users 
            SET fullname=?, email=?
            WHERE username=?""",(flask.request.form["fullname"],flask.request.form["email"],flask.session["username"],))
        if flask.request.files['file'].filename != '':
            dummy, temp_filename = tempfile.mkstemp()
            file = flask.request.files["file"]
            file.save(temp_filename)

            # Compute filename
            hash_txt = sha256sum(temp_filename)
            dummy, suffix = os.path.splitext(file.filename)
            hash_filename_basename = hash_txt + suffix
            
            cur = db.execute("SELECT filename FROM users WHERE username=?",(flask.session["username"],))
            filename = cur.fetchall()[0]["filename"]
            path1 = os.path.join(
                insta485.app.config["UPLOAD_FOLDER"],
                filename
            )
            path2 = os.path.join(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                'static', 'uploads', filename
            )
            os.remove(path1)
            os.remove(path2)

            db.execute("""UPDATE users 
                SET filename=?
                WHERE username=?""",(hash_filename_basename,flask.session["username"],))

            hash_filename = os.path.join(
                insta485.app.config["UPLOAD_FOLDER"],
                hash_filename_basename
            )

            # Move temp file to permanent location
            shutil.move(temp_filename, hash_filename)
        

    context = {"logname":flask.session["username"]}
    cur = db.execute("SELECT fullname, filename AS user_img_url, email FROM users WHERE username=?",(flask.session["username"],))
    extra = cur.fetchall()[0]
    fetch_file(extra["user_img_url"])
    return flask.render_template("edit.html", **context, **extra)

@insta485.app.route('/accounts/password/', methods=['GET', 'POST'])
@login_required
def change_password():
    context = {"logname":flask.session["username"]}
    if flask.request.method == 'POST':
        db = insta485.model.get_db()
        cur = db.execute("SELECT password FROM users WHERE username=?",(flask.session["username"],))
        if not check_password(flask.request.form["password"],cur.fetchall()[0]["password"]):
            flask.abort(403)

        if flask.request.form["new_password1"] != flask.request.form["new_password2"]:
            flask.abort(401)
        
        db.execute("UPDATE users SET password=?",(generate_password(flask.request.form["new_password1"]),))


    return flask.render_template("password.html", **context)


@insta485.app.route('/accounts/delete/', methods=['GET', 'POST'])
@login_required
def delete_account():
    context = {"logname":flask.session["username"]}
    if flask.request.method == 'POST':
        db = insta485.model.get_db()
        cur = db.execute("SELECT filename FROM users WHERE username=?",(flask.session["username"],))
        filename = cur.fetchall()[0]["filename"]
        path1 = os.path.join(
            insta485.app.config["UPLOAD_FOLDER"],
            filename
        )
        path2 = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
            'static', 'uploads', filename
        )
        os.remove(path1)
        os.remove(path2)

        cur = db.execute("SELECT filename FROM posts WHERE owner=?",(flask.session["username"],))
        for post in cur.fetchall():
            filename = post["filename"]
            path1 = os.path.join(
                insta485.app.config["UPLOAD_FOLDER"],
                filename
            )
            path2 = os.path.join(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                'static', 'uploads', filename
            )
            os.remove(path1)
            os.remove(path2)
        
        db.execute("DELETE FROM users WHERE username=?",(flask.session["username"],))
        flask.session.clear()
        return flask.redirect(flask.url_for('create'))

    return flask.render_template("delete.html", **context)

@insta485.app.route('/uploads/<filename>', methods=['GET'])
def get_static_file(filename):
    return flask.redirect(f'/static/uploads/{filename}')


def login_permission(f): 
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not flask.session.get('logged_in'):
            flask.abort(403)
        return f(*args, **kwargs)
    return decorated_function

insta485.app.view_functions['static'] = login_permission(insta485.app.send_static_file)