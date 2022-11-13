from sqlalchemy.orm import sessionmaker
from databases.define_tables import City, Users, Books, Movies, Music, Pictures


def select_db_query(engine, user_query_id):
    '''
    Функция принимает на вход движок engine и ИД пользователя в БД.

    Функция подключается к БД с движком engine и выполняет следующие действия:
    извлекает базовые сведения о пользователе из таблицы Users (имя, фамилия, возраст, ссылка на страницу в ВК, рейтинг совпадения пользователя),
    извлекает ссылки на фотографии пользователей из таблицы Pictures (не более 3),
    извлекает город пользователя из таблицы City,
    извлекает сведения о предпочтениях пользователя: книги (таблица Books), фильмы (таблица Movies), музыка (таблица Music),
    закрывает сессию.
    '''
    Session = sessionmaker(bind=engine)
    session = Session()

# basic details, blacklist
    basic_info = session.query(Users).filter(Users.user_id == user_query_id)
    selected_user_data = f"First name: {basic_info[0].first_name}, Last name: {basic_info[0].last_name}, Age: {basic_info[0].age}, User link: {basic_info[0].user_link}\n\nUser's match ranking based on his/her interests: {basic_info[0].match_rank}"
    blacklist_flag = {basic_info[0].black_listed}

# pictures
    pics = session.query(Pictures).filter(Pictures.user_id == user_query_id)
    selected_user_pictures = []
    try:
        for n in range(3):
            selected_user_pictures.append(pics[n].pic_link)
    except IndexError:
        print("User added too few photos")

# city
    subq = session.query(Users).filter(Users.user_id == user_query_id).subquery()
    user_city = session.query(City).join(subq, City.city_id == subq.c.city)
    selected_user_city = f'User city: {user_city[0].city_name}'

# books
    subq = session.query(Users).filter(Users.user_id == user_query_id).subquery()
    user_books = session.query(Books).join(subq, Books.books_user == subq.c.user_id)
    try:
        selected_user_books = f'User likes books: {user_books[0].books_favourites}'
    except IndexError:
        selected_user_books = 'User has no info on books'

# movies
    subq = session.query(Users).filter(Users.user_id == user_query_id).subquery()
    user_movies = session.query(Movies).join(subq, Movies.movies_user == subq.c.user_id)
    try:
        selected_user_movies = f'User likes movies: {user_movies[0].movies_favourites}'
    except IndexError:
        selected_user_movies = 'User has no info on movies'

# music
    subq = session.query(Users).filter(Users.user_id == user_query_id).subquery()
    user_music = session.query(Music).join(subq, Music.music_user == subq.c.user_id)
    try:
        selected_user_music = f'User likes music: {user_music[0].music_favourites}'
    except IndexError:
        selected_user_music = 'User has no info on music'

    session.close()
    return selected_user_data, selected_user_pictures, selected_user_city, selected_user_books, selected_user_movies, selected_user_music, blacklist_flag
