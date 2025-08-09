from flask import (Blueprint, render_template, redirect)
from flask import jsonify, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func
from sqlalchemy.orm import aliased
from app.forms import (LoginForm, RegisterForm, TextForReadingForm, TrainingListForm)
from app.forms import (TrainingItemForm, TrainingItemWithListForm)
from app.forms import PHRASE_MAX_LEN
from app.models import User, TextForReading, TrainingList, TrainingItem
from app.utils.item_orderer import ItemOrderer
from app.utils import diff_phrase
from app import db

train_bp = Blueprint('train', __name__)

@train_bp.route('/list/<int:list_id>/train', methods=['GET', 'POST'])
@login_required
def train_list(list_id):
	training_list = TrainingList.query.get_or_404(list_id)

	if training_list.text.user_id != current_user.id:
		flash("Unauthorized access", "danger")
		return redirect(url_for('main.dashboard'))

	# Get the current item ID from the form (if present)
	current_item_id = request.form.get('current_item_id')
	if current_item_id is not None:
		current_item_id = int(current_item_id)

	stage_index = request.form.get('stage_index')
	if stage_index is None:
		stage_index = 0
	else:
		stage_index = int(stage_index)

	stages = request.form.get('stages')
	if stages is None:
		stages = ""

	# If user clicked the "Next Item" button
	if request.form.get('action') == 'next':
		# fetch the next item in the sequence
		if stage_index > 3 or "show" in stages:
			position = 3
		elif stage_index == 3:
			position = 9
		elif stage_index == 2:
			position = 10
		else:
			position = 3000000   # end of list

		orderer = ItemOrderer(list_id)
		orderer.move_to_position(current_item_id, position)

		#ItemOrderer.move_to_position(training_list,current_item_id, position)
		item = orderer.get_first()
		stage_index = 0
		stages = ""

		return render_template(
			"train_session.html",
			training_list=training_list,
			item=item,
			result=None,
			correct=False,
			user_input=None,
			stage_index = stage_index,
			stages = stages
		)

	# If this is a POST request with a phrase submission
	if request.method == 'POST' and current_item_id:
		item = TrainingItem.query.get_or_404(current_item_id)
		user_input = request.form.get('user_phrase', '').strip()

		ph_user_norm = diff_phrase.normalize(user_input)
		ph_db_norm = diff_phrase.normalize(item.phrase)

		# diff
		correct = ph_user_norm.lower() == ph_db_norm.lower()
		if correct:
			result = item.phrase #  + "<br><br>Correct!"
		else:
			if request.form.get('action') == 'show':
				result = item.phrase
				stages += "show "
			else:
				result = diff_phrase.mask_diff(
					ph_db_norm.lower(),
					ph_user_norm.lower()
				)
				#result = "Try again!"
	else:
		# Initial page load — get the first item (random or first in order)
		item = (
			TrainingItem.query.filter_by(training_list_id=list_id)
			.order_by(TrainingItem.training_order.asc(), func.rand())
			.first()
		)
		user_input = None
		result = None
		correct = False
		stage_index = 0

	return render_template(
		"train_session.html",
		training_list=training_list,
		item=item,
		result=result,
		correct=correct,
		user_input=user_input,
		stage_index=stage_index,
		stages=stages
	)


