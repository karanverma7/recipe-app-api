from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Tag, Ingredient, Recipe
from recipe.serializers import TagSerializer, IngredientSerializer, \
                               RecipeSerializer, RecipeDetailSerializer


class BaseRecipeAPIView(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    '''Base class for Recipe attribute's API Views'''

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        '''Get queryset for the authenticated user only'''

        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        '''Create new attributes'''

        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAPIView):
    '''Manage tags in the database'''

    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAPIView):
    '''Manage ingredients in database'''

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    '''Manage recipe in database'''

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()

    def get_queryset(self):
        '''Retrive the recipes for the authenticated user'''
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        '''Return appropriate serializer class'''

        if self.action == 'retrieve':
            return RecipeDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        '''Create new recipe'''
        serializer.save(user=self.request.user)
