import os
from flask import current_app as app
from . import db
from flask import render_template, request, redirect, url_for, jsonify, Response
from pony.orm import *
from .forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash
from . import s3_helpers


set_sql_debug(True)



@app.route('/api/chats/<int:chat_id>/messages', methods=['GET', 'POST'])
def messages(chat_id):
    

    user_id = int(request.args.get('user_id'))


    # check if user in database

    try:
        chat = db.Chat[chat_id]
        user = db.User[user_id]
    except ObjectNotFound:
        return("User Does Not Exsist")

    # returns json of all chat messages

    if request.method == 'GET':
        if user not in chat.users:
            return "Page not found", 404
        else:  
            return jsonify([
                {
                    'id': m.id,
                    'body': m.body,
                    'sender_first': m.sender_id.first_name,
                    'sender_last': m.sender_id.last_name,
                    'sender_id' : m.sender_id.id,
                    'time-stamp': m.date_created

                }
                for m in chat.messages.order_by(lambda m: desc(m.date_created))
            ])

    # post message to database

    if request.method == 'POST':

        if not request.content_type == 'application/json':
            return "Invalid request.  Content type must be 'application/json'"
        
        r = request.get_json()
        body = r['body']

        with db_session:
            message = db.Message(body=body, sender_id=user, chat=chat)
            commit()
            return jsonify({
                    'id': message.id,
                    'body': message.body,
                    'sender_first': message.sender_id.first_name,
                    'sender_last': message.sender_id.last_name,
                    'sender_id' : message.sender_id.id,
                    'time-stamp': message.date_created

                })
        



@db_session
@app.route('/api/chats', methods=['GET', 'POST'])
def chats():

    user_id = current_user.get_id()

    user = db.User[user_id]

    if request.method == 'GET':
        chats = []
        for c in user.chats:
            chats.append({"id": c.id,
                            "last_updated": c.last_updated})
        return jsonify(chats)


    if request.method == 'POST':
        r = request.get_json()
    
        email = r['email']
        sender_id = r['sender_id']

        sender = db.User[sender_id]

        try:
            receipent = db.User.get(email=email)
            print(receipent)
            print(sender)
        except ObjectNotFound:
            return "User does not exsist", 404

        chat = db.Chat(chat_name=receipent.full_name, creator_id=sender.id)
        commit()
        chat.users.add(sender)
        chat.users.add(receipent)
        return "Test"



@app.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    if request.method == "POST":
        f = request.files['file']
        f.save(os.path.join(UPLOAD_FOLDER, f.filename))
        upload_file(f"uploads/{f.filename}", BUCKET)
        




# add users to chat.  Get list of chat users
@app.route('/api/chats/<int:chat_id>/users', methods=['GET', 'POST'])
def chat_users(chat_id):

    try:
        chat = db.Chat[chat_id]
    except ObjectNotFound:
        return "Chat Id not found"

    if request.method == 'GET':
        pass

    if request.method == 'POST':
        user_id = request.args.get('user_id')

        try:
            user = db.User[user_id]
        except ObjectNotFound:
            return "User does not exist"

        chat.users.add(user)
        
        return "Chat added", 201
        


@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('home'))



# BROKEN
@app.route('/api/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        if not request.content_type == 'application/json':
            return "Invalid request. Content type must be 'application/json'"

        r = request.get_json()
        first_name = r['first_name']
        last_name = r['last_name']
        email = r['email']
        password = r['password']

        with db_session:
            user = db.User(first_name=first_name, last_name=last_name, email=email, password=password)

            return "User successfully added."



@db_session
@app.route('/chat', methods=['GET'])
def home():

    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    user = current_user.get_id()

    try:
        user = db.User[user]
    except ObjectNotFound:
        return("User Does not Exist")

    chats = []
    for c in user.chats:
        
        try:
            last_message = c.messages.select().order_by(lambda m: desc(m.date_created)).limit(1)[0].body
        except IndexError:
            last_message = "Tap to send a message"
        chats.append({"id": c.id, 
                      "last_updated": c.last_updated,
                      "last_message": last_message,
                      "chat_name": user.first_name,
                      "avatar": c.avatar})
    
    return render_template('chat.html', chats=chats, user=current_user)
    




@db_session
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        user_id = current_user.get_id()
        return redirect(url_for('home', user_id=[user_id]))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = db.User(email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data, password=generate_password_hash(form.password.data))
        return redirect(url_for('login'))
    return render_template('register.html', form=form)



@db_session
@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        user_id = current_user.get_id()
        return redirect(url_for('home', user_id=[user_id]))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.User.get(email=email)
        print(user.user_id)
        if user.check_password_hash(form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            return "Did not work"
    return render_template('login.html', form=form)



@app.route('/logout')
def logout():
    logout_user()
    return "You are logged out"