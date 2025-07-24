from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import LoginForm, RegisterForm, TextForReadingForm, TrainingListForm, TrainingItemForm
from app.models import User, TextForReading, TrainingList, TrainingItem
from app import db


main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('main.home'))
        flash('Invalid credentials')
    return render_template('login.html', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registered successfully')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

# Create New Text
@main.route('/text/new', methods=['GET', 'POST'])
@login_required
def new_text():
    form = TextForReadingForm()
    if form.validate_on_submit():
        text = TextForReading(
            title=form.title.data,
            content=form.content.data,
            url=form.url.data,
            user_id=current_user.id
        )
        db.session.add(text)
        db.session.commit()
        flash("Text saved successfully.", "success")
        return redirect(url_for("main.dashboard"))  # Change to dashboard later
    return render_template("new_text.html", form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    texts = TextForReading.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", texts=texts)

@main.route('/text/<int:text_id>/lists', methods=['GET', 'POST'])
@login_required
def view_training_lists(text_id):
    text = TextForReading.query.get_or_404(text_id)
    if text.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for('main.dashboard'))

    form = TrainingListForm()
    if form.validate_on_submit():
        new_list = TrainingList(name=form.name.data, text_id=text.id)
        db.session.add(new_list)
        db.session.commit()
        flash("Training list created.", "success")
        return redirect(url_for('main.add_training_item', list_id=new_list.id))

    lists = text.training_lists
    return render_template("training_lists.html", text=text, lists=lists, form=form)

@main.route('/list/<int:list_id>/add-item', methods=['GET', 'POST'])
@login_required
def add_training_item(list_id):
    training_list = TrainingList.query.get_or_404(list_id)

    # Security check: only allow if user owns the list
    if training_list.text.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for('main.dashboard'))

    form = TrainingItemForm()
    if form.validate_on_submit():
        item = TrainingItem(
            phrase=form.phrase.data,
            translation=form.translation.data,
            context=form.context.data,
            training_list_id=training_list.id
        )
        db.session.add(item)
        db.session.commit()
        flash("Training item added!", "success")
        return redirect(url_for('main.add_training_item', list_id=list_id))

    return render_template("add_training_item.html", form=form, training_list=training_list)

@main.route('/list/<int:list_id>/edit')
@login_required
def edit_training_list(list_id):
    training_list = TrainingList.query.get_or_404(list_id)

    # проверка дали списъкът принадлежи на текущия потребител
    if training_list.text.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for('main.dashboard'))

    # вземаме всички фрази за този списък
    items = training_list.training_items

    return render_template("edit_training_list.html", training_list=training_list, items=items)
