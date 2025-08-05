from app.models import TrainingItem
from app import db
from sqlalchemy import func

class ItemOrderer:
    def __init__(self, list_id):
        self.list_id = list_id

    def order_normalize(self):
        items = (
            TrainingItem.query
            .filter_by(training_list_id=self.list_id)
            .order_by(TrainingItem.training_order.asc(),TrainingItem.created_at.asc())
            .all()
        )
        self._apply_order(items)

    def order_randomize(self):
        items = (
            TrainingItem.query
            .filter_by(training_list_id=self.list_id)
            .order_by(func.rand())
            .all()
        )
        self._apply_order(items)

    def _apply_order(self, items):
        for i, item in enumerate(items, start=1):
            item.training_order = i
        db.session.commit()

    def move_to_position(self, item_id, position):
        # self.order_normalize()
        items = (
            TrainingItem.query
            .filter_by(training_list_id=self.list_id)
            .order_by(TrainingItem.training_order.asc(),TrainingItem.created_at.asc())
            .all()
        )

        # find the element
        item_to_move = next((item for item in items if item.id == item_id), None)
        if item_to_move is None:
            raise ValueError(f"TrainingItem ID {item_id} not found in list.")

        # move to position
        items.remove(item_to_move)
        insert_position = max(0, min(position - 1, len(items)))  # limits correction
        items.insert(insert_position, item_to_move)

        self._apply_order(items)

    @staticmethod
    def get_max_order(training_list_id):
        max_order = db.session.query(
            func.max(TrainingItem.training_order)
        ).filter_by(training_list_id=training_list_id).scalar()

        return max_order or 0

