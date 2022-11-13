import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import CheckConstraint

Base = declarative_base()


class Gender(Base):
    '''
    Класс "Пол пользователя"

    Столбцы: первичный ключ,
            значение пола
    '''
    __tablename__ = 'gender'

    gender_id = sq.Column(sq.Integer, nullable=False, primary_key=True)
    gender_name = sq.Column(sq.String(length=10), CheckConstraint("gender_name IN ('Male', 'Female')"), nullable=False)


class City(Base):
    '''
    Класс "Город"

    Столбцы: первичный ключ,
            название города
    '''
    __tablename__ = 'city'

    city_id = sq.Column(sq.Integer, nullable=False, primary_key=True)
    city_name = sq.Column(sq.String(length=80))


class Users(Base):
    '''
    Класс "Пользователь"

    Столбцы: первичный ключ,
            ИД пользователя в ВК,
            имя, фамилия, возраст,
            пол (внешний ключ ссылается на таблицу "Пол"),
            ссылка на страницу пользователя,
            город (внешний ключ ссылается на таблицу "Город"),
            рейтинг совпадений пользователя по интересам,
            флаги "Избранное" и "Черный список"
    '''
    __tablename__ = 'users'

    user_id = sq.Column(sq.Integer, nullable=False, primary_key=True)
    vk_user_id = sq.Column(sq.Integer, nullable=False)
    first_name = sq.Column(sq.String(length=80))
    last_name = sq.Column(sq.String(length=80))
    age = sq.Column(sq.Integer, CheckConstraint('age>=0'))
    gender = sq.Column(sq.Integer, sq.ForeignKey(Gender.gender_id))
    user_link = sq.Column(sq.String(length=512), unique=True)
    city = sq.Column(sq.Integer, sq.ForeignKey(City.city_id))
    match_rank = sq.Column(sq.Integer, default=0)
    favourites = sq. Column(sq.Integer, CheckConstraint("favourites IN (1, 0)"), default=0)
    black_listed = sq. Column(sq.Integer, CheckConstraint("black_listed IN (1, 0)"), default=0)

    Gender = relationship(Gender, backref='users')
    City = relationship(City, backref='users')


class Pictures(Base):
    '''
    Класс "Фотографии"

    Столбцы: первичный ключ,
            ИД пользователя в БД (внешний ключ ссылается на ИД пользователя в таблице "Пользователи"),
            количество "лайков",
            ссылка на фотографию,
            ИД пользователя в ВК
    '''
    __tablename__ = 'pictures'

    pic_id = sq.Column(sq.Integer, nullable=False, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey(Users.user_id), nullable=False)
    likes = sq.Column(sq.Integer, CheckConstraint('likes >= 0'), default=0)
    pic_link = sq.Column(sq.String(length=512), nullable=False)
    vk_user_id = sq.Column(sq.Integer, nullable=False)

    Users = relationship(Users, backref='pictures')


class Books(Base):
    '''
    Класс "Книги"

    Столбцы: первичный ключ,
            ИД пользователя в БД (внешний ключ ссылается на ИД пользователя в таблице "Пользователи"),
            Список предпочтений пользователя
    '''
    __tablename__ = 'books'

    books_cat_id = sq.Column(sq.Integer, nullable=False, primary_key=True)
    books_user = sq.Column(sq.Integer, sq.ForeignKey(Users.user_id), nullable=False)
    books_favourites = sq.Column(sq.String(length=820), nullable=False)

    Users = relationship(Users, backref='books')


class Movies(Base):
    '''
    Класс "Фильмы"

    Столбцы: первичный ключ,
            ИД пользователя в БД (внешний ключ ссылается на ИД пользователя в таблице "Пользователи"),
            Список предпочтений пользователя
    '''
    __tablename__ = 'movies'

    movies_cat_id = sq.Column(sq.Integer, nullable=False, primary_key=True)
    movies_user = sq.Column(sq.Integer, sq.ForeignKey(Users.user_id), nullable=False)
    movies_favourites = sq.Column(sq.String(length=820), nullable=False)

    Users = relationship(Users, backref='movies')


class Music(Base):
    '''
    Класс "Музыка"

    Столбцы: первичный ключ,
            ИД пользователя в БД (внешний ключ ссылается на ИД пользователя в таблице "Пользователи"),
            Список предпочтений пользователя
    '''
    __tablename__ = 'music'

    music_cat_id = sq.Column(sq.Integer, nullable=False, primary_key=True)
    music_user = sq.Column(sq.Integer, sq.ForeignKey(Users.user_id), nullable=False)
    music_favourites = sq.Column(sq.String(length=820), nullable=False)

    Users = relationship(Users, backref='music')


def create_tables(engine, cascade="all, delete-orphan"):
    '''
    Функция принимает на вход движок engine и флаг "каскадное удаление" (срабатывает не всегда).

    Функция подключается к БД с движком engine и выполняет следующие действия:
    удаляет все заданные в родительском классе Base таблицы,
    создает структуру таблиц на основе родительского класса Base (см. выше)
    '''
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
