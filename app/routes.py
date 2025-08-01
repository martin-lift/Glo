from flask import (Blueprint, render_template, redirect)
from flask import jsonify, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from sqlalchemy.orm import aliased
from app.forms import (LoginForm, RegisterForm, TextForReadingForm, TrainingListForm)
from app.forms import (TrainingItemForm, TrainingItemWithListForm)
from app.forms import PHRASE_MAX_LEN
from app.models import User, TextForReading, TrainingList, TrainingItem
from app.models import TrainingLang
from app import db
from config import DEFAULT_LANG_FROM, DEFAULT_LANG_TO

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

    form = TrainingListForm(
        lang_from=DEFAULT_LANG_FROM,
        lang_to=DEFAULT_LANG_TO
    )
    form.submit.label.text = "Create List"

    # lang dropdowns loading
    langs = TrainingLang.query.order_by(TrainingLang.lang_name).all()
    choices = [(lang.lang_code, f"{lang.lang_name} ({lang.native_name})") for lang in langs]
    form.lang_from.choices = choices
    form.lang_to.choices = choices

    if form.validate_on_submit():
        new_list = TrainingList(
            name=form.name.data,
            text_id=text.id,
            lang_from=form.lang_from.data,
            lang_to=form.lang_to.data
        )
        db.session.add(new_list)
        db.session.commit()
        flash("Training list created.", "success")
        return redirect(url_for('main.add_training_item', list_id=new_list.id))

    # Зареждане на списъците с брой елементи и last_used_at
    ti = aliased(TrainingItem)
    query = (
        db.session.query(
            TrainingList,
            func.max(
                func.ifnull(ti.last_trained_at, func.ifnull(ti.created_at, TrainingList.created_at))
            ).label("last_used_at"),
            func.count(ti.id).label("item_count")
        )
        .outerjoin(ti, ti.training_list_id == TrainingList.id)
        .filter(TrainingList.text_id == text.id)
        .group_by(TrainingList.id)
        .order_by(func.max(
            func.ifnull(ti.last_trained_at, func.ifnull(ti.created_at, TrainingList.created_at))
        ).desc())
    )

    results = query.all()
    lists = []
    for lst, last_used_at, item_count in results:
        lst.last_used_at = last_used_at
        lst.item_count = item_count
        lists.append(lst)

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

@main.route("/list/<int:list_id>/edit", methods=["GET", "POST"])
@login_required
def edit_training_list(list_id):
    training_list = TrainingList.query.get_or_404(list_id)

    if training_list.text.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for('main.dashboard'))

    form = TrainingListForm(obj=training_list)

    # lang dropdowns loading
    langs = TrainingLang.query.order_by(TrainingLang.lang_name).all()
    choices = [(lang.lang_code, f"{lang.lang_name} ({lang.native_name})") for lang in langs]
    form.lang_from.choices = choices
    form.lang_to.choices = choices

    # all phrases for the list
    items = training_list.training_items

    if form.validate_on_submit():
        training_list.name = form.name.data
        training_list.lang_from = form.lang_from.data
        training_list.lang_to = form.lang_to.data
        db.session.commit()
        flash("Training list updated.", "success")
      # return redirect(url_for("main.view_training_lists"))
        return render_template("edit_training_list.html", form=form, training_list=training_list, items=items)

    return render_template("edit_training_list.html", form=form, training_list=training_list, items=items)

@main.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_training_item(item_id):
    item = TrainingItem.query.get_or_404(item_id)
    if item.list.text.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for('main.dashboard'))

    form = TrainingItemForm(obj=item)

    if form.validate_on_submit():
        item.phrase = form.phrase.data
        item.translation = form.translation.data
        item.context = form.context.data
        db.session.commit()
        flash("Item updated.", "success")
        return redirect(url_for('main.edit_training_list', list_id=item.training_list_id))

    return render_template("edit_training_item.html", form=form, item=item)

@main.route('/item/<int:item_id>/delete')
@login_required
def delete_training_item(item_id):
    item = TrainingItem.query.get_or_404(item_id)
    if item.list.text.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for('main.dashboard'))

    db.session.delete(item)
    db.session.commit()
    flash("Item deleted.", "info")
    return redirect(url_for('main.edit_training_list', list_id=item.training_list_id))

@main.route('/list/<int:list_id>/train')
@login_required
def train_list(list_id):
    training_list = TrainingList.query.get_or_404(list_id)

    if training_list.text.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for('main.dashboard'))

    # Get only item with training_order = 1
    item = TrainingItem.query.filter_by(training_list_id=list_id, training_order=1).first()

    return render_template("train_session.html", training_list=training_list, item=item)

@main.route('/text/<int:text_id>/read', methods=['GET', 'POST'])
@login_required
def read_text(text_id):
    text = TextForReading.query.get_or_404(text_id)
    if text.user_id != current_user.id:
        return redirect(url_for('main.dashboard'))

    form = TrainingItemWithListForm()

    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        form = TrainingItemWithListForm(data=data)

        if form.validate():
            list_name = form.list_name.data.strip()

            training_list = TrainingList.query.filter_by(name=list_name, text_id=text.id).first()
            if not training_list:
                training_list = TrainingList(
                    name=list_name,
                    text_id=text.id,
                    lang_from=DEFAULT_LANG_FROM,
                    lang_to=DEFAULT_LANG_TO
                )
                db.session.add(training_list)
                db.session.commit()

            item = TrainingItem(
                phrase=form.phrase.data,
                translation=form.translation.data,
                context=form.context.data,
                training_list_id=training_list.id
            )
            db.session.add(item)
            db.session.commit()

            return jsonify({
                "status": "success",
                "message": "Phrase added!",
                "list_name": training_list.name
            })

        return jsonify({
            "status": "error",
            "message": "Validation failed"
        }), 400

    # GET
    # fill in with the new element
    latest_item = (
        TrainingItem.query
        .join(TrainingList)
        .filter(TrainingList.text_id == text.id)
        .order_by(TrainingItem.created_at.desc())
        .first()
    )
    if latest_item:
        form.list_name.data = latest_item.list.name
    else:
        form.list_name.data = "Main Training List"

    return render_template("read_text.html", text=text, form=form, phrase_max_len=PHRASE_MAX_LEN)

@main.route('/get_langs')
def get_langs():
    list_name = request.args.get('list_name', '')
    text_id = request.args.get('text_id', 0)

    # db search
    training_list = TrainingList.query.filter_by(name=list_name, text_id=text_id).first()

    if training_list:
        lang_from = training_list.lang_from
        lang_to = training_list.lang_to
    else:
        lang_from = DEFAULT_LANG_FROM
        lang_to = DEFAULT_LANG_TO

    return jsonify({'lang_from': lang_from, 'lang_to': lang_to})

@main.route('/training-list/<int:list_id>/delete', methods=['POST'])
@login_required
def delete_training_list(list_id):
    lst = TrainingList.query.get_or_404(list_id)

    if lst.text.user_id != current_user.id:
        flash("Unauthorized access", "danger")
        return redirect(url_for('main.dashboard'))

    db.session.delete(lst)
    db.session.commit()
    flash("Training list deleted.", "success")

    return redirect(url_for('main.view_training_lists', text_id=lst.text_id))

