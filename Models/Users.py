from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy import String, Column, DateTime, Integer

from Tools.Database.Conn import Base


class UserModel(Base):

    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    username = Column(String(100), nullable=False)
    password = Column(String(250), nullable=False)
    first_lastname = Column(String(100))
    second_lastname = Column(String(100))
    phone_number = Column(String(50))
    email = Column(String(250), nullable=False)
    type_document_id = Column(Integer)
    document = Column(String(100))
    city_id = Column(Integer)
    active = Column(Integer, server_default=str(1))
    created_at = Column(DateTime, default=current_timestamp())
    updated_at = Column(
        DateTime, default=current_timestamp(), onupdate=current_timestamp()
    )

    def __init__(self, **kwargs):

        self.user_id = kwargs['user_id']
        self.name = kwargs['name']
        self.username = kwargs['username']
        self.password = kwargs['password']
        self.first_lasname = kwargs['first_lasname']
        self.second_lasname = kwargs['second_lasname']
        self.phone_number = kwargs['phone_number']
        self.email = kwargs['email']
        self.type_document_id = kwargs['type_document_id']
        self.document = kwargs['document']
        self.city_id = kwargs['city_id']
        self.active = kwargs['active']
