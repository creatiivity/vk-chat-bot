import random
import vk_api

URL = 'https://vk.com/id'


class VK_User:
    '''
    Класс для работы с пользователем VK
    '''
    def __init__(self, token, user_id, app_id):
        '''
        Аргументы:
            token: - токен текущего пользователя в ВК
            user_id - ИД текущего пользователя в ВК
            app_id - ИД приложения в ВК
        '''
        self.user_id = user_id
        self.app_id = app_id
        self.token = token

# get current user info
    def get_profile_info(self):
        '''
        Подключение к VK api с помощью токена и ИД,
        возвращение полной информации о текущем пользователе
        '''
        vk_session = vk_api.VkApi(app_id=self.app_id, token=self.token)
        self.vk = vk_session.get_api()
        response = self.vk.account.getProfileInfo()
        user_info = self.vk.users.get(fields='books, movies, music')
        year_of_birth = int(response['bdate'].split('.')[-1])  # get year of birth
        self.self_age = 2022 - year_of_birth  # get age
        self.hometown = str(response['home_town'])
        self.gender = str(response['sex'])
        self.birth_date = str(response['bdate'])
        self.link = f'{URL}{self.user_id}'
        return self.vk, self.user_id, self.hometown, self.gender, self.birth_date, response, user_info, self.self_age, self.link

# define matching criteria and return list of matching ids
    def find_people(self):
        '''
        Поиск пользователей в ВК на основе критериев (пол, возраст, город, предпочтения), ограничение числа пользователей (произвольно) до 15, возвращение ИД отобранных пользователей в ВК в виде списка.
        '''
        self.get_profile_info()
        gender_match = None
        if self.gender == '1':
            gender_match = '2'
        elif self.gender == '2':
            gender_match = '1'
        age_min = str(self.self_age - 3)  # min age for search matches
        age_max = str(self.self_age + 3)  # max age for search matches

        self.list_of_ids = []
        off_n = random.randint(1, 3)
        matches = self.vk.users.search(offset=off_n, count='200', hometown=self.hometown, sex=gender_match, age_from=age_min, age_to=age_max, fields='books, movies, music', has_photo='1')
        m_user_list = []
        for m_user in matches['items']:
            if 'books' or 'movies' or 'music' in m_user.keys():
                if m_user.get('books') or m_user.get('movies') or m_user.get('music'):
                    m_user_list.append(m_user)
        if len(m_user_list) > 15:
            final_match_list = random.sample(m_user_list, 15)
        else:
            final_match_list = m_user_list
        for user in final_match_list:
            self.list_of_ids.append(user['id'])
        return self.list_of_ids

# get photos of matching users
    def get_photos(self):
        '''
        Получение фотографий (в макс. размере) для отобранных (с помощью функции find_people) пользователей (при наличии доступа к фото). Возвращение словаря (ключ - ИД пользователя, значения - ссылка и число "лайков").
        '''
        self.find_people()
        self.photos_dict = dict()
        for id in self.list_of_ids:
            self.photos_dict[id] = []
            try:
                p = self.vk.photos.get(owner_id=id, album_id='profile', extended='1', photo_sizes='1')
                for n in range(p['count']):
                    try:
                        self.photos_dict[id].append({'likes': p['items'][n]['likes']['count'],
                                                     'link': p['items'][n]['sizes'][-1]['url']})
                    except IndexError:
                        print('no image')
            except vk_api.exceptions.ApiError:
                print('no access')
        return self.photos_dict

# find best photos by number of likes
    def get_best_photos(self):
        '''
        Сортировка фотографий всех пользователей (полученных с помощью функции get_photos) на основе числа "лайков", возвращение словаря (ключ - ИД пользователя, значения - ссылки на фотографии, отсортированные по числу "лайков").
        '''
        self.get_photos()
        self.sorted_dict_of_photos = dict()
        for k in self.photos_dict.keys():
            sorted_tuple = sorted(self.photos_dict[k], key=lambda x: x['likes'], reverse=True)
            self.sorted_dict_of_photos[k] = sorted_tuple
        return self.sorted_dict_of_photos

# find detailed info for matching users
    def get_info_by_user_id(self):
        '''
        Возвращает подробные сведения о каждом найденном (с помощью функции find_people) пользователе в виде списка словарей.
        '''
        matching_list = []
        for match_id in self.list_of_ids:
            match_rank = 0
            info = self.vk.users.get(user_id=match_id, fields='books, movies, music, bdate, home_town, sex')
            try:
                match_age = 2022 - (int(info[0]['bdate'].split('.')[-1]))
            except KeyError:
                match_age = None

            if info[0]['movies']:
                match_rank += 40
            if info[0]['music']:
                match_rank += 30
            if info[0]['books']:
                match_rank += 20

            user_dict = {'vk_user_id': match_id, 'first_name': info[0]['first_name'], 'last_name': info[0]['last_name'], 'age': match_age, 'gender': info[0]['sex'], 'city': info[0].get('home_town'), 'user_link': f'{URL}{match_id}', 'music': info[0]['music'], 'movies': info[0]['movies'], 'books': info[0]['books'], 'match_rank': match_rank}
            matching_list.append(user_dict)
        return matching_list
