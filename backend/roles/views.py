from rest_framework import viewsets,generics
from .models import Role, Permission, GroupUserRole
from .serializers import RoleSerializer, PermissionSerializer, GroupUserRoleSerializer
from .permissions import HasGroupPermission,IsOrgAdmin 

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [HasGroupPermission]

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [HasGroupPermission]

class GroupUserRoleViewSet(viewsets.ModelViewSet):
    queryset = GroupUserRole.objects.all()
    serializer_class = GroupUserRoleSerializer
    permission_classes = [HasGroupPermission]

class CreatePermissionView(generics.CreateAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsOrgAdmin]  # <- only org admins allowed
