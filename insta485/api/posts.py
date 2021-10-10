"""REST API for posts."""
import flask
from flask import sessions
import insta485
from functools import wraps


def postid_range_required(f):
    @wraps(f)
    def decorated_function(postid):
        db = insta485.model.get_db()
        cur = db.execute("SELECT postid FROM posts WHERE postid=?",(postid,))
        if not list(cur.fetchall()):
          flask.abort(404)
        return f(postid)
    return decorated_function

def login_required(f):
  @wraps(f)
  def decorated_function(*args,**kwargs):
    if not flask.session.get('logged_in'):
      flask.abort(403)
    return f(*args,**kwargs)
  return decorated_function

@insta485.app.route('/api/v1/', methods = ["GET"])
def api():
  context = {
    "comments": "/api/v1/comments/",
    "likes": "/api/v1/likes/",
    "posts": "/api/v1/posts/",
    "url": "/api/v1/"
  }
  return flask.jsonify(**context);

@insta485.app.route('/api/v1/posts/', methods =["GET"])
def posts():
  db = insta485.model.get_db()
  size = flask.request.args.get("size",default=10,type=int)
  page = flask.request.args.get("page",default=0,type=int)
  
  url = "/api/v1/posts/"
  context = {
      "url": url
  }


  cur = db.execute(
                   "SELECT p.created AS created, ('/uploads/' || p.filename) AS imgUrl, p.owner AS owner, "
                   "('/uploads/' || u.filename) AS ownerImgUrl, ('/users/' || u.username) AS ownerShowUrl, ('/posts/' || p.postid) AS postShowUrl, "
                   "p.postid AS postid, ('/api/v1/p/' || p.postid || '/') AS url " 
                   "FROM posts AS p JOIN users AS u ON p.owner=u.username "
                   "WHERE p.owner=? OR p.owner IN (SELECT username2 FROM following WHERE username1=?) ORDER BY created DESC, postid DESC LIMIT ? OFFSET ? * ?",\
                   (flask.session["username"],flask.session["username"],size,size,page,))
  
  context['results'] = list(cur.fetchall())
  cur = db.execute( "SELECT * FROM (SELECT CASE likes.owner WHEN ? THEN true ELSE false END lognameLikesThis, "
                     "COUNT (*) AS numLikes FROM likes JOIN posts AS p ON likes.postid = p.postid "
                     "WHERE p.owner=? OR p.owner IN (SELECT username2 FROM following WHERE username1=?) ORDER BY p.created DESC, p.postid DESC LIMIT ? OFFSET ? * ?)"
                     "JOIN "
                     "(SELECT ('/api/v1/likes/' || likes.likeid || '/') AS url "
                     "FROM likes JOIN posts AS p ON likes.owner = ? AND likes.postid = p.postid "
                     "WHERE p.owner=? OR p.owner IN (SELECT username2 FROM following WHERE username1=?) ORDER BY p.created DESC, p.postid DESC LIMIT ? OFFSET ? * ?)",\
                     (flask.session["username"], flask.session["username"],flask.session["username"], size, size, page, flask.session["username"], flask.session["username"],flask.session["username"], size, size, page, ))
  context['likes'] = list(cur.fetchall())
  cur = db.execute("SELECT COUNT(*) AS num FROM posts WHERE owner=? OR "
                   "owner IN (SELECT username2 FROM following WHERE username1=?)", \
                     (flask.session["username"],flask.session["username"],))
  if size*(page+1) >= cur.fetchall()[0]["num"]:
    context['next'] = ''
  else:
    context['next'] = f"/api/v1/p/?size={size}&page={page+1}"
  return flask.jsonify(**context);

@insta485.app.route('/api/v1/posts/<int:postid>/', methods=["GET"])
@login_required
@postid_range_required
def get_post(postid):
    db = insta485.model.get_db()
    cur = db.execute("""SELECT p.created AS created, ('/uploads/' || p.filename) AS imgUrl, p.owner AS owner, 
        ('/uploads/' || u.filename) AS ownerImgUrl, ('/users/' || p.owner || '/') AS ownerShowUrl, 
        ('/posts/' || p.postid || '/') AS postShowUrl, p.postid AS postid, ('/api/v1/posts/' || p.postid || '/') AS url
        FROM posts AS p JOIN users AS u ON p.owner=u.username WHERE p.postid=?""",(postid,))
    context = cur.fetchall()[0]
    
    cur = db.execute("SELECT comments.commentid AS commentid, CASE comments.owner WHEN ? THEN true ELSE false END lognameOwnsThis, "
                     "comments.owner AS owner, ('/users/' || comments.owner || '/') AS ownerShowUrl, "
                     "comments.text, ('/api/v1/comments/' || comments.commentid || '/') AS url "
                     "FROM comments JOIN posts ON posts.postid = comments.postid WHERE posts.postid = ?",(flask.session["username"], postid,))
    context["comments"] = list(cur.fetchall())
    
    cur = db.execute("SELECT * FROM (SELECT CASE likes.owner WHEN ? THEN true ELSE false END lognameLikesThis, "
                     "COUNT (*) AS numLikes FROM likes WHERE likes.postid = ?) "
                     "JOIN "
                     "(SELECT ('/api/v1/likes/' || likes.likeid || '/') AS url "
                     "FROM likes WHERE likes.owner = ? AND likes.postid = ?)", (flask.session["username"], postid, flask.session["username"], postid, ))
    
    context["likes"] = cur.fetchall()[0]
    cur = db.execute("")
    print(cur.fetchall())
    return flask.jsonify(**context), 200
  

@insta485.app.route('/api/v1/likes/?postid=<postid>',methods = ["POST","DELETE"])
@login_required
@postid_range_required
def post_like(postid):
  db = insta485.model.get_db()
  if flask.request.method == "POST":
    try:
      context = {}
      db.execute("INSERT INTO likes(owner,postid) VALUES (?,?)", (flask.session["username"],postid,))
      cur = db.execute("SELECT likes.likeid AS likeid, ('/api/v1/likes/' || likes.likeid || '/') AS url "
                       "FROM likes WHERE likes.owner = ? AND likes.postid = ?",(flask.session["username"],postid,))
      context = cur.fetchall()[0]
      return flask.jsonify(**context), 201
    except:
      return 'Conflict', 409
  elif flask.request.method == "DELETE":
    db.execute("DELETE FROM likes WHERE owner=? AND postid=?", (flask.session["username"],postid,))
    return 'NO CONTENT', 204
    
@insta485.app.route('/api/v1/comments/?postid=<postid>', methods = ["POST"])
@login_required
@postid_range_required
def post_comments(postid):
  db = insta485.model.get_db()
  if flask.request.method == "POST":
    db.execute("INSERT INTO comments(owner,postid,text) VALUES (?,?,?)", (flask.session["username"],postid,flask.request.json["text"],))
    return 201

@insta485.app.route('/api/v1/comments/<commentid>/', methods = ["DELETE"])
@login_required
@postid_range_required 
def delete_comment(commentid):
  db = insta485.model.get_db()
  if flask.request.method == "DELETE":
    db.execute("DELETE FROM comments WHERE owner = ? AND postid = ?", (flask.session["usernmae"],commentid,))
    return 'NO CONTENT', 204
    
