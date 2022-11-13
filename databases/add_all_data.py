from sqlalchemy.orm import sessionmaker
from databases.define_tables import Gender, City, Users, Books, Movies, Music


# add all data to db
def add_to_db(engine, user_data_db):
    '''
    Функция принимает на вход движок engine и список словарей user_data_db, который содержит все сведения о пользователях, которые будут добавлены в БД.

    Функция подключается к БД с движком engine и выполняет следующие действия:
    записывает значения Male и Female в таблицу Gender,
    проверяет, существует ли город пользователя в таблице City
    (если город не существует, он будет добавлен),
    заполняет все поля таблицы Users значениями из списка словарей user_data_db,
    заполняет таблицы Books, Movies, Music данными из списка словарей user_data_db (если эти данные содержатся в этом списке),
    закрывает сессию.
    '''
    Session = sessionmaker(bind=engine)
    session = Session()

    female_gender = Gender(gender_name='Female')
    male_gender = Gender(gender_name='Male')
    session.add_all([female_gender, male_gender])
    session.commit()

    all_cities_list = []
    for n in range(len(user_data_db)):
        if user_data_db[n]['city'] != None and user_data_db[n]['city'] not in all_cities_list:
            session.add(City(city_name=user_data_db[n]['city']))
            all_cities_list.append(user_data_db[n]['city'])
            session.commit()
        if user_data_db[n]['city']:
            user_town = session.query(City).filter(City.city_name == user_data_db[n]['city'])
            user_town_id = user_town[0].city_id
        else:
            user_town_id = None
        session.add(Users(vk_user_id=user_data_db[n]['vk_user_id'], first_name=user_data_db[n]['first_name'], last_name=user_data_db[n]['last_name'], age=user_data_db[n]['age'], gender=user_data_db[n]['gender'], city=user_town_id, user_link=user_data_db[n]['user_link'], match_rank=user_data_db[n]['match_rank']))
    session.commit()

    for n in range(len(user_data_db)):
        user_id_vk = session.query(Users).filter(Users.vk_user_id == user_data_db[n]['vk_user_id'])
        user_vk = user_id_vk[0].user_id
        try:
            if user_data_db[n]['books']:
                session.add(Books(books_user=user_vk, books_favourites=user_data_db[n]['books']))
        except KeyError:
            print('No data')
        try:
            if user_data_db[n]['movies']:
                session.add(Movies(movies_user=user_vk, movies_favourites=user_data_db[n]['movies']))
        except KeyError:
            print('No data')
        try:
            if user_data_db[n]['music']:
                session.add(Music(music_user=user_vk, music_favourites=user_data_db[n]['music']))
        except KeyError:
            print('No data')
    session.commit()
    session.close()

    return
