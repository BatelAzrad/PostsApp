import mysql.connector
import yaml

yaml.warnings({'YAMLLoadWarning': False})

db = yaml.load(open('config.yaml'))

mydb = mysql.connector.connect(
    host = db['mysql']['host'],
    user = db['mysql']['user'],
    password = db['mysql']['pass'],
    database = 'mydev'
)

mycursor = mydb.cursor()

#Create database
mycursor.execute("CREATE DATABASE IF NOT EXISTS mydev")
mydb.commit()

#Create tables in database
mycursor.execute("CREATE TABLE IF NOT EXISTS users ( user varchar(30) NOT NULL, password varchar(30) NOT NULL, type varchar(5) NOT NULL, PRIMARY KEY (user))")
mycursor.execute("CREATE TABLE IF NOT EXISTS posts ( id int NOT NULL auto_increment unique, user varchar(30) NOT NULL, title varchar(255) NOT NULL, content text NOT NULL, admin_content text, tags varchar(255),likes int NOT NULL DEFAULT 0, PRIMARY KEY (id))")
mycursor.execute("CREATE TABLE IF NOT EXISTS likes ( id int NOT NULL, user varchar(30) NOT NULL)")
mycursor.execute("CREATE TABLE IF NOT EXISTS comments ( id int NOT NULL , user varchar(30) NOT NULL, comment text NOT NULL)")

mydb.commit()

#Insert users into database
mycursor.execute("insert into users (user, password, type) values ('batel', '123456', 'admin')")
mycursor.execute("insert into users (user, password, type) values ('kira', '123456', 'admin')")
mycursor.execute("insert into users (user, password, type) values ('red', '123456', 'user')")
mydb.commit()

#Insert users into database
mycursor.execute("insert into posts (user, title, content, admin_content, tags) values ('kira', '3 places to bury my bone', '1) Yard, 2) Under my parents bed, 3) Inside the pot. - Woff-Woff Kira', '', '')")
mycursor.execute("insert into posts (user, title, content, admin_content, tags) values ('batel', 'My developing skills', 'Python, Javascript, Java, HTML, CSS, etc.', 'Software engineer skills', '\#Developer \#Software')")
mydb.commit()
