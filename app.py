from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)
app.secret_key = 'my secret key'
#set datebase connection settings
db = yaml.load(open('config.yaml'))
app.config['MYSQL_HOST'] = db['mysql']['host']
app.config['MYSQL_USER'] = db['mysql']['user']
app.config['MYSQL_PASSWORD'] = db['mysql']['pass']
app.config['MYSQL_DB'] = db['mysql']['db']

mysql = MySQL(app)
print(mysql)

#route for main-
#check if user in session and redirect accordingly
@app.route('/')
def Main():
    if 'user' not in session:
                return redirect(url_for('login'))
    return redirect(url_for('posts'))

#route for login-
#authenticate user details and redirect accordingly
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('posts'))
    msg = ''
    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']

        curs = mysql.connection.cursor()
        curs.execute('SELECT * FROM users WHERE user = %s AND password = %s', (user, password))
        account = curs.fetchone()
        if account:
            session['user'] = account[0]
            return redirect(url_for('posts'))
        else:
            msg = 'Username or Password are incorrect!'
    return render_template('welcome.html', msg=msg)

#route for logout-
#remove user session and redirect to login page
@app.route('/logout')
def logout():
   session.pop('user', None)
   return redirect(url_for('login'))

#route for post update-
#display the posts details and recieve update
@app.route('/postUpdate', methods = ['GET', 'POST'])
def update():
    if 'user' not in session:
        return redirect(url_for('login'))
    updateRes = ''
    curs = mysql.connection.cursor()
    if request.method == 'POST':
        #get post updated details
        postid = request.form.get('postToUpdate')
        title = request.form['title']
        content = request.form['content']
        adminContent = request.form['adminContent']
        tags = request.form['tags']
        curs.execute('SELECT * FROM users where user = %s', [session['user']])
        data = curs.fetchone()
        user = data[0]
        #update to post details according to the details received by admin user
        curs.execute('UPDATE posts SET user=%s, title=%s, content=%s, admin_content=%s, tags=%s WHERE id=%s', (user, title, content, adminContent, tags, postid))
        mysql.connection.commit()
        updateRes = str(curs.rowcount) + ' Post updated!'
        return redirect(url_for('posts'))
    #display the post details
    postID = request.args['id']
    curs.execute('SELECT * FROM posts where id = %s', (postID))
    postData = curs.fetchone()
    return render_template('postsUpdate.html', postDetails=postData, updateRes=updateRes)

#route for new post-
#receive post details from user and create a new entry in database
@app.route('/postsCreate', methods = ['GET', 'POST'])
def create():
    if 'user' not in session:
        return redirect(url_for('login'))
    createRes = ''
    if request.method == 'POST':
        #get new post details
        title = request.form['title']
        content = request.form['content']
        adminContent = request.form['adminContent']
        tags = request.form['tags']
        curs = mysql.connection.cursor()
        #create new post details according to the details received by admin user
        curs.execute('SELECT * FROM users where user = %s', [session['user']])
        data = curs.fetchone()
        user = data[0]
        curs.execute('INSERT INTO posts (user, title, content, admin_content, tags) values (%s, %s, %s, %s, %s)', (user, title, content, adminContent, tags))
        mysql.connection.commit()
        createRes = str(curs.rowcount) + ' Post inserted to DB!'
        return redirect(url_for('posts'))
    #loading new post page
    return render_template('postsCreate.html')


#route for reading posts-
#display all posts details
@app.route('/posts', methods = ['GET'])
def posts():
    if 'user' not in session:
        return redirect(url_for('login'))
    searchRes = ''
    curs = mysql.connection.cursor()
    curs.execute('SELECT * FROM users where user = %s', [session['user']])
    data = curs.fetchone()
    currentUserType = data[2]
    #get all posts in database
    curs.execute('SELECT * FROM posts')
    data = curs.fetchall()
    #redirect the user according to it's type (admin or regular)
    if currentUserType == 'admin':
        return render_template('posts.html', searchRes=searchRes, posts=data)
    else:
        return render_template('postsR.html', searchRes=searchRes, posts=data)

#route for post search-
#get post ID by user and disply post details
@app.route('/posts', methods = ['GET', 'POST'])
def search():
    if 'user' not in session:
        return redirect(url_for('login'))
    searchRes = ''
    curs = mysql.connection.cursor()
    curs.execute('SELECT * FROM users where user = %s', [session['user']])
    data = curs.fetchone()
    currentUserType = data[2]
    if request.method == 'POST':
        #get post ID
        postid =  request.form['search']
        #get post ID details from database
        curs.execute('SELECT * FROM posts WHERE id = %s', (postid))
        post = curs.fetchall()
        #redirect the post details to the posts page according to the user type (admin or regular)
        if post:
            if currentUserType == 'admin':
                return render_template('posts.html', posts=post)
            else:
                return render_template('postsR.html', posts=post)
        #post ID was not found, redirect to posts page according to the user type (admin or regular)
        else:
            searchRes = 'Post was not found in DB!'
            if currentUserType == 'admin':
                return render_template('posts.html', searchRes=searchRes)
            else:
                return render_template('postsR.html', searchRes=searchRes)
#route for post like-
#like or unlike post
@app.route('/likePost', methods = ['GET', 'POST'])
def like():
    if 'user' not in session:
        return redirect(url_for('login'))
    postToLike = request.args['id']
    curs = mysql.connection.cursor()
    curs.execute('SELECT * FROM users where user = %s', [session['user']])
    data = curs.fetchone()
    user = data[0]
    curs.execute('SELECT * FROM likes WHERE id=%s', (postToLike))
    mysql.connection.commit()
    likesNow = curs.rowcount
    #check if the user like/unlike the post
    curs.execute('SELECT * FROM likes WHERE id=%s AND user=%s', (postToLike, user))
    mysql.connection.commit()
    userLiked = curs.rowcount
    #update 'likes' and 'posts' table according to the user chice
    if  userLiked == 0:
        likesNow += 1
        print('Post to like')
        print(postToLike)
        #update 'likes' table by adding user like
        curs.execute('INSERT INTO likes (id, user) values (%s, %s)', (postToLike, user))
        mysql.connection.commit()
        print(likesNow)
        #update 'posts' table by incresing the like count
        curs.execute('UPDATE posts SET likes=%s WHERE id=%s', (likesNow, postToLike))
        mysql.connection.commit()
    else:
        likesNow -= 1
        #update 'likes' table by removing user like
        curs.execute('DELETE FROM likes where id = %s AND user=%s', (postToLike, user))
        mysql.connection.commit()
        print(likesNow)
        #update 'posts' table by decresing like count
        curs.execute('UPDATE posts SET likes=%s WHERE id=%s', (likesNow, postToLike))
        mysql.connection.commit()
    return redirect(url_for('posts'))

#route for post comments-
#display to post comments and enable to add a new comment
@app.route('/postComments', methods = ['GET', 'POST'])
def comments():
    if 'user' not in session:
        return redirect(url_for('login'))
    curs = mysql.connection.cursor()
    if request.method == 'POST':
        #get new comment
        postToComment = request.form.get('postToComment')
        comment = request.form['comment']
        curs.execute('SELECT * FROM users where user = %s', [session['user']])
        data = curs.fetchone()
        user = data[0]
        #update 'comments' table with a new user comment
        curs.execute('INSERT INTO comments (id, user, comment) values (%s, %s, %s)', (postToComment, user, comment))
        mysql.connection.commit()
        return redirect(url_for('posts'))
    #display the post comments
    postID = request.args['id']
    #get all posts comments from database
    curs.execute('SELECT * FROM comments where id=%s', (postID))
    mysql.connection.commit()
    data = curs.fetchall()
    return render_template('comments.html', comments=data, id=postID)

#route for delete post-
#get post ID and delete it from database and redirect to posts page
@app.route('/postDelete', methods = ['GET', 'POST'])
def delete():
    if 'user' not in session:
        return redirect(url_for('login'))
    #get post ID
    postDel = request.args['id']
    curs = mysql.connection.cursor()
    #delete the post form 'posts' table
    curs.execute('DELETE FROM posts where id = %s', (postDel))
    mysql.connection.commit()
    curs.execute('DELETE FROM comments where id = %s', (postDel))
    mysql.connection.commit()
    curs.execute('DELETE FROM likes where id = %s', (postDel))
    mysql.connection.commit()
    return redirect(url_for('posts'))


if __name__=='__main__':
    app.run(host='0.0.0.0', debug='True')
