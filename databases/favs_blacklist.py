from sqlalchemy.orm import sessionmaker
from databases.define_tables import Users


def add_to_blacklist(engine, user_query_id):
    '''
    Функция принимает на вход движок engine и ИД пользователя в БД.

    Функция подключается к БД с движком engine и выполняет следующие действия:
    находит пользователя в таблице Users по его/ее ИД в БД,
    изменяет флаг "Черный спискок" для этого пользователя с 0 на 1 (или наоборот),
    закрывает сессию.
    '''
    Session = sessionmaker(bind=engine)
    session = Session()

    req_user = session.query(Users).filter(Users.user_id == user_query_id)
    old_bl_value = req_user[0].black_listed
    if old_bl_value == 0:
        new_bl_value = 1
    else:
        new_bl_value = 0
    session.query(Users).filter(Users.user_id == user_query_id).update({'black_listed': new_bl_value})
    session.commit()
    session.close()
    return new_bl_value


def add_to_favs(engine, user_query_id):
    '''
    Функция принимает на вход движок engine и ИД пользователя в БД.

    Функция подключается к БД с движком engine и выполняет следующие действия:
    находит пользователя в таблице Users по его/ее ИД в БД,
    изменяет флаг "Избранное" для этого пользователя с 0 на 1 (или наоборот),
    закрывает сессию.
    '''
    Session = sessionmaker(bind=engine)
    session = Session()

    req_user = session.query(Users).filter(Users.user_id == user_query_id)
    old_fav_value = req_user[0].favourites
    if old_fav_value == 0:
        new_fav_value = 1
    else:
        new_fav_value = 0
    session.query(Users).filter(Users.user_id == user_query_id).update({'favourites': new_fav_value})
    session.commit()
    session.close()
    return new_fav_value


def show_all_favs(engine):
    '''
    Функция принимает на вход движок engine.

    Функция подключается к БД с движком engine и выполняет следующие действия:
    находит всех пользователей в таблице Users, для которых установлен флаг "Избранное", равный 1,
    возвращает список этих пользователей с информацией о них (имя, фамилия, возраст, ссылка на страницу в ВК, рейтинг совпадения),
    закрывает сессию.
    '''
    Session = sessionmaker(bind=engine)
    session = Session()

    fav_user_list = []
    i = 0
    for c in session.query(Users).filter(Users.favourites == 1).all():
        i += 1
        fav_user = f"{i}.\nFirst name: {c.first_name}, last name: {c.last_name}, age: {c.age}, user link: {c.user_link}\nUser's match ranking based on his/her interests: {c.match_rank}\n\n\n\n\n\n"
        fav_user_list.append(fav_user)
    session.close()
    return fav_user_list
