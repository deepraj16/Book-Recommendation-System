from flask import Flask ,render_template,url_for,request,flash,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

import pandas as pd
import numpy as np
import pickle
app =Flask(__name__,)

app.config['SECRET_KEY'] = 'mysecretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


popular_df =pickle.load(open('popular.pkl','rb'))
pt =pickle.load(open('pt.pkl','rb'))
books =pickle.load(open('books.pkl','rb'))
similarty_score =pickle.load(open('similarty_score.pkl','rb'))

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)



# Form for user registration
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


# Form for user login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')












class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Create the database and table
with app.app_context():
    db.create_all()



@app.route('/books')
def view_books():
    # Fetch all books from the database
    #books = Book.query.all()
    return render_template('view_books.html', books=books)

@app.route('/add1', methods=['POST'])
def add_book1():
    page=request.form['book_name']
    return page


# @app.route('/add', methods=['POST'])
# def add_book():
#     # Get the book name from the form
#     book_name = request.form['book_name']

#     # Create a new book instance
#     new_book = Book(name=book_name)

#     # Add and commit the new book to the database
#     db.session.add(new_book)
#     db.session.commit()

    return redirect(url_for('view_books'))

@app.route('/delete/<int:book_id>')
def delete_book(book_id):
    # Get the book by ID from the database
    book_to_delete = Book.query.get_or_404(book_id)

    # Delete the book
    db.session.delete(book_to_delete)
    db.session.commit()

    return redirect(url_for('view_books'))

@app.route('/check', methods=['GET'])
def check_book():
    # Redirect to view books when "Check" is clicked
    return redirect(url_for('view_books'))






# recomed funtions 
# def recommend(book_name): 
#     index=np.where(pt.index==book_name)[0][0]
#     distance=similarty_score[index]
#     similar_items=sorted(list(enumerate(similarty_score[index])),key=lambda x:x[1],reverse=True)[1:6]
#     data=[]
#     for i in similar_items : 
#         items=[]
#         temp_df = books[books['Book-Title']==pt.index[i[0]]]
#         items.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
#         items.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
#         items.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

#         data.append(items)

#     return data 
#     #return suggenstion
popular_df1=popular_df.sample(50)
l=["The Hitchhiker's Guide to the Galaxy","The Color Purple","Outlander"]
for i in l:
   popular_df1=popular_df1[popular_df['Book-Title']!=i]


@app.route('/add_book')
def add_book():
    return render_template("add_books.html",book_name=(popular_df1['Book-Title'].values),
                           author=list(popular_df1['Book-Author'].values),
                           image=list(popular_df1['Image-URL-M'].values))

@app.route("/")
@app.route("/home")
def start(): 
    form = LoginForm()
    return render_template("start.html", book_name=list(popular_df1['Book-Title'].values),
                           author=list(popular_df1['Book-Author'].values),
                           image=list(popular_df1['Image-URL-M'].values) ,form=form)


@app.route("/Top-50")
def home(): 
    return render_template("home.html",
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_ratings'].values)
                           )

@app.route("/recommend")
def recommend(): 
    return render_template("recommend.html",
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_ratings'].values))

@app.route("/recommend_books",methods=['POST'])
def recommend_ui(): 
    user_input=request.form.get("user_input")
    user_input=user_input
    print(type(user_input))
    index=np.where(pt.index==user_input)
    print(len(index))
    if len(index)==0:
        index=698
    else : 
        index=index[0][0]
    distance=similarty_score[index]
    similar_items=sorted(list(enumerate(similarty_score[index])),key=lambda x:x[1],reverse=True)[0:6]
    data=[]
    for i in similar_items : 
        items=[]
        temp_df = books[books['Book-Title']==pt.index[i[0]]]
        items.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        items.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        items.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(items)
    print(data)
    return render_template('recommend.html',data=data,image=list(popular_df['Image-URL-M'].values))




@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # Initialize registration form
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists, please choose a different one.')
            return redirect(url_for('register'))

        # Create new user entry
        new_user = User(username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, password=form.password.data).first()
        if user:
            flash('Login successful!')
            return redirect(url_for('start'))
        else:
            flash('Login failed. Check your username and password.')
    return render_template('login.html', form=form)




if __name__ =="__main__": 
    app.run(debug=True)