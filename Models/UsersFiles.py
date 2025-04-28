from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy import String, Column, DateTime, Integer

from Tools.Database.Conn import Base


class UsersFilesModel(Base):

    __tablename__ = 'users_files'

    user_file_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    url = Column(String(500))
    active = Column(Integer, server_default=str(1))
    created_at = Column(DateTime, default=current_timestamp())
    updated_at = Column(
        DateTime, default=current_timestamp(), onupdate=current_timestamp()
    )

    def __init__(self, **kwargs):

        self.user_file_id = kwargs['user_file_id']
        self.user_id = kwargs['user_id']
        self.url = kwargs['url']
        self.active = kwargs['active']
