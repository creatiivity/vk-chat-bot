from sqlalchemy.orm import sessionmaker
from databases.define_tables import Users, Pictures


def add_pics_to_db(engine, sorted_dict_of_photos):
    '''
    Функция принимает на вход движок engine и список фотографий пользователей.

    Функция подключается к БД с движком engine и выполняет следующие действия:
    находит ИД пользователя в БД по его/ее ИД в соц.сети ВК,
    заполняет таблицу Pictures (поля: ИД пользователя в БД, ссылка на фотографию, количество "лайков", ИД пользователя в ВК),
    закрывает сессию.
    '''
    Session = sessionmaker(bind=engine)
    session = Session()

    for key, value in sorted_dict_of_photos.items():
        user_id_vk = session.query(Users).filter(Users.vk_user_id == key)
        user_vk = user_id_vk[0].user_id
        try:
            for n in range(3):
                session.add(Pictures(user_id=user_vk, likes=value[n]['likes'], pic_link=value[n]['link'], vk_user_id=key))
        except IndexError:
            print('Too few photos')

    session.commit()
    session.close()
    return
