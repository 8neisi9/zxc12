from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, EqualTo, NumberRange
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
# Инициализация приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Замените на секретный ключ
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # База данных SQLite
db = SQLAlchemy(app)
# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
# Модель пользователя
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
# Модель комментария
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)  # Текст комментария
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ID пользователя
    product_id = db.Column(db.Integer, nullable=False)  # ID товара (можно сделать ForeignKey, если есть модель товара)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Время создания комментария
    user = db.relationship('User', backref=db.backref('comments', lazy=True))  # Связь с моделью User
# Модель оценки
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)  # Значение оценки (от 1 до 5)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ID пользователя
    product_id = db.Column(db.Integer, nullable=False)  # ID товара
    user = db.relationship('User', backref=db.backref('ratings', lazy=True))  # Связь с моделью User
# Форма регистрации
class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')
# Форма входа
class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)  # ФИО
    address = db.Column(db.String(200), nullable=False)  # Адрес доставки
    zip_code = db.Column(db.String(20), nullable=False)  # Индекс
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ID пользователя
    user = db.relationship('User', backref=db.backref('orders', lazy=True))  # Связь с моделью User
# Загрузка пользователя
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# Маршруты
@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')
@app.route("/about")
def about():
    return render_template('about.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрировались!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    return render_template('login.html', form=form)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы!', 'success')
    return redirect(url_for('index'))
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)
@app.route("/tovar1.html", methods=['GET', 'POST'])
def tovar1():
    images = [
        'tovar1.1.png',
        'tovar1.2.png',
        'tovar1.3.png'
    ]
    comments = Comment.query.filter_by(product_id=1).order_by(Comment.created_at.desc()).all()  # Получаем комментарии для товара с ID=1
    ratings = Rating.query.filter_by(product_id=1).all()  # Получаем оценки для товара с ID=1

    # Вычисляем средний рейтинг
    if ratings:
        average_rating = sum(rating.value for rating in ratings) / len(ratings)
    else:
        average_rating = 0

    return render_template('tovar1.html', images=images, comments=comments, average_rating=average_rating)
@app.route("/tovar2.html", methods=['GET', 'POST'])
def tovar2():
    images = [
        'tovar2.1.png',
        'tovar2.2.png',
        'tovar2.3.png'
    ]
    comments = Comment.query.filter_by(product_id=2).order_by(Comment.created_at.desc()).all()  # Получаем комментарии для товара с ID=1
    ratings = Rating.query.filter_by(product_id=2).all()  # Получаем оценки для товара с ID=1

    # Вычисляем средний рейтинг
    if ratings:
        average_rating = sum(rating.value for rating in ratings) / len(ratings)
    else:
        average_rating = 0

    return render_template('tovar2.html', images=images, comments=comments, average_rating=average_rating)
@app.route("/tovar3.html", methods=['GET', 'POST'])
def tovar3():
    images = [
        'tovar3.1.png',
        'tovar3.2.png',
        'tovar3.3.png'
    ]
    comments = Comment.query.filter_by(product_id=3).order_by(Comment.created_at.desc()).all()  # Получаем комментарии для товара с ID=1
    ratings = Rating.query.filter_by(product_id=3).all()  # Получаем оценки для товара с ID=1

    # Вычисляем средний рейтинг
    if ratings:
        average_rating = sum(rating.value for rating in ratings) / len(ratings)
    else:
        average_rating = 0

    return render_template('tovar3.html', images=images, comments=comments, average_rating=average_rating)
@app.route('/add_comment', methods=['POST'])
@login_required
def add_comment():
    comment_text = request.form.get('comment')  # Получаем текст комментария из формы
    product_id = request.form.get('product_id')  # Получаем ID товара (можно передавать через скрытое поле)
    next_url = request.form.get('next')  # Получаем URL для перенаправления

    if not comment_text:
        flash('Комментарий не может быть пустым!', 'danger')
    else:
        # Создаем новый комментарий
        new_comment = Comment(
            text=comment_text,
            user_id=current_user.id,
            product_id=product_id
        )
        db.session.add(new_comment)
        db.session.commit()
        flash('Комментарий успешно добавлен!', 'success')
    return redirect(next_url)
@app.route('/add_rating', methods=['POST'])
@login_required
def add_rating():
    rating_value = request.form.get('rating')  # Получаем значение оценки из формы
    product_id = request.form.get('product_id')  # Получаем ID товара (можно передавать через скрытое поле)
    next_url = request.form.get('next')  # Получаем URL для перенаправления

    if not rating_value:
        flash('Оценка не может быть пустой!', 'danger')
    else:
        # Создаем новую оценку
        new_rating = Rating(
            value=int(rating_value),
            user_id=current_user.id,
            product_id=product_id
        )
        db.session.add(new_rating)
        db.session.commit()
        flash('Оценка успешно добавлена!', 'success')

    return redirect(next_url)  # Перенаправляем на страницу товара
@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    full_name = request.form.get('full_name')
    address = request.form.get('address')
    zip_code = request.form.get('zip_code')

    # Создаем новый заказ
    new_order = Order(
        full_name=full_name,
        address=address,
        zip_code=zip_code,
        user_id=current_user.id  # Связываем заказ с текущим пользователем
    )
    # Сохраняем заказ в базу данных
    db.session.add(new_order)
    db.session.commit()
    flash('Адрес доставки успешно сохранен!', 'success')
    return redirect(url_for('payment'))  # Перенаправляем на страницу оплаты
@app.route('/buy')
@login_required  # Требуется авторизация
def buy():
    return render_template('buy.html')
@app.route('/payment')
def payment():
    return render_template('payment.html')  # Убедитесь, что у вас есть шаблон payment.html
# Запуск приложения
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создаем таблицы в базе данных
    app.run(debug=True, port=5001)