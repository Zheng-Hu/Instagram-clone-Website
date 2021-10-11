"""REST API for posts."""
import flask
from flask import jsonify, hashlib
import insta485
from functools import wraps

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message='Bad Request', status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv["status_code"] = self.status_code
        return rv

@insta485.app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
  
def postid_range_required(f):
    @wraps(f)
    def decorated_function(postid):
        db = insta485.model.get_db()
        cur = db.execute("SELECT postid FROM posts WHERE postid=?",(postid,))
        if not list(cur.fetchall()):
          flask.abort(404)
        return f(postid)
    return decorated_function

def check_password(password,password_db_string):
  [algorithm, salt, password_hash] = password_db_string.split("$")
  hash_obj = hashlib.new(algorithm)
  password_salted = salt + password
  hash_obj.update(password_salted.encode('utf-8'))
  return hash_obj.hexdigest() == password_hash

def check_authentication(f):
  @wraps(f)
  def decorated_function(*args,**kwargs):
    if flask.request.authorization == None and flask.sessions == None:
      raise InvalidUsage('Forbidden', status_code=403)
    elif flask.request.authorization != None:
      username = flask.request.authorization['username']
      password = flask.request.authorization['password']
      db = insta485.model.get_db()
      cur = db.execute("SELECT password FROM users WHERE username=?",(username,))
      res = list(cur.fetchall())
      if res.__len__ == 0 or not check_password(password,res[0]['password']):
        raise InvalidUsage('Forbidden', status_code=403)
    elif flask.sessions != None:
        if not flask.session.get('logged_in'):
          flask.abort(403)
        username = flask.session["username"]
    return f(*args,**kwargs)
  return decorated_function

def get_username():
  if flask.session:
    username = flask.session["username"]
  elif flask.request.authorization:
    username = flask.request.authorization['username']
  else:
    raise InvalidUsage('Forbidden', status_code=403)
  return username
  
            
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
@check_authentication
def posts():
  db = insta485.model.get_db()
  size = flask.request.args.get("size",default=10,type=int)
  page = flask.request.args.get("page",default=0,type=int)

  username = get_username()
    
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
                   (username,username,size,size,page,))
  
  context['results'] = list(cur.fetchall())
  cur = db.execute( "SELECT * FROM (SELECT CASE likes.owner WHEN ? THEN true ELSE false END lognameLikesThis, "
                     "COUNT (*) AS numLikes FROM likes JOIN posts AS p ON likes.postid = p.postid "
                     "WHERE p.owner=? OR p.owner IN (SELECT username2 FROM following WHERE username1=?) ORDER BY p.created DESC, p.postid DESC LIMIT ? OFFSET ? * ?)"
                     "JOIN "
                     "(SELECT ('/api/v1/likes/' || likes.likeid || '/') AS url "
                     "FROM likes JOIN posts AS p ON likes.owner = ? AND likes.postid = p.postid "
                     "WHERE p.owner=? OR p.owner IN (SELECT username2 FROM following WHERE username1=?) ORDER BY p.created DESC, p.postid DESC LIMIT ? OFFSET ? * ?)",\
                     (username, username,username, size, size, page, username, username,username, size, size, page, ))
  context['likes'] = list(cur.fetchall())
  cur = db.execute("SELECT COUNT(*) AS num FROM posts WHERE owner=? OR "
                   "owner IN (SELECT username2 FROM following WHERE username1=?)", \
                     (username,username,))
  if size*(page+1) >= cur.fetchall()[0]["num"]:
    context['next'] = ''
  else:
    context['next'] = f"/api/v1/p/?size={size}&page={page+1}"
  return flask.jsonify(**context);

@insta485.app.route('/api/v1/posts/<int:postid>/', methods=["GET"])
@check_authentication
@postid_range_required

def get_post(postid):
    username = get_username()

    db = insta485.model.get_db()
    cur = db.execute("""SELECT p.created AS created, ('/uploads/' || p.filename) AS imgUrl, p.owner AS owner, 
        ('/uploads/' || u.filename) AS ownerImgUrl, ('/users/' || p.owner || '/') AS ownerShowUrl, 
        ('/posts/' || p.postid || '/') AS postShowUrl, p.postid AS postid, ('/api/v1/posts/' || p.postid || '/') AS url
        FROM posts AS p JOIN users AS u ON p.owner=u.username WHERE p.postid=?""",(postid,))
    context = cur.fetchall()[0]
    
    cur = db.execute("SELECT comments.commentid AS commentid, CASE comments.owner WHEN ? THEN true ELSE false END lognameOwnsThis, "
                     "comments.owner AS owner, ('/users/' || comments.owner || '/') AS ownerShowUrl, "
                     "comments.text, ('/api/v1/comments/' || comments.commentid || '/') AS url "
                     "FROM comments JOIN posts ON posts.postid = comments.postid WHERE posts.postid = ?",(username, postid,))
    context["comments"] = list(cur.fetchall())
    
    cur = db.execute("SELECT * FROM (SELECT CASE likes.owner WHEN ? THEN true ELSE false END lognameLikesThis, "
                     "COUNT (*) AS numLikes FROM likes WHERE likes.postid = ?) "
                     "JOIN "
                     "(SELECT ('/api/v1/likes/' || likes.likeid || '/') AS url "
                     "FROM likes WHERE likes.owner = ? AND likes.postid = ?)", (username, postid, username, postid, ))
    
    likes = cur.fetchall()

    if len(likes)== 0:
      context["likes"] = {
        "numLikes": 0,  
        "lognameLikesThis": 0,  
        "url": None,
      }
    else:
      context["likes"] = likes[0]

    return flask.jsonify(**context), 200
  

@insta485.app.route('/api/v1/likes/<int:likeid>/',methods = ["POST","DELETE"])
@check_authentication
def like(likeid):
  username = get_username()
  
  db = insta485.model.get_db()
  if flask.request.method == "POST":
    try:
      context = {}
      db.execute("INSERT INTO likes(owner,postid) VALUES (?,?)", (username,likeid,))
      cur = db.execute("SELECT likes.likeid AS likeid, ('/api/v1/likes/' || likes.likeid || '/') AS url "
                       "FROM likes WHERE likes.owner = ? AND likes.postid = ?",(username,likeid,))
      context = cur.fetchall()[0]
      return flask.jsonify(**context), 201
    except:
      raise InvalidUsage('Conflict', status_code=409)
  elif flask.request.method == "DELETE":
    try:
      db.execute("DELETE FROM likes WHERE owner=? AND likeid=?", (username,likeid,))
      return 'NO CONTENT', 204
    except:
      return 'NO CONTENT', 204
@insta485.app.route('/api/v1/comments/?postid=<postid>', methods = ["POST"])
@check_authentication
@postid_range_required
def post_comments(postid):
  
  username = get_username()
  
  db = insta485.model.get_db()
  if flask.request.method == "POST":
    db.execute("INSERT INTO comments(owner,postid,text) VALUES (?,?,?)", (username,postid,flask.request.json["text"],))
    return 201

@insta485.app.route('/api/v1/comments/<commentid>/', methods = ["DELETE"])
@check_authentication
@postid_range_required 
def delete_comment(commentid):
  
  username = get_username()
  
  db = insta485.model.get_db()
  if flask.request.method == "DELETE":
    db.execute("DELETE FROM comments WHERE owner = ? AND postid = ?", (username,commentid,))
    return 'NO CONTENT', 204
    
