"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485
import uuid
import hashlib
import arrow
import pathlib
import os


@insta485.app.route('/uploads/<path:filename>')
def download_file(filename):
    """Return picture."""
    if 'user_session' in flask.session:
        return flask.send_from_directory(insta485.app.config['UPLOAD_FOLDER'],
                                         filename, as_attachment=True)
    flask.abort(403)


@insta485.app.route('/explore/', methods=['GET', 'POST'])
def explore():
    """Return picture."""
    connection = insta485.model.get_db()
    if 'user_session' in flask.session:
        if flask.request.method == 'POST':
            username = flask.request.form['username']
            connection.execute(
                "INSERT INTO following(username1,username2) "
                "Values((SELECT users.username "
                "From users WHERE users.username = ?), "
                "(SELECT DISTINCT users.username "
                "From users WHERE users.username = ?)) ",
                (flask.session['user_session'], username),
            )
        curl1 = connection.execute(
            "SELECT DISTINCT users.username, users.filename  "
            "FROM users "
            "WHERE users.username not in  "
            "(SELECT DISTINCT following.username2 "
            "FROM following WHERE following.username1 == ? "
            "UNION SELECT DISTINCT following.username1 "
            "FROM following WHERE following.username1 == ? ) ",
            (flask.session['user_session'], flask.session['user_session']),
        )

        temp1 = curl1.fetchall()

        for x in temp1:
            x["filename"] = flask.url_for("download_file",
                                          filename=x["filename"])
        return flask.render_template("explore.html",
                                     explore_people=temp1,
                                     user=flask.session['user_session'])
    else:
        return flask.redirect(flask.url_for('login'))


@insta485.app.route('/u/<user_url_slug>/following/', methods=['GET', 'POST'])
def following(user_url_slug):
    """Return picture."""
    connection = insta485.model.get_db()
    if 'user_session' in flask.session:
        if flask.request.method == 'POST':
            username = flask.request.form['username']
            if 'follow' in flask.request.form:
                connection.execute(
                    "INSERT INTO following(username1,username2) "
                    "Values((SELECT users.username "
                    "From users WHERE users.username = ?), "
                    "(SELECT DISTINCT users.username "
                    "From users WHERE users.username = ?)) ",
                    (flask.session['user_session'], username),
                )
            if 'unfollow' in flask.request.form:
                connection.execute(
                    "DELETE FROM following "
                    "WHERE username1 = ? AND username2 = ?",
                    (flask.session['user_session'], username),
                )

        curl1 = connection.execute(
            "SELECT DISTINCT following.username2 AS username "
            "FROM following "
            "WHERE following.username1 == ?",
            (user_url_slug,),
        )

        temp1 = curl1.fetchall()

        for x in temp1:
            curl2 = connection.execute(
                "SELECT following.username1 AS us "
                "FROM following "
                "WHERE following.username1 == ? AND following.username2 == ? ",
                (flask.session['user_session'], x["username"]),
            )
            temp2 = curl2.fetchall()

            if len(temp2) == 0:
                x['fol'] = 0
            else:
                x['fol'] = temp2[0].get('us')

            curl3 = connection.execute(
                "SELECT DISTINCT users.filename AS img "
                "FROM users "
                "WHERE users.username == ? ",
                (x["username"],),
            )

            temp3 = curl3.fetchall()
            x["img"] = flask.url_for("download_file",
                                     filename=temp3[0].get('img'))
        return flask.render_template("following.html",
                                     followings=temp1,
                                     user=flask.session['user_session'],
                                     page=user_url_slug)
    else:
        return flask.redirect(flask.url_for('login'))


@insta485.app.route('/u/<user_url_slug>/followers/', methods=['GET', 'POST'])
def follower(user_url_slug):
    """Return picture."""
    connection = insta485.model.get_db()
    if 'user_session' in flask.session:
        if flask.request.method == 'POST':
            username = flask.request.form['username']
            if 'follow' in flask.request.form:
                connection.execute(
                    "INSERT INTO following(username1,username2) "
                    "Values((SELECT users.username "
                    "From users WHERE users.username = ?), "
                    "(SELECT DISTINCT users.username "
                    "From users WHERE users.username = ?)) ",
                    (flask.session['user_session'], username),
                )
            if 'unfollow' in flask.request.form:
                connection.execute(
                    "DELETE FROM following WHERE username1 = ? "
                    "AND username2 = ?",
                    (flask.session['user_session'], username),
                )

        curl1 = connection.execute(
            "SELECT DISTINCT following.username1 AS username "
            "FROM following "
            "WHERE following.username2 == ?",
            (user_url_slug,),
        )

        temp1 = curl1.fetchall()

        for x in temp1:
            curl2 = connection.execute(
                "SELECT following.username1 AS us "
                "FROM following "
                "WHERE following.username1 == ? AND following.username2 == ? ",
                (flask.session['user_session'], x["username"]),
            )
            temp2 = curl2.fetchall()

            if len(temp2) == 0:
                x['fol'] = 0
            else:
                x['fol'] = temp2[0].get('us')

            curl3 = connection.execute(
                "SELECT DISTINCT users.filename AS img "
                "FROM users "
                "WHERE users.username == ? ",
                (x["username"],),
            )

            temp3 = curl3.fetchall()
            x["img"] = flask.url_for("download_file",
                                     filename=temp3[0].get('img'))

        return flask.render_template("follower.html",
                                     followings=temp1,
                                     user=flask.session['user_session'],
                                     page=user_url_slug)
    else:
        return flask.redirect(flask.url_for('login'))


@insta485.app.route('/', methods=['GET', 'POST'])
def show_index():
    """Display / route."""
    if 'user_session' in flask.session:
        connection = insta485.model.get_db()
        if flask.request.method == 'POST':
            if 'like' in flask.request.form:
                postid = flask.request.form["postid"]
                connection.execute(
                    "INSERT INTO likes(owner, postid) "
                    "Values((?), (?)) ",
                    (flask.session['user_session'], postid),
                )
            if 'unlike' in flask.request.form:
                postid = flask.request.form["postid"]
                connection.execute(
                   "DELETE FROM likes WHERE likes.owner = ? "
                   "AND likes.postid = ?",
                   (flask.session['user_session'], postid),
                )
            if 'comment' in flask.request.form:
                text = flask.request.form['text']
                postid = flask.request.form['postid']
                connection.execute(
                    "INSERT INTO comments(owner,postid,text) "
                    "Values((SELECT username FROM users "
                    "WHERE users.username = ?), "
                    "(SELECT postid FROM posts WHERE posts.postid = ?), (?)) ",
                    (flask.session['user_session'], postid, text),
                )
        curl1 = connection.execute(
            "SELECT posts.owner,posts.postid, "
            "posts.created, posts.filename,users.filename AS owner_img "
            "FROM posts "
            "JOIN following ON following.username1 == posts.owner "
            "JOIN users ON users.username == posts.owner "
            "WHERE following.username2= ?  "
            "UNION "
            "SELECT  posts.owner,posts.postid, "
            "posts.created, posts.filename,users.filename AS owner_img "
            "FROM posts "
            "JOIN users ON users.username == posts.owner "
            "WHERE posts.owner= ?  "
            "ORDER BY postid ",
            (flask.session['user_session'], flask.session['user_session']),
        )
        temp = curl1.fetchall()

        # GET likes
        for x in temp:
            a = arrow.get(x["created"], 'YYYY-MM-DD HH:mm:ss')
            x["created"] = a.humanize()

            x["filename"] = flask.url_for("download_file",
                                          filename=x["filename"])
            x["owner_img"] = flask.url_for("download_file",
                                           filename=x["owner_img"])
            curl2 = connection.execute(
                "SELECT COUNT(likes.owner) AS num "
                "FROM likes "
                "WHERE likes.postid == ? ",
                (x.get("postid"),)
            )
            temp2 = curl2.fetchall()
            if len(temp2) == 0:
                x["likes"] = 0
            else:
                x["likes"] = temp2[0].get("num")

        # GET Comments
        for x in temp:
            curl3 = connection.execute(
                "SELECT commentid, owner, text "
                "FROM comments "
                "WHERE comments.postid == ? "
                "ORDER BY commentid ",
                (x.get("postid"),)
            )
            temp3 = curl3.fetchall()
            x["Comments"] = temp3
        # GET unlike or like
        for x in temp:
            curl4 = connection.execute(
                "SELECT owner "
                "FROM likes "
                "WHERE likes.postid == ? AND likes.owner == ? ",
                (x.get("postid"), flask.session['user_session'])
            )
            temp4 = curl4.fetchall()
            if len(temp4) == 0:
                x["unlike"] = 0
            else:
                x["unlike"] = temp4[0].get("owner")
        return flask.render_template("index.html",
                                     posts=temp,
                                     user=flask.session['user_session'])

    return flask.redirect(flask.url_for('login'))

    # context = {"users": users}
    # return flask.render_template("index.html", **context)


@insta485.app.route('/accounts/login/', methods=['GET', 'POST'])
def login():
    """Return picture."""
    if 'user_session' in flask.session:
        return flask.redirect(flask.url_for('show_index'))
    # Connect to database
    connection = insta485.model.get_db()
    # Query database
    cur = connection.execute(
        "SELECT username, password "
        "FROM users"
    )
    users = cur.fetchall()
    if flask.request.method == 'POST':
        flask.session.pop('user_session', None)
        username = flask.request.form['username']
        password = flask.request.form['password']
        for x in users:
            if username == x.get("username") and password == x.get("password"):
                flask.session['user_session'] = username
                return flask.redirect(flask.url_for('show_index'))
        flask.abort(403)
    return flask.render_template('login.html')


@insta485.app.route('/accounts/logout/', methods=['POST'])
def logout():
    """Return picture."""
    flask.session.pop('user_session', None)
    return flask.redirect(flask.url_for('login'))


@insta485.app.route('/accounts/create/', methods=['GET', 'POST'])
def create():
    """Return picture."""
    if 'user_session' in flask.session:
        return flask.redirect(flask.url_for('edit'))
    if flask.request.method == 'POST':
        connection = insta485.model.get_db()
        curl = connection.execute(
            "SELECT username "
            "FROM users"
        )
        # GET DATA FROM POST
        username = flask.request.form['username']
        fullname = flask.request.form['fullname']
        email = flask.request.form['email']
        password = flask.request.form['password']

        # CHECK ERRORS
        user_check = curl.fetchall()
        if (len(user_check) != 0):
            for x in user_check:
                if username == x.get('username'):
                    flask.abort(409)
        if(len(password) == 0):
            flask.abort(400)

        algorithm = 'sha512'
        salt = uuid.uuid4().hex
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])

        # Unpack flask object
        fileobj = flask.request.files["file"]
        filename = fileobj.filename
        uuid_basename = "{stem}{suffix}".format(
            stem=uuid.uuid4().hex,
            suffix=pathlib.Path(filename).suffix
        )

        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
        fileobj.save(path)
        connection.execute(
            "INSERT INTO "
            "users(username, fullname, "
            "email, filename, password) "
            "VALUES (?, ?, ?, ?, ?)",
            (username, fullname, email, uuid_basename, password_db_string)
        )

        flask.session.pop('user_session', None)
        flask.session['user_session'] = username

        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template('create.html')


@insta485.app.route('/accounts/delete/', methods=['GET', 'POST'])
def delete():
    """Return picture."""
    if 'user_session' in flask.session:
        if flask.request.method == 'POST':
            connection = insta485.model.get_db()
            username = flask.session['user_session']
            flask.session.pop('user_session', None)

            curl = connection.execute("SELECT filename "
                                      "FROM users WHERE "
                                      "username = ? ", (username,),)
            temp = curl.fetchall()
            filename = temp[0]["filename"]

            curl3 = connection.execute("SELECT posts.filename "
                                       "FROM posts WHERE "
                                       "posts.owner = ? ", (username,),)
            temp3 = curl3.fetchall()
            for x in temp3:
                pat = path = insta485.app.config["UPLOAD_FOLDER"]/x["filename"]
                os.remove(pat)

            connection.execute("delete from users "
                               "where username=(?)", (username,),)
            path = insta485.app.config["UPLOAD_FOLDER"]/filename
            os.remove(path)
            return flask.redirect(flask.url_for('create'))
        u = flask.session['user_session']
        return flask.render_template('delete.html', user=u)
    return flask.redirect(flask.url_for('login'))


@insta485.app.route('/accounts/edit/', methods=['GET', 'POST'])
def edit():
    """Return picture."""
    if "user_session" in flask.session:
        connection = insta485.model.get_db()
        user = flask.session['user_session']
        if flask.request.method == 'POST':
            fullname = flask.request.form['fullname']
            email1 = flask.request.form['email']
            file1 = flask.request.files["file"]

            if not file1:
                connection.execute("UPDATE users SET fullname =: fullname, "
                                   "email =: email "
                                   "WHERE username == username",
                                   {"fullname": fullname,  "email": email1})
            else:
                # Unpack flask object
                # Unpack flask object
                fileobj = flask.request.files["file"]
                filename = fileobj.filename
                uuid_basename = "{stem}{suffix}".format(
                    stem=uuid.uuid4().hex,
                    suffix=pathlib.Path(filename).suffix
                )

                curl1 = connection.execute(
                    "SELECT fullname,email,filename "
                    "FROM users WHERE username=?", (user,),
                )
                user_data1 = curl1.fetchall()
                filename2 = user_data1[0].get('filename')
                path = insta485.app.config["UPLOAD_FOLDER"]/filename2
                os.remove(path)

                # Save to disk
                path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
                fileobj.save(path)
                connection.execute("UPDATE users SET fullname=:fullname, "
                                   "email=:email, "
                                   " filename=:filename "
                                   "WHERE username == username",
                                   {"fullname": fullname, "email": email1,
                                    "filename": uuid_basename})
        curl = connection.execute(
            "SELECT fullname,email,filename "
            " FROM users WHERE username=?", (user,),
        )
        user_data = curl.fetchall()
        filename1 = user_data[0].get('filename')
        filename = flask.url_for("download_file", filename=filename1)
        email = user_data[0].get('email')
        fullname = user_data[0].get('fullname')
        return flask.render_template('edit.html',
                                     user=flask.session['user_session'],
                                     e=email, name=fullname, file=filename)

    return flask.redirect(flask.url_for('login'))


@insta485.app.route('/accounts/password/', methods=['GET', 'POST'])
def password():
    """Return picture."""
    u = flask.session["user_session"]
    if "user_session" in flask.session:
        if flask.request.method == 'POST':
            connection = insta485.model.get_db()
            cur = connection.execute(
                "SELECT username, password "
                "FROM users "
            )
            users = cur.fetchall()
            password = flask.request.form['password']
            new_password1 = flask.request.form['new_password1']
            new_password2 = flask.request.form['new_password2']

            if new_password1 != new_password2:
                flask.abort(401)

            if len(users) == 0:
                flask.abort(403)

            for x in users:
                if u == x.get("username") and password == x.get("password"):
                    algorithm = 'sha512'
                    salt = uuid.uuid4().hex
                    hash_obj = hashlib.new(algorithm)
                    password_salted = salt + password
                    hash_obj.update(password_salted.encode('utf-8'))
                    password_hash = hash_obj.hexdigest()
                    password_db_string = "$".join([algorithm,
                                                  salt, password_hash])
                    connection.execute("UPDATE users SET password = ?"
                                       "WHERE username == ?",
                                       (password_db_string,
                                        flask.session['user_session']),)
                    return flask.redirect(flask.url_for('edit'))
            flask.abort(403)
        u = flask.session['user_session']
        return flask.render_template('password.html', user=u)
    return flask.redirect(flask.url_for('login'))


@insta485.app.route('/u/<user_url_slug>/', methods=['GET', 'POST'])
def home(user_url_slug):
    """Return picture."""
    a = 0
    connection = insta485.model.get_db()
    if 'user_session' in flask.session:
        if flask.request.method == 'POST':
            if 'follow' in flask.request.form:
                username = flask.request.form['username']
                connection.execute(
                    "INSERT INTO following(username1,username2) "
                    "Values((SELECT users.username "
                    "From users WHERE users.username = ?), "
                    "(SELECT DISTINCT users.username "
                    "From users WHERE users.username = ?)) ",
                    (flask.session['user_session'], username),
                )
            if 'unfollow' in flask.request.form:
                username = flask.request.form['username']
                connection.execute(
                    "DELETE FROM following WHERE username1 = ? "
                    "AND username2 = ? ",
                    (flask.session['user_session'], username),
                )

            if 'logout' in flask.request.form:
                flask.session.pop('user_session', None)
                return flask.redirect(flask.url_for('login'))

            if 'file' in flask.request.files:
                a = 1
                # Unpack flask object
                # Unpack flask object
                fileobj = flask.request.files["file"]
                filename = fileobj.filename
                uuid_basename = "{stem}{suffix}".format(
                    stem=uuid.uuid4().hex,
                    suffix=pathlib.Path(filename).suffix
                )

                # Save to disk
                path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
                fileobj.save(path)
            if 'create_post' in flask.request.form:
                if a == 0:
                    flask.abort(400)
                else:
                    connection.execute(
                        "INSERT INTO posts (filename,owner) "
                        "Values((?), "
                        "(SELECT username FROM users WHERE "
                        "users.username == ? )) ",
                        (uuid_basename, flask.session['user_session']),
                        )
        # CHECK user in db
        curl6 = connection.execute(
            "SELECT username "
            "FROM users "
            "WHERE users.username == ? ",
            (user_url_slug,),
        )
        temp6 = curl6.fetchall()
        if len(temp6) == 0:
            flask.abort(404)

        # GET posts_img and number of posts
        curl1 = connection.execute(
            "SELECT  posts.filename AS img, posts.postid AS id "
            "FROM posts "
            "WHERE posts.owner == ? ",
            (user_url_slug,),
        )
        temp1 = curl1.fetchall()

        # Change img_url
        if len(temp1) != 0:
            temp1[0]['num'] = len(temp1)
            for x in temp1:
                x["img"] = flask.url_for("download_file", filename=x["img"])

        # In case the post_num is 0
        else:
            temp1 = [{}]
            temp1[0]['num'] = 0
        # GET relationship
        curl2 = connection.execute(
            "SELECT following.username1 AS us "
            "FROM following "
            "WHERE following.username1 == ? AND following.username2 == ? ",
            (flask.session['user_session'], user_url_slug),
        )
        temp2 = curl2.fetchall()

        if len(temp2) == 0:
            temp1[0]['fol'] = 0
        if len(temp2) != 0:
            temp1[0]['fol'] = temp2[0].get('us')
        if user_url_slug == flask.session['user_session']:
            temp1[0]['fol'] = -1

        # GET FULLNAME
        curl5 = connection.execute(
            "SELECT users.fullname "
            "FROM users "
            "WHERE users.username == ? ",
            (user_url_slug,),
        )
        temp5 = curl5.fetchall()
        temp1[0]['fullname'] = temp5[0].get('fullname')
        curl3 = connection.execute(
            "SELECT COUNT(following.username2) AS num1 "
            "FROM following "
            "WHERE following.username1 == ? ",
            (user_url_slug,),
        )
        temp3 = curl3.fetchall()
        temp1[0]['num_following'] = temp3[0].get('num1')
        # Get num followers
        curl4 = connection.execute(
            "SELECT COUNT(following.username1) AS num2 "
            "FROM following "
            "WHERE following.username2 == ? ",
            (user_url_slug,),
        )
        temp4 = curl4.fetchall()

        temp1[0]['num_follower'] = temp4[0].get('num2')
        return flask.render_template("home.html",
                                     homepage=temp1, page=user_url_slug,
                                     user=flask.session['user_session'])
    return flask.redirect(flask.url_for('login'))


@insta485.app.route('/p/<postid_url_slug>/', methods=['GET', 'POST'])
def picture(postid_url_slug):
    """Return picture."""
    connection = insta485.model.get_db()
    if 'user_session' in flask.session:
        if flask.request.method == 'POST':
            if 'like' in flask.request.form:
                connection.execute(
                    "INSERT INTO likes(owner,postid) "
                    "Values((?), (?)) ",
                    (flask.session['user_session'], postid_url_slug),
                    )
            if 'unlike' in flask.request.form:
                connection.execute(
                   "DELETE FROM likes WHERE likes.owner = ? "
                   "AND likes.postid = ?",
                   (flask.session['user_session'], postid_url_slug),
                )
            if 'comment' in flask.request.form:
                text = flask.request.form['text']
                connection.execute(
                    "INSERT INTO comments(owner,postid,text) "
                    "Values((SELECT username FROM "
                    "users WHERE users.username = ?), "
                    "(SELECT postid FROM posts WHERE posts.postid = ?), (?)) ",
                    (flask.session['user_session'], postid_url_slug, text),
                )

            if 'uncomment' in flask.request.form:
                commentid = flask.request.form["commentid"]

                connection.execute(
                   "DELETE FROM comments WHERE commentid = ? ",  (commentid,),
                )

            if 'delete' in flask.request.form:
                c = connection.execute(
                    "SELECT posts.filename FROM posts "
                    "WHERE posts.postid = ? ",
                    (postid_url_slug,),
                )
                temp = c.fetchall()
                filename = temp[0]["filename"]
                path = insta485.app.config["UPLOAD_FOLDER"]/filename
                os.remove(path)
                connection.execute(
                   "DELETE FROM posts WHERE postid = ? ",  (postid_url_slug,),
                )
                u = flask.session['user_session']
                return flask.redirect(flask.url_for('home', user_url_slug=u))
        curl1 = connection.execute(
            "SELECT posts.filename AS img, posts.owner AS owner, "
            "posts.created AS time "
            "FROM posts "
            "WHERE posts.postid == ?  ",
            (postid_url_slug,),
        )

        temp1 = curl1.fetchall()

        curl2 = connection.execute(
            "SELECT users.filename AS owner_img "
            "FROM users "
            "WHERE users.username == ?  ",
            (temp1[0]['owner'],),
        )
        temp2 = curl2.fetchall()
        temp1[0]["owner_img"] = temp2[0]["owner_img"]
        # GET LIKES AND CONVERT Img URL
        for x in temp1:
            a = arrow.get(x["time"], 'YYYY-MM-DD HH:mm:ss')
            x["time"] = a.humanize()
            x["img"] = flask.url_for("download_file", filename=x["img"])
            x["owner_img"] = flask.url_for("download_file",
                                           filename=x["owner_img"])
            curl3 = connection.execute(
                "SELECT COUNT(likes.owner) AS num "
                "FROM likes "
                "WHERE likes.postid == ? ",
                (postid_url_slug,),
            )
            temp3 = curl3.fetchall()
            if len(temp3) == 0:
                x["likes"] = 0
            else:
                x["likes"] = temp3[0].get("num")
        curl4 = connection.execute(
            "SELECT commentid, owner, text "
            "FROM comments "
            "WHERE comments.postid == ? "
            "ORDER BY commentid ",
            (postid_url_slug)
            )
        temp4 = curl4.fetchall()
        temp1[0]["comments"] = temp4
        curl5 = connection.execute(
            "SELECT owner "
            "FROM likes "
            "WHERE likes.postid == ? AND likes.owner == ? ",
            (postid_url_slug, flask.session['user_session']),
            )
        temp5 = curl5.fetchall()
        if len(temp5) == 0:
            temp1[0]["unlike"] = 0
        else:
            temp1[0]["unlike"] = temp5[0].get("owner")

        return flask.render_template("picture.html",
                                     posts=temp1,
                                     user=flask.session['user_session'],
                                     postid=postid_url_slug)
    return flask.redirect(flask.url_for('login'))
