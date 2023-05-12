from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction

from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from drf_yasg import openapi

from .models import User, Friendship


class MyView(viewsets.ViewSet):

    # Авторизация юзера
    @csrf_exempt
    @swagger_auto_schema(
        method='post',
        tags=['Функция входа'],
        operation_id = 'Функция для авторизации пользователя',
        operation_description = 'Эта функция используется для авторизации пользователя и принимает на вход два значения: логин и пароль',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description='Успешная авторизация',
                examples={
                    'application/json': {
                        'success': 'Авторизация прошла успешно'
                    }
                }
            ),
            400: openapi.Response(
                description='Некорректные данные авторизации',
                examples={
                    'application/json': {
                        'error': 'Неверный логин или пароль'
                    }
                }
            ),
            405: openapi.Response(
                description='Метод не разрешен',
                examples={
                    'application/json': {
                        'error': 'Неверный метод запроса'
                    }
                }
            ),
        }
    )
    @api_view(['POST'])
    def login_user(request):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return Response(data={'success': 'Авторизация прошла успешно'}, status=200)
            else:
                return Response(data={'error': 'Неверный логин или пароль'}, status=400)
        else:
            return Response(data={'error': 'Неверный метод запроса'}, status=405)

    # Регистрация нового юзера
    @csrf_exempt
    @swagger_auto_schema(
        method='post',
        tags=['Функция регистрации'],
        operation_id = 'Функция для регистрации пользователя',
        operation_description = 'Эта функция используется для регистрации пользователя и принимает на вход два значения: логин и пароль',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description='Успешная регистрация',
                examples={
                    'application/json': {
                        'success': 'Пользователь зарегестрирован успешно'
                    }
                }
            ),
            400: openapi.Response(
                description='Некорректные данные для регистрации',
                examples={
                    'application/json': {
                        'error':'Такой пользователь уже существует'
                    }
                }
            ),
            405: openapi.Response(
                description='Метод не разрешен',
                examples={
                    'application/json': {
                        'error': 'Неверный метод запроса'
                    }
                }
            ),
        }
    )
    @api_view(['POST'])
    @transaction.atomic # Для того, чтобы поймать IntegrityError при создании существующего пользователя
    def register_user(request):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            try:
                user = User.objects.create_user(username=username, password=password)
            except IntegrityError:
                return Response(data={'error':'Такой пользователь уже существует'}, status = 400)
            else:
                login(request, user)
                return Response(data={'success': 'Пользователь зарегестрирован успешно'}, status=200)
        else:
            return Response(data={'error': 'Неверный метод запроса'}, status=405)

    # Деавторизация юзера
    @csrf_exempt
    @swagger_auto_schema(
        method='post',
        tags=['Функция выхода'],
        operation_id = 'Функция для выхода из системы',
        operation_description = 'Эта функция используется для выхода из системы и не принимает входных параметров',
        responses={
            200: openapi.Response(
                description='Успешный выход',
                examples={
                    'application/json': {
                        'success': 'Выход выполнен успешно'
                    }
                }
            ),
            405: openapi.Response(
                description='Метод не разрешен',
                examples={
                    'application/json': {
                        'error': 'Неверный метод запроса'
                    }
                }
            ),
        }
    )
    @api_view(['POST'])
    def logout_user(request):
        if request.method == 'POST':
            logout(request)
            return Response(data={'success': 'Выход выполнен успешно'}, status=200)
        else:
            return Response(data={'error': 'Неверный метод запроса'}, status=405)
        
    # Отправка заявки в друзья
    @login_required
    @csrf_exempt
    @swagger_auto_schema(
        method='post',
        tags=['Функция отправки заявки'],
        operation_id = 'Функция для отправки заявки в друзья пользователю',
        operation_description = 'Эта функция используется для отправки запроса в друзья другому пользователю, требует быть авторизованным',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['to_user_id'],
            properties={
                'to_user_id': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description='Успешная отправка заявки',
                examples={
                    'application/json': {
                        'success': 'Запрос дружбы успешно отправлен'
                    }
                }
            ),
            400: openapi.Response(
                description='Пользователь не существует',
                examples={
                    'application/json': {
                        'error':'Такого пользователя не существует'
                    }
                }
            ),
            401: openapi.Response(
                description='Заявка уже отправлена',
                examples={
                    'application/json': {
                        'error':'У вас уже есть активная заявка с этим пользователем'
                    }
                }
            ),
            402: openapi.Response(
                description='Заявка самому себе',
                examples={
                    'application/json': {
                        'error':'Вы не можете отправить заявку самому себе'
                    }
                }
            ),
            405: openapi.Response(
                description='Метод не разрешен',
                examples={
                    'application/json': {
                        'error': 'Неверный метод запроса'
                    }
                }
            ),
        }
    )
    @api_view(['POST'])
    def send_friend_request(request):
        if request.method == 'POST':
            to_user_id = request.POST.get('to_user_id')
            user1 = request.user
            try:
                user2 = get_object_or_404(User, id=to_user_id)
            except Exception:
                return Response(data={'error':'Такого пользователя не существует'}, status=400)
            else:
                if user1.id != user2.id:
                    try:
                        friendship = Friendship(from_user=user1, to_user=user2, status='pending')
                        friendship.save()
                    except Exception:
                        return Response(data={'error':'У вас уже есть активная заявка с этим пользователем'}, status=401)
                    else:
                        try:
                            friendship2 = get_object_or_404(Friendship, from_user=user2, to_user=user1)
                        except Exception:
                            return Response(data={'success': 'Запрос дружбы успешно отправлен'}, status=200)
                        else:
                            friendship1 = get_object_or_404(Friendship, from_user=user1, to_user=user2)
                            if friendship2.status == 'accepted' or friendship2.status == 'pending':
                                friendship1.status = 'accepted'
                                friendship2.status = 'accepted'
                                friendship1.save()
                                friendship2.save()
                            return Response(data={'success': 'Запрос дружбы успешно отправлен'}, status=200)
                else:
                    return Response(data={'error':'Вы не можете отправить заявку самому себе'}, status=402)
        else:
            return Response(data={'error': 'Неверный метод запроса'}, status=405)

    # Принятие заявки в друзья
    @login_required
    @csrf_exempt
    @swagger_auto_schema(
        method='post',
        tags=['Функция принятия заявки'],
        operation_id = 'Функция для принятия заявки в друзья от пользователя',
        operation_description = 'Эта функция используется для принятия заявки в друзья от пользователя, требует авторизации',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['friend_id'],
            properties={
                'friend_id': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description='Заявка принята',
                examples={
                    'application/json': {
                        'success':'Заявка успешно принята'
                    }
                }
            ),
            400: openapi.Response(
                description='Пользователь не существует',
                examples={
                    'application/json': {
                        'error':'Такого пользователя не существует'
                    }
                }
            ),
            401: openapi.Response(
                description='Заявка отстуствует',
                examples={
                    'application/json': {
                        'error':'У вас нет активных заявок от этого пользователя'
                    }
                }
            ),
            405: openapi.Response(
                description='Метод не разрешен',
                examples={
                    'application/json': {
                        'error': 'Неверный метод запроса'
                    }
                }
            ),
        }
    )
    @api_view(['POST'])
    def accept_friend_request(request):
        if request.method == 'POST':
            friend_id = request.POST.get('friend_id')
            user1 = request.user
            try:
                user2 = get_object_or_404(User, id=friend_id)
            except Exception:
                return Response(data={'error':'Такого пользователя не существует'}, status=400)
            else:
                try:
                    friendship = get_object_or_404(Friendship, to_user=user1, from_user=user2)
                except Exception:
                    return Response(data={'error':'У вас нет активных заявок от этого пользователя'}, status=401)
                else:
                    friendship.status = 'accepted'
                    friendship.save()
                    return Response(data={'success':'Заявка успешно принята'}, status=200)
        else:
            return Response(data={'error': 'Неверный метод запроса'}, status=405)

    # Отклонение заявки в друзья
    @login_required
    @csrf_exempt
    @swagger_auto_schema(
        method='post',
        tags=['Функция отклонения заявки'],
        operation_id = 'Функция для отклонения заявки в друзья от пользователя',
        operation_description = 'Эта функция используется для отклонения заявки в друзья от пользователя, требует авторизации',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['friend_id'],
            properties={
                'friend_id': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description='Заявка отклонена',
                examples={
                    'application/json': {
                        'success':'Заявка успешно отклонена'
                    }
                }
            ),
            400: openapi.Response(
                description='Пользователь не существует',
                examples={
                    'application/json': {
                        'error':'Такого пользователя не существует'
                    }
                }
            ),
            401: openapi.Response(
                description='Заявка отстуствует',
                examples={
                    'application/json': {
                        'error':'У вас нет активных заявок от этого пользователя'
                    }
                }
            ),
            405: openapi.Response(
                description='Метод не разрешен',
                examples={
                    'application/json': {
                        'error': 'Неверный метод запроса'
                    }
                }
            ),
        }
    )
    @api_view(['POST'])
    def reject_friend_request(request):
        if request.method == 'POST':
            friend_id = request.POST.get('friend_id')
            user1 = request.user
            try:
                user2 = get_object_or_404(User, id=friend_id)
            except Exception:
                return Response(data={'error':'Такого пользователя не существует'}, status=400)
            else:
                try:
                    friendship = get_object_or_404(Friendship, to_user=user1, from_user=user2)
                except Exception:
                    return Response(data={'error':'У вас нет активных заявок от этого пользователя'}, status=401)
                else:
                    friendship.status = 'rejected'
                    friendship.save()
                    return Response(data={'success':'Заявка успешно отклонена'}, status=200)
        else:
            return Response(data={'error': 'Неверный метод запроса'}, status=405)

    # Получения списка друзей
    @login_required
    @csrf_exempt
    @swagger_auto_schema(
        method='post',
        tags=['Функция просмотра списка друзей'],
        operation_id = 'Функция для просмотра списка друзей пользователя',
        operation_description = 'Эта функция используется для списка друзей пользователя, требует авторизации',
        responses={
            200: openapi.Response(
                description='Список друзей получен',
                examples={
                    'application/json': {
                        'friends': '[friend_list]'
                    }
                }
            ),
            405: openapi.Response(
                description='Метод не разрешен',
                examples={
                    'application/json': {
                        'error': 'Неверный метод запроса'
                    }
                }
            ),
        }
    )
    @api_view(['POST'])
    def get_friends(request):
        if request.method == 'POST':
            user = request.user
            friends = Friendship.objects.filter(
                (Q(from_user=user) | Q(to_user=user)) & Q(status='accepted')
            )
            friend_list = []
            for friend in friends:
                if friend.from_user == user:
                    friend_id = friend.to_user.id
                else:
                    friend_id = friend.from_user.id
                friend_list.append({
                    'id': friend_id,
                    'username': friend.to_user.username if friend.from_user == user else friend.from_user.username
                })
            return Response({'friends': friend_list}, status=200)
        else:
            return Response(data={'error': 'Неверный метод запроса'}, status=405)

    # Получение списка входящих и исходящих заявок
    @login_required
    @csrf_exempt
    @swagger_auto_schema(
        method='post',
        tags=['Функция просмотра списка заявок'],
        operation_id = 'Функция для просмотра списка исходящих и входящих заявок в друзья',
        operation_description = 'Эта функция используется для списка заявок в друзья пользователя, требует авторизации',
        responses={
            200: openapi.Response(
                description='Список заявок получен',
                examples={
                    'application/json': {
                        'incoming_requests': '[incoming_list]',
                        'outgoing_requests': '[outgoing_list]'
                    }
                }
            ),
            405: openapi.Response(
                description='Метод не разрешен',
                examples={
                    'application/json': {
                        'error': 'Неверный метод запроса'
                    }
                }
            ),
        }
    )
    @api_view(['POST'])
    def get_friend_requests(request):
        if request.method == 'POST':
            user = request.user
            incoming_requests = Friendship.objects.filter(to_user=user)
            incoming_list = []
            for request in incoming_requests:
                incoming_list.append({
                    'id': request.from_user.id,
                    'username': request.from_user.username,
                    'status' : request.status
                })
            outgoing_requests = Friendship.objects.filter(from_user=user)
            outgoing_list = []
            for request in outgoing_requests:
                outgoing_list.append({
                    'id': request.to_user.id,
                    'username': request.to_user.username,
                    'status' : request.status
                })
            return Response(data={
                'incoming_requests': incoming_list,
                'outgoing_requests': outgoing_list
            }, status=200)
        else:
            return Response(data={'error': 'Неверный метод запроса'}, status=405)

    # Получение статуса дружбы с юзером
    @login_required
    @csrf_exempt
    @swagger_auto_schema(
        method='post',
        tags=['Функция просмотра статуса дружбы'],
        operation_id = 'Функция для просмотра статуса дружбы с пользователем',
        operation_description = 'Эта функция используется для статуса дружбы с пользователем, требует авторизации',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['friend_id'],
            properties={
                'friend_id': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description='Статус дружбы',
                examples={
                    'application/json': {
                        'friend': 'id',
                        'status': 'status'
                    }
                }
            ),
            400: openapi.Response(
                description='Пользователь не существует',
                examples={
                    'application/json': {
                        'error':'Такого пользователя не существует'
                    }
                }
            ),
            401: openapi.Response(
                description='Заявка отстуствует',
                examples={
                    'application/json': {
                        'error':'У вас нет заявок с этим пользователем'
                    }
                }
            ),
            405: openapi.Response(
                description='Метод не разрешен',
                examples={
                    'application/json': {
                        'error': 'Неверный метод запроса'
                    }
                }
            ),
        }
    )
    @api_view(['POST'])
    def view_friend_status(request):
        if request.method == 'POST':
            friend_id = request.POST.get('friend_id')
            try:
                user1 = request.user
                user2 = get_object_or_404(User, id=friend_id)
            except Exception:
                return Response(data={'error':'Такого пользователя не существует'}, status=400)
            else:
                friendship = Friendship.objects.filter((Q(from_user=user1) & Q(to_user=user2)) | (Q(from_user=user2) & Q(to_user=user1))).first()
                if not friendship:
                    return Response(data={'error':'У вас нет заявок с этим пользователем'}, status=401)
                else:
                    return Response(data={'friend': user2.id, 'status': friendship.status}, status=200)
        else:
            return Response(data={'error': 'Неверный метод запроса'}, status=405)


    # Удаление юзера из друзей
    @login_required
    @csrf_exempt
    @swagger_auto_schema(
        method='post',
        tags=['Функция удаления друга'],
        operation_id = 'Функция для удаления пользователя из друзей',
        operation_description = 'Эта функция используется для удаления пользователя из друзей, требует авторизации',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['friend_id'],
            properties={
                'friend_id': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            200: openapi.Response(
                description='Пользователь удален',
                examples={
                    'application/json': {
                        'success': 'Пользователь успешно удален из друзей'
                    }
                }
            ),
            400: openapi.Response(
                description='Пользователь не существует',
                examples={
                    'application/json': {
                        'error':'Такого пользователя не существует'
                    }
                }
            ),
            401: openapi.Response(
                description='Нет заявок',
                examples={
                    'application/json': {
                        'error': 'У вас нет заявок с этим пользователем'
                    }
                }
            ),
            405: openapi.Response(
                description='Метод не разрешен',
                examples={
                    'application/json': {
                        'error': 'Неверный метод запроса'
                    }
                }
            ),
        }
    )
    @api_view(['POST'])
    def remove_friend(request):
        if request.method == 'POST':
            friend_id = request.POST.get('friend_id')
            user1 = request.user
            try:
                user2 = get_object_or_404(User, id=friend_id)
            except Exception:
                return Response(data={'error':'Такого пользователя не существует'}, status=400)
            else:
                friendship1 = Friendship.objects.filter(Q(from_user=user1) & Q(to_user=user2))
                friendship2 = Friendship.objects.filter(Q(from_user=user2) & Q(to_user=user1))

            if friendship1 and friendship2:
                friendship1.delete()
                friendship2.delete()
                return Response({'success': 'Пользователь успешно удален из друзей'}, status=200)
            elif friendship1:
                friendship1.delete()
                return Response({'success': 'Пользователь успешно удален из друзей'}, status=200)
            elif friendship2:
                friendship2.delete()
                return Response({'success': 'Пользователь успешно удален из друзей'}, status=200)
            else:
                return Response(data={'error': 'У вас нет заявок с этим пользователем'}, status=401)
        else:
            return Response(data={'error': 'Неверный метод запроса'}, status=405)


