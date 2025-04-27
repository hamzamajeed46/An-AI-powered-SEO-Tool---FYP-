from flask import request, redirect, url_for, render_template, session
from pymongo import MongoClient
import hashlib

# MongoDB connection setup
def get_db_connection():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['seotool']  # your database
        print("Connected to MongoDB successfully!")
        return db
    except Exception as e:
        print("MongoDB connection failed:", e)
        return None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password_hash(stored_password, input_password):
    return stored_password == hash_password(input_password)

# Sign up route
def signup_route():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        username = request.form["username"]

        db = get_db_connection()
        users_collection = db['users']

        # Check if the email already exists
        user = users_collection.find_one({"email": email})

        if user:
            return "Email already exists, please log in."

        # Insert the new user
        users_collection.insert_one({
            "email": email,
            "password": hash_password(password),
            "username": username
        })

        user = users_collection.find_one({"email": email})

        if user and check_password_hash(user['password'], password):
            # Store user info in session
            session['user_id'] = str(user['_id'])  # MongoDB _id
            session['username'] = user['username']
            session['email'] = user['email']
            return redirect(url_for('home'))

    return render_template('signup.html')

# Sign in route
def login_route():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db_connection()
        users_collection = db['users']

        # Fetch user from database
        user = users_collection.find_one({"email": email})

        if user and check_password_hash(user['password'], password):
            # Store user info in session
            session['user_id'] = str(user['_id'])  # MongoDB _id
            session['username'] = user['username']
            session['email'] = user['email']
            return redirect(url_for('home'))
        else:
            return "Invalid email or password."

    return render_template('signin.html')
