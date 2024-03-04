from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from django.contrib.auth.models  import Group, User 
from django.shortcuts import get_object_or_404

from .serializers import UserSerializer
from .permissions import IsManagerOrAdmin


class ManagementMixin(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsManagerOrAdmin] 
    group_name = ''

    def get_queryset(self):
        return User.objects.filter(groups__name=self.group_name)
    
    def get_group(self):
        return Group.objects.get(name=self.group_name)
    
    def list(self, request):
        serializer = UserSerializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            self.get_group().user_set.add(user)
            return Response({"message":f"user has been added to the {self.group_name} group"}, status=status.HTTP_201_CREATED)
        return Response({"message":"user not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def destroy(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        self.get_group().user_set.remove(user)
        return Response({"message":f"user has been removed from the {self.group_name} group"}, status=status.HTTP_200_OK)
