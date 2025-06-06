from rest_framework import serializers
from .models import Group, GroupMembership
from accounts.models import User  # Use your custom User model
from roles.models import GroupUserRole
class GroupSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Group
        fields = ['id', 'name', 'owner', 'created_at']

class GroupMembershipSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    group = serializers.StringRelatedField()

    class Meta:
        model = GroupMembership
        fields = ['id', 'group', 'user', 'joined_at']


class GroupMemberWithRoleSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role']

    def get_role(self, user):
        group = self.context.get('group')
        if not group:
            return None

        # Check GroupUserRole
        group_user_role = GroupUserRole.objects.filter(user=user, group=group).first()
        if group_user_role:
            return group_user_role.role.name

        # Fallback: if user is owner of the group model or marked is_org_admin
        if user == group.owner or getattr(user, "is_org_admin", False):
            return 'Owner'

        # Check if they’re in the group membership
        if GroupMembership.objects.filter(user=user, group=group).exists():
            return 'Member'

        return 'Unknown'
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role']

    def get_role(self, user):
        group = self.context.get('group')
        if not group:
            return None

        # First check roles
        group_user_role = GroupUserRole.objects.filter(user=user, group=group).first()
        if group_user_role:
            return group_user_role.role.name

        # Then check if they are the owner
        if group.owner == user:
            return 'Owner'

        # Fallback: is a member
        if GroupMembership.objects.filter(user=user, group=group).exists():
            return 'Member'

        return 'Unknown'