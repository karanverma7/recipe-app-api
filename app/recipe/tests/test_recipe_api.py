from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    '''return recipe detail url'''
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main course'):
    '''create and return a sample tag'''
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamon'):
    '''create and return sample ingredient'''
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    '''Create sample recipe'''

    defaults = {
        'title': 'Chicken tikka',
        'time_minutes': 25,
        'price': 200.00
    }
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPITests(TestCase):
    '''Test Un-authenticated User's Recipe API'''

    def setUp(self):
        self.client = APIClient()

    def test_authentication_required(self):
        '''Test that authentication is required'''

        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    '''Test Authenticated User's Recipe API'''

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'sample@gmail.com',
            'password123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_list(self):
        '''Test retrieving recipes for the authenticated user'''

        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        '''Test retrieving recipes limited to authenticated user only'''

        user2 = get_user_model().objects.create_user(
            'other@gmail.com',
            'otherpassword'
        )
        sample_recipe(user=self.user)
        sample_recipe(user=user2)
        res = self.client.get(RECIPES_URL)
        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_view_detail(self):
        '''Test recipe detail view'''

        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        res = self.client.get(detail_url(recipe.id))
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        '''Test creating a basic recipe'''
        payload = {
            'title': 'Paneer Tikka',
            'time_minutes': 20,
            'price': 200.00,
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        '''Test creating a recipe with tags'''
        tag1 = sample_tag(user=self.user, name='Ginger')
        tag2 = sample_tag(user=self.user, name='Lemon')
        payload = {
            'title': 'Paneer Tikka',
            'time_minutes': 20,
            'price': 200.00,
            'tags': [tag1.id, tag2.id],
        }
        res = self.client.post(RECIPES_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(tags), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        '''Test creating a recipe with tags'''
        ingredient1 = sample_ingredient(user=self.user, name='Ginger')
        ingredient2 = sample_ingredient(user=self.user, name='Lemon')
        payload = {
            'title': 'Mashroom Tikka',
            'time_minutes': 30,
            'price': 150.00,
            'ingredients': [ingredient1.id, ingredient2.id],
        }
        res = self.client.post(RECIPES_URL, payload)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(ingredients), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
