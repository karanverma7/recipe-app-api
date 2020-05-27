from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Tag
from recipe.serializers import TagSerializer


class TagViewSet(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.CreateModelMixin):
    '''Manage tags in the database'''

    serializer_class = TagSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()

    def get_queryset(self):
        '''Get queryset for the authenticated user only'''
        user = self.request.user
        if user:
            return self.queryset.filter(user=user).order_by('-name')
        return Tag.objects.none()

    def perform_create(self, serializer):
        '''Create a new tag'''

        serializer.save(user=self.request.user)
