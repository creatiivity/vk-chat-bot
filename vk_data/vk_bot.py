import requests
import re
import vk_api
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api import VkUpload
from vk_api.keyboard import VkKeyboard
from databases.select_from_db import select_db_query
from databases.favs_blacklist import add_to_blacklist, add_to_favs, show_all_favs


def process_user_data(engine, user_query_id, upload):
    '''
    Аргументы:
        engine: движок для подключения к БД
        user_query_id: ИД пользователя в БД
        upload: параметр сессии VK api

    Возвращает:
        полные сведения о пользователе, список фотографий attachments (в случае возникновения сбоя при поиске фотографий в консоли выйдет предупреждение), флаг "черный список".
    '''
    selected_user_data, selected_user_pictures, selected_user_city, selected_user_books, selected_user_movies, selected_user_music, blacklist_flag = select_db_query(engine, user_query_id)
    user_message = f'{selected_user_data}\n\n{selected_user_city}\n\n{selected_user_books}\n\n{selected_user_movies}\n\n{selected_user_music}'

    attachments = []
    try:
        for pic in selected_user_pictures:
            image = requests.Session().get(pic, stream=True)
            photo = upload.photo_messages(photos=image.raw)[0]
            pic_link = f"photo{photo['owner_id']}_{photo['id']}"
            attachments.append(pic_link)
    except vk_api.exceptions.ApiError:
        print("Invalid link")
        attachments = []
    return user_message, attachments, blacklist_flag


def send_matches(engine, TOKEN_GROUP):
    '''
    Аргументы:
        engine: движок для подключения к БД
        TOKEN_GROUP: токен для сообщества в ВК

    Функция создает сессию в чате ВК, при получении сообщения "go" выводит на экран 5 кнопок и первого совпадающего пользователя (ИД 2). Далее пользователь может использовать кнопки для перехода между пользователями, добавления в "черный список"/"избранное" (или удаления из него), отображения списка "избранного".
    '''
    user_query_id = 2
    vk_session = vk_api.VkApi(token=TOKEN_GROUP)
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()
    upload = VkUpload(vk_session)

# get group ID
    group_info = vk.groups.getById(token=TOKEN_GROUP)
    current_group_id = group_info[0]['screen_name']

# create buttons
    my_keyboard = vk_api.keyboard.VkKeyboard(one_time=False)
    my_keyboard.add_button(label="Previous", color='primary')
    my_keyboard.add_button(label="Next", color='primary')
    my_keyboard.add_line()
    my_keyboard.add_button(label="Add to favs", color='positive')
    my_keyboard.add_button(label="Show favs", color='primary')
    my_keyboard.add_button(label="Add to blacklist", color='negative')

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            text = event.text.lower()

            if text == "go":
                user_message, attachments, blacklist_flag = process_user_data(engine, user_query_id, upload)
                if blacklist_flag == {0}:
                    vk.messages.send(chat_id=event.chat_id, random_id=get_random_id(), attachment=','.join(attachments), message=user_message, keyboard=my_keyboard.get_keyboard())
                else:
                    vk.messages.send(chat_id=event.chat_id, random_id=get_random_id(), message="This user has been blacklisted by you. Go to previous or next user.")

            if 'next' in text:
                try:
                    user_query_id += 1
                    user_message, attachments, blacklist_flag = process_user_data(engine, user_query_id, upload)
                    if blacklist_flag == {0}:
                        vk.messages.send(chat_id=event.chat_id, random_id=get_random_id(), attachment=','.join(attachments), message=user_message, keyboard=my_keyboard.get_keyboard())
                    else:
                        vk.messages.send(chat_id=event.chat_id, random_id=get_random_id(), message="This user has been blacklisted by you. Go to previous or next user.")
                except IndexError:
                    vk.messages.send(chat_id=event.chat_id, random_id=get_random_id(), message="No more selected users")
                    user_query_id -= 1

            if 'previous' in text:
                user_query_id -= 1
                if user_query_id > 1:
                    user_message, attachments, blacklist_flag = process_user_data(engine, user_query_id, upload)
                    if blacklist_flag == {0}:
                        vk.messages.send(chat_id=event.chat_id, random_id=get_random_id(), attachment=','.join(attachments), message=user_message, keyboard=my_keyboard.get_keyboard())
                    else:
                        vk.messages.send(chat_id=event.chat_id, random_id=get_random_id(), message="This user has been blacklisted by you")
                else:
                    vk.messages.send(chat_id=event.chat_id, random_id=get_random_id(), message="This was the first user. Click 'Next' to see other matches")
                    user_query_id = 2

            if 'add to favs' in text:
                new_fav_value = add_to_favs(engine, user_query_id)
                if new_fav_value == 0:
                    vk.messages.send(chat_id=event.chat_id, random_id=get_random_id(),
                                     message="The user was removed from favourites.")
                else:
                    vk.messages.send(chat_id=event.chat_id, random_id=get_random_id(),
                                     message="The user was added to favourites.")

            if 'add to blacklist' in text:
                new_bl_value = add_to_blacklist(engine, user_query_id)
                if new_bl_value == 0:
                    vk.messages.send(chat_id=event.chat_id, random_id=get_random_id(),
                                     message="The user was removed from blacklist.")
                else:
                    vk.messages.send(chat_id=event.chat_id, random_id=get_random_id(),
                                     message="The user was added to blacklist.")

            if 'show favs' in text:
                fav_user_list = show_all_favs(engine)
                if fav_user_list:
                    vk.messages.send(chat_id=event.chat_id, random_id=get_random_id(),
                                     message=fav_user_list)
                else:
                    vk.messages.send(chat_id=event.chat_id, random_id=get_random_id(),
                                     message="You haven't added users to Favourites.")

    return
