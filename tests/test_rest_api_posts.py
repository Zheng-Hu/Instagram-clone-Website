"""Unit tests for posts routes in REST API."""
import pathlib
from base64 import b64encode
import sqlite3


def delete_created_time(response_json):
    """Delete "created" key since it will vary between requests."""
    for res in response_json["results"]:
        assert "created" in res
        del res["created"]
    return response_json


def test_posts_list(client):
    """Verify GET requests to posts list endpoint.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    credentials = b64encode(b"awdeorio:password").decode('utf-8')

    # Verify response with default database content
    response = client.get(
        "/api/v1/posts/",
        headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 200
    response_json = delete_created_time(response.get_json())

    assert response_json == {
        "next": "",
        "results": [
            {
                "comments": [
                    {
                        "commentid": 1,
                        "lognameOwnsThis": True,
                        "owner": "awdeorio",
                        "ownerShowUrl": "/users/awdeorio/",
                        "text": "#chickensofinstagram",
                        "url": "/api/v1/comments/1/"
                    },
                    {
                        "commentid": 2,
                        "lognameOwnsThis": False,
                        "owner": "jflinn",
                        "ownerShowUrl": "/users/jflinn/",
                        "text": "I <3 chickens",
                        "url": "/api/v1/comments/2/"
                    },
                    {
                        "commentid": 3,
                        "lognameOwnsThis": False,
                        "owner": "michjc",
                        "ownerShowUrl": "/users/michjc/",
                        "text": "Cute overload!",
                        "url": "/api/v1/comments/3/"
                    }
                ],
                "imgUrl":
                    "/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg",
                "likes": {
                    "lognameLikesThis": True,
                    "numLikes": 1,
                    "url": "/api/v1/likes/6/"
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/3/",
                "postid": 3,
                "url": "/api/v1/posts/3/"
            },
            {
                "comments": [
                    {
                        "commentid": 4,
                        "lognameOwnsThis": True,
                        "owner": "awdeorio",
                        "ownerShowUrl": "/users/awdeorio/",
                        "text": "Sick #crossword",
                        "url": "/api/v1/comments/4/"
                    }
                ],
                "imgUrl":
                    "/uploads/ad7790405c539894d25ab8dcf0b79eed3341e109.jpg",
                "likes": {
                    "lognameLikesThis": True,
                    "numLikes": 2,
                    "url": "/api/v1/likes/4/"
                },
                "owner": "jflinn",
                "ownerImgUrl":
                    "/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg",
                "ownerShowUrl": "/users/jflinn/",
                "postShowUrl": "/posts/2/",
                "postid": 2,
                "url": "/api/v1/posts/2/"
            },
            {
                "comments": [
                    {
                        "commentid": 5,
                        "lognameOwnsThis": False,
                        "owner": "jflinn",
                        "ownerShowUrl": "/users/jflinn/",
                        "text": "Walking the plank #chickensofinstagram",
                        "url": "/api/v1/comments/5/"
                    },
                    {
                        "commentid": 6,
                        "lognameOwnsThis": True,
                        "owner": "awdeorio",
                        "ownerShowUrl": "/users/awdeorio/",
                        "text":
                            "This was after trying to "
                            "teach them to do a #crossword",
                        "url": "/api/v1/comments/6/"
                    }
                ],
                "imgUrl":
                    "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
                "likes": {
                    "lognameLikesThis": True,
                    "numLikes": 3,
                    "url": "/api/v1/likes/1/"
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/1/",
                "postid": 1,
                "url": "/api/v1/posts/1/"
            }
        ],
        "url": "/api/v1/posts/"
    }


def test_posts_detail(client):
    """Verify GET requests to posts detail endpoint.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    credentials = b64encode(b"awdeorio:password").decode('utf-8')
    response = client.get(
        "/api/v1/posts/3/",
        headers={"Authorization": f"Basic {credentials}"},
    )
    assert response.status_code == 200

    # Overwrite timestamps, which will be different
    response_json = response.get_json()
    response_json["created"] = ""

    # Compare with correct response
    assert response_json == {
        "comments": [
            {
                "commentid": 1,
                "lognameOwnsThis": True,
                "owner": "awdeorio",
                "ownerShowUrl": "/users/awdeorio/",
                "text": "#chickensofinstagram",
                "url": "/api/v1/comments/1/"
            },
            {
                "commentid": 2,
                "lognameOwnsThis": False,
                "owner": "jflinn",
                "ownerShowUrl": "/users/jflinn/",
                "text": "I <3 chickens",
                "url": "/api/v1/comments/2/"
            },
            {
                "commentid": 3,
                "lognameOwnsThis": False,
                "owner": "michjc",
                "ownerShowUrl": "/users/michjc/",
                "text": "Cute overload!",
                "url": "/api/v1/comments/3/"
            }
        ],
        "created": "",
        "imgUrl": "/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg",
        "likes": {
            "lognameLikesThis": True,
            "numLikes": 1,
            "url": "/api/v1/likes/6/"
        },
        "owner": "awdeorio",
        "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
        "ownerShowUrl": "/users/awdeorio/",
        "postShowUrl": "/posts/3/",
        "postid": 3,
        "url": "/api/v1/posts/3/"
    }


def test_posts_autoincrement(db_connection):
    """Verify database uses AUTOINCREMENT for postids.

    This is important because the tests look at the postids and we want to give
    students an early warning if they make this mistake.
    """
    # Load student schema.sql
    schema_sql = pathlib.Path("sql/schema.sql").read_text(encoding='utf-8')
    assert "PRAGMA foreign_keys = ON" in schema_sql
    db_connection.executescript(schema_sql)
    db_connection.commit()

    # Add user awdeorio
    db_connection.execute(
        "INSERT INTO users(username, fullname, email, filename, password) "
        "VALUES ('awdeorio', 'Andrew DeOrio', 'awdeorio@umich.edu', "
        "'dummy.jpg', 'dummy'); "
    )

    # Add one new post and check postid
    db_connection.execute(
        "INSERT INTO posts(owner, filename) "
        " VALUES('awdeorio', '122a7d27ca1d7420a1072f695d9290fad4501a41.jpg')"
    )
    cur = db_connection.execute("SELECT postid FROM posts")
    postids = cur.fetchall()
    assert postids == [{'postid': 1}]

    # Delete post
    db_connection.execute("DELETE FROM posts")
    db_connection.commit()

    # Add one new post and check postid.  New post *should* not reuse deleted
    # postids
    db_connection.execute(
        "INSERT INTO posts(owner, filename) "
        " VALUES('awdeorio', '122a7d27ca1d7420a1072f695d9290fad4501a41.jpg')"
    )
    cur = db_connection.execute("SELECT postid FROM posts")
    postids = cur.fetchall()
    assert postids == [{'postid': 2}]


def test_posts_pagination_simple(client):
    """Verify GET 'posts' with two pages.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    # Log in
    credentials = b64encode(b"awdeorio:password").decode('utf-8')

    # Delete all likes, comments and posts.  The default database contains
    # postids {1,2,3,4}.  We're going to delete those and add new posts later
    # in this test.  The new posts will start with postid=5.
    connection = sqlite3.connect("var/insta485.sqlite3")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("DELETE FROM likes")
    connection.execute("DELETE FROM comments")
    connection.execute("DELETE FROM posts")

    # Create exactly 11 posts
    for _ in range(11):
        connection.execute(
            "INSERT INTO posts(owner, filename) "
            "VALUES('awdeorio', 'fox.jpg') ",
        )
    connection.commit()
    connection.close()

    # GET request with defaults return 10 most recent items
    response = client.get(
        "/api/v1/posts/",
        headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 200
    response_json = delete_created_time(response.get_json())

    assert response_json == {
        "next": "/api/v1/posts/?size=10&page=1&postid_lte=15",
        "results": [
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/15/",
                "postid": 15,
                "url": "/api/v1/posts/15/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/14/",
                "postid": 14,
                "url": "/api/v1/posts/14/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/13/",
                "postid": 13,
                "url": "/api/v1/posts/13/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/12/",
                "postid": 12,
                "url": "/api/v1/posts/12/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/11/",
                "postid": 11,
                "url": "/api/v1/posts/11/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/10/",
                "postid": 10,
                "url": "/api/v1/posts/10/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/9/",
                "postid": 9,
                "url": "/api/v1/posts/9/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/8/",
                "postid": 8,
                "url": "/api/v1/posts/8/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/7/",
                "postid": 7,
                "url": "/api/v1/posts/7/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/6/",
                "postid": 6,
                "url": "/api/v1/posts/6/"
            }
        ],
        "url": "/api/v1/posts/"
    }

    # GET request to second page returns 1 item, which is the first of our 11
    # new posts (the oldest).  Remember that our 11 posts are postids 5 to 15.
    # Thus, the postid of the oldest post is 5.
    response = client.get(
        "/api/v1/posts/?size=10&page=1&postid_lte=15",
        headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 200
    response_json = delete_created_time(response.get_json())

    assert response_json == {
        "next": "",
        "results": [
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/5/",
                "postid": 5,
                "url": "/api/v1/posts/5/"
            }
        ],
        "url": "/api/v1/posts/?size=10&page=1&postid_lte=15"
    }


def test_posts_pagination_page_size(client):
    """Verify GET 'posts' with pagination and 'page' and 'size' parameters.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    credentials = b64encode(b"awdeorio:password").decode('utf-8')

    # Delete all likes, comments and posts.  The default database contains
    # postids {1,2,3,4}.  We're going to delete those and add new posts later
    # in this test.  The new posts will start with postid=5.
    connection = sqlite3.connect("var/insta485.sqlite3")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("DELETE FROM likes")
    connection.execute("DELETE FROM comments")
    connection.execute("DELETE FROM posts")

    # Create exactly 11 posts
    for _ in range(11):
        connection.execute(
            "INSERT INTO posts(owner, filename) "
            "VALUES('awdeorio', 'fox.jpg') ",
        )
    connection.commit()
    connection.close()

    # GET page 1 size 6
    response = client.get(
        "/api/v1/posts/?size=6",
        headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 200
    response_json = delete_created_time(response.get_json())

    assert response_json == {
        "next": "/api/v1/posts/?size=6&page=1&postid_lte=15",
        "results": [
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/15/",
                "postid": 15,
                "url": "/api/v1/posts/15/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/14/",
                "postid": 14,
                "url": "/api/v1/posts/14/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/13/",
                "postid": 13,
                "url": "/api/v1/posts/13/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/12/",
                "postid": 12,
                "url": "/api/v1/posts/12/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/11/",
                "postid": 11,
                "url": "/api/v1/posts/11/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/10/",
                "postid": 10,
                "url": "/api/v1/posts/10/"
            }
        ],
        "url": "/api/v1/posts/?size=6"
    }

    # GET page 2 size 6
    response = client.get(
        "/api/v1/posts/?size=6&page=1&postid_lte=15",
        headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 200
    response_json = delete_created_time(response.get_json())

    assert response_json == {
        "next": "",
        "results": [
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/9/",
                "postid": 9,
                "url": "/api/v1/posts/9/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/8/",
                "postid": 8,
                "url": "/api/v1/posts/8/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/7/",
                "postid": 7,
                "url": "/api/v1/posts/7/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/6/",
                "postid": 6,
                "url": "/api/v1/posts/6/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/5/",
                "postid": 5,
                "url": "/api/v1/posts/5/"
            }
        ],
        "url": "/api/v1/posts/?size=6&page=1&postid_lte=15"
    }


def test_posts_pagination_upload_between_requests(client):
    """Verify correct results when another user uploads in between requests.

    1. Get first page of posts
    2. Create a new post
    3. Get second page of posts.  New posts *should not* be present.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    # Delete all likes, comments and posts.  The default database contains
    # postids {1,2,3,4}.  We're going to delete those and add new posts later
    # in this test.  The new posts will start with postid=5.
    connection = sqlite3.connect("var/insta485.sqlite3")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("DELETE FROM likes")
    connection.execute("DELETE FROM comments")
    connection.execute("DELETE FROM posts")

    # Create exactly 10 posts
    for _ in range(10):
        connection.execute(
            "INSERT INTO posts(owner, filename) "
            "VALUES('awdeorio', 'fox.jpg') ",
        )
    connection.commit()
    connection.close()

    credentials = b64encode(b"awdeorio:password").decode('utf-8')

    # GET request with defaults return 10 most recent items
    response = client.get(
        "/api/v1/posts/",
        headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 200
    response_json = delete_created_time(response.get_json())

    assert response_json == {
        "next": "/api/v1/posts/?size=10&page=1&postid_lte=14",
        "results": [
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/14/",
                "postid": 14,
                "url": "/api/v1/posts/14/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/13/",
                "postid": 13,
                "url": "/api/v1/posts/13/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/12/",
                "postid": 12,
                "url": "/api/v1/posts/12/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/11/",
                "postid": 11,
                "url": "/api/v1/posts/11/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/10/",
                "postid": 10,
                "url": "/api/v1/posts/10/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/9/",
                "postid": 9,
                "url": "/api/v1/posts/9/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/8/",
                "postid": 8,
                "url": "/api/v1/posts/8/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/7/",
                "postid": 7,
                "url": "/api/v1/posts/7/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/6/",
                "postid": 6,
                "url": "/api/v1/posts/6/"
            },
            {
                "comments": [],
                "imgUrl": "/uploads/fox.jpg",
                "likes": {
                    "lognameLikesThis": False,
                    "numLikes": 0,
                    "url": None
                },
                "owner": "awdeorio",
                "ownerImgUrl":
                    "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
                "ownerShowUrl": "/users/awdeorio/",
                "postShowUrl": "/posts/5/",
                "postid": 5,
                "url": "/api/v1/posts/5/"
            }
        ],
        "url": "/api/v1/posts/"
    }

    # Create one new post
    connection = sqlite3.connect("var/insta485.sqlite3")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute(
        "INSERT INTO posts(owner, filename) "
        "VALUES('awdeorio', 'fox.jpg') ",
    )
    connection.commit()
    connection.close()

    # GET request to second page returns no items, it should ignore the new
    # post we added.
    response = client.get(
        "/api/v1/posts/?size=10&page=1&postid_lte=14",
        headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 200
    assert response.get_json() == {
        "next": "",
        "results": [],
        "url": "/api/v1/posts/?size=10&page=1&postid_lte=14"
    }


def test_posts_pagination_errors(client):
    """Verify pagination error conditions.

    Note: 'client' is a fixture fuction that provides a Flask test server
    interface with a clean database.  It is implemented in conftest.py and
    reused by many tests.  Docs: https://docs.pytest.org/en/latest/fixture.html
    """
    credentials = b64encode(b"awdeorio:password").decode('utf-8')

    response = client.get(
        "/api/v1/posts/1000/",
        headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 404

    response = client.get(
        "/api/v1/posts/1000/comments/",
        headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 404

    response = client.get(
        "/api/v1/posts/1000/likes/",
        headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 404

    response = client.get(
        "/api/v1/posts/?page=-1",
        headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 400

    response = client.get(
        "/api/v1/posts/?size=-1",
        headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 400
