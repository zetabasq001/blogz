from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:o4n*#8kK@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = "kdi76%@jd#@gdhYDETXG"

db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(228))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
     
@app.route("/")
def index():
    users = User.query.all()
    return render_template("index.html", users=users)

@app.route("/login", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in", 'success')
            return redirect("/newpost")
        else:
            flash("User password incorrect or user does not exist", "error")

    return render_template("login.html")
            
@app.route("/signup", methods = ["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        verify = request.form["verify"]
        password_error, verify_error, username_error = "","",""

        if username == "" or " " in username or len(username) < 3 or len(username) > 20:
            username_error = "Please enter a valid username"

        if password == "" or " " in password or len(password) < 3 or len(password) > 20:
            password_error = """Please enter a valid password:
                                no spaces, no less than three
                                characters"""
        elif verify != password:
            verify_error = "Password mismatch"

        user = User.query.filter_by(username=username).first()   
        if user:
            duplicate_user = "Username already exists" 

        if not user and not password_error and not verify_error and not username_error:
            user = User(username, password)
            db.session.add(user)
            db.session.commit()
            session['username'] = username
            return redirect("/newpost")
        elif user:
            flash(duplicate_user, 'error')
        elif username_error:
            flash(username_error, 'error')
        elif password_error:
            flash(password_error, 'error')
        else:
            flash(verify_error, 'error')

    return render_template("signup.html")

@app.route("/blog")
def main_blog():
    user_id = request.args.get("user")
    if user_id:
        username = User.query.filter_by(id=user_id).first().username
        user_blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template("singleUser.html", user_blogs=user_blogs, username=username,
        user_id=user_id)

    blog_id = request.args.get("id")
    if blog_id:   
        blog = Blog.query.get(blog_id)   
        return render_template("blogpage.html", blog_title=blog.title, blog_body=blog.body,
            blog_owner_id=blog.owner_id, username=blog.owner.username)
    
    blogs = Blog.query.all()
    return render_template("blog.html", tab_title="All Blogz", blogs=blogs)

@app.route("/newpost", methods = ["POST", "GET"])
def new_post():  
    if request.method == "POST":
        title_error = ""
        body_error = ""

        blog_title = request.form["blog_title"]
        blog_body = request.form["blog_body"]

        if blog_title == "":
            title_error = "Please fill in the title"
        if blog_body == "":
            body_error = "Please fill in the body"

        if title_error or body_error:
            return render_template("newpost.html", title_error=title_error,
                body_error=body_error, blog_title=blog_title, blog_body=blog_body)

        username = session['username']
        user = User.query.filter_by(username=username).first()
        new_blog = Blog(blog_title, blog_body, user)
        db.session.add(new_blog)
        db.session.commit()
    
        return redirect("/blog?id={0}".format(new_blog.id))
    else:
        return render_template("newpost.html", tab_title="Add a Blog Entry")

@app.route("/logout")
def logout():
    del session['username']
    return redirect('/blog')

@app.before_request
def require_login():
    allowed_routes = ["login", "main_blog", "index", "signup", "logout"]
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")
  
if __name__ == '__main__':
    app.run()