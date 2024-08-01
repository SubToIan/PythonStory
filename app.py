import os
from flask import Flask, render_template, request, redirect, send_file, url_for, session
from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Story
from openai import OpenAI
from fpdf import FPDF

client = OpenAI(
    api_key="sk-proj-418yuqNf2J1kqvnnFIimT3BlbkFJSSTeZ7wSSRZmxv33kU4m"
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stories.db'
app.config['SECRET_KEY'] = 'your_secret_key2'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = password #generate_password_hash(password, method='sha256')

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password: # check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/generate', methods=['POST'])
def generate_story():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # 사용자 입력 정보 가져오기
    topic = request.form['topic']
    genre = request.form['genre']
    length = request.form['length']
    character = request.form.get('character', '')

    # GPT API 요청
    messages = [
        {'role': 'system', 'content': f"당신은 창의적인 이야기 작가입니다. 장르: {genre}, 길이: {length}."},
        {'role': 'user', 'content': f"주제: {topic}, 캐릭터: {character}"}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo", #"gpt-4o-mini",
        messages=messages
    )
    story_content = response.choices[0].message.content

    # 이야기 저장
    new_story = Story(title=topic, content=story_content, user_id=session['user_id'])
    db.session.add(new_story)
    db.session.commit()

    return redirect(url_for('dashboard'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    stories = Story.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', stories=stories)

@app.route('/story/<int:id>')
def view_story(id):
    story = Story.query.get_or_404(id)
    return render_template('view_story.html', story=story)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_story(id):
    story = Story.query.get_or_404(id)

    if request.method == 'POST':
        story.title = request.form['title']
        story.content = request.form['content']
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('edit_story.html', story=story)

@app.route('/delete/<int:id>')
def delete_story(id):
    story = Story.query.get_or_404(id)
    db.session.delete(story)
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)

