from rest_framework import serializers
from .models import Group, GroupMembership
from accounts.models import User  # Use your custom User model

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
