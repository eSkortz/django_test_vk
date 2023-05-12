Django-сервис друзей

Основные функции:
- регистрация пользователя
- авторизация пользователя
- выход из учетной записи
- отправка запроса в друзья другому пользователю
- принятия входящей заявки в друзья
- отклонение входящей заявки в друзья
- получение списка друзей
- получение списка входящих и исходящих заявок и их статусов
- получение статуса дружбы с пользователем
- удаление пользователя из друзей
- автоматическое добавление в друзья при наличии обратной заявки

В файле friend_service.yaml можно найти openapi спецификацию сервиса

Краткую документацию с примерами запуска api можно найти по ссылке localhost:8000/api/docs после запуска сервиса

В корневой директории проекта находится Dockerfile и файл зависимостей requirements.txt для упаковки в контейнер

В проекте присутствуют unit-тесты, для их запуска стоит воспользоваться командой 'python manage.py test api.tests'

Для запуска отдельных модулей стоит воспользоваться командой 'python manage.py test api.tests.<Название тест-кейса>'. Ниже представлены названия и описание тест-кейсов:
- LoginUserViewTestCase (проверка views.login_user)
- RegisterUserTestCase (проверка views.register_user)
- LogoutUserTestCase (проверка views.logout_user)
- SendFriendRequestTestCase (проверка views.send_friend_request)
- AcceptFriendRequestTestCase (проверка views.accept_friend_request)
- RejectFriendRequestTestCase (проверка views.reject_friend_request)
- GetFriendsTestCase (проверка views.get_friends)
- GetFriendRequestsTestCase (проверка views.get_friend_requests)
- ViewFriendStatusTestCase (проверка views.view_friend_status)
- RemoveFriendTestCase (проверка views.remove_friend)
