from flask import Flask, render_template, request, redirect, session, make_response, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = 'my_top_secret_123'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# путь к папке для сохранения файлов
UPLOAD_FOLDER = os.path.join(app.root_path, 'user_img')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if not query:
        # Если поиск пустой, можно либо перенаправить на страницу со всеми постами
        return redirect(url_for('all_cards'))
    # Поиск по заголовкам или другим полям
    cards = Card.query.filter(
        or_(
            Card.title.ilike(f'%{query}%')
        )
    ).all()
    return render_template('all_cards.html', cards=cards)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)
            return 'Файл сохранен!'


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #Заголовок
    title = db.Column(db.String(100), nullable=False)
    #Текст
    text = db.Column(db.Text, nullable=False)
    #email
    user_email = db.Column(db.String(100), nullable=False)
    #ФОТО
    user_img = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return f'<Card {self.id}>'
    



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

#Запуск страницы с контентом
@app.route('/log', methods=['GET','POST'])
def login():
    error = ''
    if request.method == 'POST':
        form_login = request.form['email']
        form_password = request.form['password']
        # проверкa пользователей
        users_db = User.query.all()
        for user in users_db:
            if form_login == user.email and form_password == user.password:
                session['user_email'] = user.email
                return redirect('/index')
        else:
            error = 'Неправильно указан пользователь или пароль'
            return render_template('login.html', error=error)
     
    else:
        return render_template('login.html')




@app.route('/reg', methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect('/')
    
    else:    
        return render_template('registration.html')
    
# свои карты
@app.route('/index')
def index():
    email = session.get('user_email')
    cards = Card.query.filter_by(user_email=email).all()
    return render_template('index.html', cards=cards)

@app.route('/')
def allcards():
    cards = Card.query.order_by(Card.created_at.desc()).all()
    return render_template('all_cards.html', cards=cards)

@app.route('/all')
def allcardslog():
    cards = Card.query.order_by(Card.created_at.desc()).all()
    return render_template('all_cards_log.html', cards=cards)

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/info_al')
def info_al():
    return render_template('info_al.html')

@app.route('/card/<int:id>')
def card(id):
    card = Card.query.get(id)

    return render_template('card.html', card=card)




@app.route('/card_al/<int:id>')
def card_al(id):
    card = Card.query.get(id)

    return render_template('card_al.html', card=card)





@app.route('/create')
def create():
    return render_template('create_card.html')

@app.route('/form_create', methods=['GET', 'POST'])
def form_create():
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['text']
        file = request.files['user_img']
        if file:
            # Вставьте сюда
            filename = secure_filename(file.filename)
            static_path = os.path.join('static', 'user_img', filename)
            save_path = os.path.join(app.root_path, static_path)
            file.save(save_path)
            # сохраняем относительный путь для использования в шаблоне
            user_img_path = static_path
        else:
            error = 'Пожалуйста, выберите изображение для загрузки'
            return render_template('create_card.html', error=error)
        # далее сохраняете карточку, передавая user_img=user_img_path
        user_email = session.get('user_email')
        card = Card(title=title, text=text, user_email=user_email, user_img=user_img_path)
        db.session.add(card)
        db.session.commit()
        return redirect('/index')
    return render_template('create_card.html')



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
