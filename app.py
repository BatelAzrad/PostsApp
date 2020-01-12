from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)
app.secret_key = 'my secret key'

db = yaml.load(open('config.yaml'))
app.config['MYSQL_HOST'] = db['mysql']['host']
app.config['MYSQL_USER'] = db['mysql']['user']
app.config['MYSQL_PASSWORD'] = db['mysql']['pass']
app.config['MYSQL_DB'] = db['mysql']['db']

mysql = MySQL(app)
print(mysql)

@app.route('/')
def Main():
    if 'user' not in session:
                return redirect(url_for('login'))
    return redirect(url_for('posts'))

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

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('user', None)
   # Redirect to login page
   return redirect(url_for('login'))



@app.route('/postUpdate', methods = ['GET', 'POST'])
def update():
    if 'user' not in session:
        return redirect(url_for('login'))
    updateRes = ''
    curs = mysql.connection.cursor()
    if request.method == 'POST':
        postid = request.form.get('postToUpdate')
        title = request.form['title']
        content = request.form['content']
        adminContent = request.form['adminContent']
        tags = request.form['tags']
        curs.execute('SELECT * FROM users where user = %s', [session['user']])
        data = curs.fetchone()
        user = data[0]
        curs.execute('UPDATE posts SET user=%s, title=%s, content=%s, admin_content=%s, tags=%s WHERE id=%s', (user, title, content, adminContent, tags, postid))
        mysql.connection.commit()
        updateRes = str(curs.rowcount) + ' Post updated!'
        return redirect(url_for('posts'))
    postID = request.args['id']
    curs.execute('SELECT * FROM posts where id = %s', (postID))
    postData = curs.fetchone()
    return render_template('postsUpdate.html', postDetails=postData, updateRes=updateRes)



@app.route('/postsCreate', methods = ['GET', 'POST'])
def create():
    if 'user' not in session:
        return redirect(url_for('login'))
    createRes = ''
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        adminContent = request.form['adminContent']
        tags = request.form['tags']
        curs = mysql.connection.cursor()
        curs.execute('SELECT * FROM users where user = %s', [session['user']])
        data = curs.fetchone()
        user = data[0]
        curs.execute('INSERT INTO posts (user, title, content, admin_content, tags) values (%s, %s, %s, %s, %s)', (user, title, content, adminContent, tags))
        mysql.connection.commit()
        createRes = str(curs.rowcount) + ' Post inserted to DB!'
        return redirect(url_for('posts'))
    return render_template('postsCreate.html')




@app.route('/posts', methods = ['GET'])
def posts():
    if 'user' not in session:
        return redirect(url_for('login'))
    searchRes = ''
    curs = mysql.connection.cursor()
    curs.execute('SELECT * FROM users where user = %s', [session['user']])
    data = curs.fetchone()
    currentUserType = data[2]
    curs.execute('SELECT * FROM posts')
    data = curs.fetchall()
    if currentUserType == 'admin':
        return render_template('posts.html', searchRes=searchRes, posts=data)
    else:
        return render_template('postsR.html', searchRes=searchRes, posts=data)


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
        postid =  request.form['search']
        curs.execute('SELECT * FROM posts WHERE id = %s', (postid))
        post = curs.fetchall()
        if post:
            if currentUserType == 'admin':
                return render_template('posts.html', posts=post)
            else:
                return render_template('postsR.html', posts=post)
        else:
            searchRes = 'Post was not found in DB!'
            if currentUserType == 'admin':
                return render_template('posts.html', searchRes=searchRes)
            else:
                return render_template('postsR.html', searchRes=searchRes)


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
    curs.execute('SELECT * FROM likes WHERE id=%s AND user=%s', (postToLike, user))
    mysql.connection.commit()
    userLiked = curs.rowcount
    if  userLiked == 0:
        likesNow += 1
        print('Post to like')
        print(postToLike)
        curs.execute('INSERT INTO likes (id, user) values (%s, %s)', (postToLike, user))
        mysql.connection.commit()
        print(likesNow)
        curs.execute('UPDATE posts SET likes=%s WHERE id=%s', (likesNow, postToLike))
        mysql.connection.commit()
    else:
        likesNow -= 1
        curs.execute('DELETE FROM likes where id = %s AND user=%s', (postToLike, user))
        mysql.connection.commit()
        print(likesNow)
        curs.execute('UPDATE posts SET likes=%s WHERE id=%s', (likesNow, postToLike))
        mysql.connection.commit()
    return redirect(url_for('posts'))


@app.route('/postComments', methods = ['GET', 'POST'])
def comments():
    if 'user' not in session:
        return redirect(url_for('login'))
    curs = mysql.connection.cursor()
    if request.method == 'POST':
        postToComment = request.form.get('postToComment')
        comment = request.form['comment']
        curs.execute('SELECT * FROM users where user = %s', [session['user']])
        data = curs.fetchone()
        user = data[0]
        curs.execute('INSERT INTO comments (id, user, comment) values (%s, %s, %s)', (postToComment, user, comment))
        mysql.connection.commit()
        return redirect(url_for('posts'))
    postID = request.args['id']
    curs.execute('SELECT * FROM comments where id=%s', (postID))
    mysql.connection.commit()
    data = curs.fetchall()
    return render_template('comments.html', comments=data, id=postID)



@app.route('/postDelete', methods = ['GET', 'POST'])
def delete():
    if 'user' not in session:
        return redirect(url_for('login'))
    postDel = request.args['id']
    curs = mysql.connection.cursor()
    curs.execute('DELETE FROM posts where id = %s', (postDel))
    mysql.connection.commit()
    return redirect(url_for('posts'))




if __name__=='__main__':
    app.run(host='0.0.0.0', debug='True')
