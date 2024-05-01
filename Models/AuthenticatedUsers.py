from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy import String, Column, DateTime, Integer

from Tools.Database.Conn import Base


class AuthenticatedUsersModel(Base):

    __tablename__ = 'authenticated_users'

    authenticated_user_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    code = Column(String(50))
    is_authenticated = Column(Integer)
    active = Column(Integer, server_default=str(1))
    created_at = Column(DateTime, default=current_timestamp())
    updated_at = Column(
        DateTime, default=current_timestamp(), onupdate=current_timestamp()
    )

    def __init__(self, **kwargs):

        self.authenticated_user_id = kwargs['authenticated_user_id']
        self.user_id = kwargs['user_id']
        self.code = kwargs['code']
        self.is_authenticated = kwargs['is_authenticated']
        self.active = kwargs['active']
