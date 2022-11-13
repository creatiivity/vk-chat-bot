import sqlalchemy
from databases.define_tables import create_tables
from databases.add_all_data import add_to_db
from databases.add_pics import add_pics_to_db
from vk_data.vk_users_search import VK_User
from vk_data.vk_bot import send_matches
from credentials import TOKEN, TOKEN_GROUP, user_id, app_id, db_password


if __name__ == '__main__':
# connect to DB
    DSN = f'postgresql://postgres:{db_password}@localhost:5432/tinder'
    engine = sqlalchemy.create_engine(DSN)

# create tables
    create_tables(engine, cascade="all, delete-orphan")

# get current user's profile info
    current_user = VK_User(TOKEN, user_id, app_id)
    vk, current_user_id, home_town, gender, birth_date, response, user_info, self_age, link = current_user.get_profile_info()
    user_data_db = [{'vk_user_id': current_user_id, 'first_name': user_info[0]['first_name'],
                     'last_name': user_info[0]['last_name'], 'age': self_age, 'gender': gender, 'city': home_town, 'user_link': link, 'match_rank': '0', 'music': user_info[0]['music'], 'movies': user_info[0]['movies'], 'books': user_info[0]['books']}]

# get photo links of matches
    sorted_dict_of_photos = current_user.get_best_photos()

# get detailed info on matches
    matching_list = current_user.get_info_by_user_id()
    user_data_db.extend(matching_list)

# add all data and pics to bd
    add_to_db(engine, user_data_db)
    add_pics_to_db(engine, sorted_dict_of_photos)

# send matches to chat
    send_matches(engine, TOKEN_GROUP)
