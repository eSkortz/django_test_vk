from django.test import TestCase, Client
from .models import User
from django.urls import reverse
from rest_framework import status


class LoginUserViewTestCase(TestCase):
    

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.login_url = reverse('login')


    def test_incorrect_method(self):
        response = self.client.get(self.login_url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_valid_login(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'success': 'Авторизация прошла успешно'})


    def test_invalid_login(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'wrongpassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'Неверный логин или пароль'})


class RegisterUserTestCase(TestCase):


    def setUp(self):
        self.client = Client()
        self.registration_url = reverse('register')


    def test_incorrect_method(self):
        response = self.client.get(self.registration_url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_register_user(self):
        response = self.client.post(self.registration_url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue('_auth_user_id' in self.client.session)
        self.assertEqual(response.data, {'success': 'Пользователь зарегестрирован успешно'})


    def test_register_user_with_existing_username(self):
        User.objects.create_user(username='testuser', password='testpassword')
        response = self.client.post(self.registration_url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertFalse('_auth_user_id' in self.client.session)
        self.assertEqual(response.data, {'error': 'Такой пользователь уже существует'})


class LogoutUserTestCase(TestCase):


    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.logout_url = reverse('logout')
        self.login_url = reverse('login')
    

    def test_incorrect_method(self):
        self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)  


    def test_logout_user(self):
        self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'success': 'Выход выполнен успешно'})


class SendFriendRequestTestCase(TestCase):


    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='testuser1', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword')
        self.login_url = reverse('login')
        self.send_friend_request_url = reverse('send_request')
    

    def test_incorrect_method(self):
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        response = self.client.get(self.send_friend_request_url, {'to_user_id': self.user2.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_send_request_success(self):
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        response = self.client.post(self.send_friend_request_url, {'to_user_id': self.user2.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'success': 'Запрос дружбы успешно отправлен'})
    

    def test_send_request_non_existent_user(self):
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        response = self.client.post(self.send_friend_request_url, {'to_user_id': '0'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error':'Такого пользователя не существует'})

    
    def test_send_request_twice(self):
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user2.id}, format='json')
        response = self.client.post(self.send_friend_request_url, {'to_user_id': self.user2.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'error':'У вас уже есть активная заявка с этим пользователем'})
    

    def test_send_request_to_myself(self):
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        response = self.client.post(self.send_friend_request_url, {'to_user_id': self.user1.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_402_PAYMENT_REQUIRED)
        self.assertEqual(response.data, {'error':'Вы не можете отправить заявку самому себе'})


class AcceptFriendRequestTestCase(TestCase):


    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='testuser1', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword')
        self.login_url = reverse('login')
        self.send_friend_request_url = reverse('send_request')
        self.accept_friend_request_url = reverse('accept_request')
    

    def test_incorrect_method(self):
        self.client.post(self.login_url, {'username': 'testuser2', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user1.id}, format='json')
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        response = self.client.get(self.accept_friend_request_url, {'friend_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    
    def test_accept_request_success(self):
        self.client.post(self.login_url, {'username': 'testuser2', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user1.id}, format='json')
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        response = self.client.post(self.accept_friend_request_url, {'friend_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'success':'Заявка успешно принята'})

    
    def test_accept_request_non_existent_user(self):
        self.client.post(self.login_url, {'username': 'testuser2', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user1.id}, format='json')
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        response = self.client.post(self.accept_friend_request_url, {'friend_id': '0'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error':'Такого пользователя не существует'})
    

    def test_accept_request_non_existent_request(self):
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        response = self.client.post(self.accept_friend_request_url, {'friend_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'error':'У вас нет активных заявок от этого пользователя'})


class RejectFriendRequestTestCase(TestCase):


    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='testuser1', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword')
        self.login_url = reverse('login')
        self.send_friend_request_url = reverse('send_request')
        self.reject_friend_request_url = reverse('reject_request')
    

    def test_incorrect_method(self):
        self.client.post(self.login_url, {'username': 'testuser2', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user1.id}, format='json')
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        response = self.client.get(self.reject_friend_request_url, {'friend_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    

    def test_reject_request_success(self):
        self.client.post(self.login_url, {'username': 'testuser2', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user1.id}, format='json')
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        response = self.client.post(self.reject_friend_request_url, {'friend_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'success':'Заявка успешно отклонена'})


    def test_reject_request_non_existent_user(self):
        self.client.post(self.login_url, {'username': 'testuser2', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user1.id}, format='json')
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        response = self.client.post(self.reject_friend_request_url, {'friend_id': '0'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error':'Такого пользователя не существует'})
    

    def test_reject_request_non_existent_request(self):
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        response = self.client.post(self.reject_friend_request_url, {'friend_id': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'error':'У вас нет активных заявок от этого пользователя'})


class GetFriendsTestCase(TestCase):


    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='testuser', password='testpassword')
        self.login_url = reverse('login')
        self.get_friends_url = reverse('get_friends')
    

    def test_incorrect_method(self):
        self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        response = self.client.get(self.get_friends_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_get_friends_success(self):
        self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        response = self.client.post(self.get_friends_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetFriendRequestsTestCase(TestCase):


    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='testuser', password='testpassword')
        self.login_url = reverse('login')
        self.get_friend_requests_url = reverse('get_friend_requests')


    def test_incorrect_method(self):
        self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        response = self.client.get(self.get_friend_requests_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_get_friend_requests(self):
        self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'}, format='json')
        response = self.client.post(self.get_friend_requests_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ViewFriendStatusTestCase(TestCase):


    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='testuser1', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword')
        self.login_url = reverse('login')
        self.send_friend_request_url = reverse('send_request')
        self.view_friend_status_url = reverse('friendship_status')
    

    def test_incorrect_method(self):
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user2.id}, format='json')
        response = self.client.get(self.view_friend_status_url, {'friend_id':self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_view_friend_status_success_outgoing_request(self):
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user2.id}, format='json')
        response = self.client.post(self.view_friend_status_url, {'friend_id':self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    

    def test_view_friend_status_success_incoming_request(self):
        self.client.post(self.login_url, {'username': 'testuser2', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user1.id}, format='json')
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        response = self.client.post(self.view_friend_status_url, {'friend_id':self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    

    def test_view_friend_status_non_existent_user(self):
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user2.id}, format='json')
        response = self.client.post(self.view_friend_status_url, {'friend_id':'0'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error':'Такого пользователя не существует'})
    

    def test_view_friend_status_non_existent_requests(self):
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        response = self.client.post(self.view_friend_status_url, {'friend_id':self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'error':'У вас нет заявок с этим пользователем'})


class RemoveFriendTestCase(TestCase):


    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='testuser1', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword')
        self.login_url = reverse('login')
        self.send_friend_request_url = reverse('send_request')
        self.remove_friend_url = reverse('remove_friend')
    

    def test_incorrect_method(self):
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user2.id}, format='json')
        self.client.post(self.login_url, {'username': 'testuser2', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user1.id}, format='json')
        response = self.client.get(self.remove_friend_url, {'friend_id':self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_delete_outgoing_request_success(self):
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user2.id}, format='json')
        response = self.client.post(self.remove_friend_url, {'friend_id':self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'success': 'Пользователь успешно удален из друзей'})

    
    def test_delete_incoming_request_success(self):
        self.client.post(self.login_url, {'username': 'testuser2', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user1.id}, format='json')
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        response = self.client.post(self.remove_friend_url, {'friend_id':self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'success': 'Пользователь успешно удален из друзей'})
    

    def test_delete_two_requests_success(self):
        self.client.post(self.login_url, {'username': 'testuser2', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user1.id}, format='json')
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user2.id}, format='json')
        response = self.client.post(self.remove_friend_url, {'friend_id':self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'success': 'Пользователь успешно удален из друзей'})
    

    def test_remove_friend_non_existent_user(self):
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        self.client.post(self.send_friend_request_url, {'to_user_id': self.user2.id}, format='json')
        response = self.client.post(self.remove_friend_url, {'friend_id':'0'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error':'Такого пользователя не существует'})
    

    def test_remove_friend_non_existent_requests(self):
        self.client.post(self.login_url, {'username': 'testuser1', 'password': 'testpassword'}, format='json')
        response = self.client.post(self.remove_friend_url, {'friend_id':self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'error':'У вас нет заявок с этим пользователем'})