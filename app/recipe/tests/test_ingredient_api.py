from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientAPITests(TestCase):
    '''Test publically available Ingredient API'''

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        '''Test that authentication is required to retrieve ingredients'''

        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITest(TestCase):
    '''Test Ingredient API for authenticated user'''

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='test123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        '''Test retrieving ingredient list for authenticated user'''

        Ingredient.objects.create(user=self.user, name='Cucumber')
        Ingredient.objects.create(user=self.user, name='Cheese')
        res = self.client.get(INGREDIENT_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        '''Test that ingredient list belongs to authenticated user'''

        user2 = get_user_model().objects.create_user(
            'other@gmail.com',
            'otherpassword',
        )
        Ingredient.objects.create(user=user2, name='Banana')
        ingredient = Ingredient.objects.create(user=self.user, name='Mango')
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        '''Test creating a new tag'''

        payload = {'name': 'Test ingredient'}
        self.client.post(INGREDIENT_URL, payload)
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        '''Test creating a new tag with invalid payload'''

        payload = {'name': ''}
        res = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
