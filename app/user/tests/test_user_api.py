from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    '''Test the User API (Public)'''

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        '''Test user creation with valid payload'''

        payload = {
            'email': 'test@gmail.com',
            'password': 'test123',
            'name': 'Test user',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        '''Test user creation that already exists fails'''

        payload = {
            'email': 'test@gmail.com',
            'password': 'test123',
            'name': 'Test User',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        '''Test that password must be more than 5 characters'''

        payload = {
            'email': 'test@gmail.com',
            'password': 'pw',
            'name': 'Test User',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        '''Test token creation for user'''

        payload = {'email': 'test@gmail.com', 'password': 'test123'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        '''Test that token is not created with invalid credentials'''

        create_user(email='test@gmail.com', password='test123')
        payload = {'email': 'test@gmail.com', 'password': 'wrong'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        '''Test that token is not created if user doesn't exists'''

        payload = {'email': 'test@gmail.com', 'password': 'test123'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_fields(self):
        '''Test that email and password are required'''

        payload = {'email': 'test@gmail.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_update_unauthorized(self):
        '''Test that user authentication is required'''

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    '''Test API requests that require authentication'''

    def setUp(self):
        self.user = create_user(
            email='test@gmail.com',
            password='test123',
            name='Test User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        '''Test retrieving user profile for logged in user'''

        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        '''Test that post is not allowed for ME URL'''

        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        '''Test updating user profile for authenticated user'''

        payload = {'email': 'new@gmail.com', 'password': 'newPass'}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, payload['email'])
        self.assertTrue(self.user.check_password(payload['password']))