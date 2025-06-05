from rest_framework import serializers
from .models import Role, Permission, GroupUserRole

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    inherited_roles = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'group', 'permissions', 'inherited_roles']

class GroupUserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupUserRole
        fields = '__all__'
