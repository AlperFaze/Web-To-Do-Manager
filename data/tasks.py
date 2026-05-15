import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Tasks(SqlAlchemyBase):
    def __repr__(self):
        return f"<Tasks> {self.id} {self.title} {self.content}"

    __tablename__ = 'tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')

    deadline = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)

    is_completed = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    completed_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)

    categories = orm.relationship("Category",
                                  secondary="association",
                                  backref="tasks")

    def get_date(self, date_field, fmt="%d.%m.%Y %H:%M"):
        date = getattr(self, date_field)
        return date.strftime(fmt)