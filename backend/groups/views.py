from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Group, GroupMembership
from .serializers import GroupSerializer,GroupMemberWithRoleSerializer

from roles.models import GroupUserRole
from accounts.models import User
from roles.models import Role
from rest_framework import status



class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        group = serializer.save(owner=self.request.user)

        # 1. Add the creator as Admin
        admin_role, _ = Role.objects.get_or_create(name="Admin", group=group)
        GroupUserRole.objects.get_or_create(user=self.request.user, group=group, role=admin_role)

        # 2. Add the creator to GroupMembership
        GroupMembership.objects.get_or_create(group=group, user=self.request.user)

        # 3. Add ALL users with is_org_admin=True as Owner
        owner_role, _ = Role.objects.get_or_create(name="Owner", group=group)
        org_admins = User.objects.filter(is_org_admin=True)
        for admin_user in org_admins:
            GroupUserRole.objects.get_or_create(user=admin_user, group=group, role=owner_role)
            GroupMembership.objects.get_or_create(group=group, user=admin_user)

class GroupMembershipListView(generics.ListAPIView):
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Group.objects.filter(memberships__user=self.request.user)


class JoinGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)

        # Default to request.user
        user_to_add = request.user

        # Check if user_id is provided in body
        user_id = request.data.get('user_id')
        if user_id and str(user_id) != str(request.user.id):
            # Allow only if request.user is admin/owner of the group
            allowed_roles = ["Admin", "Owner"]
            has_permission = GroupUserRole.objects.filter(
                user=request.user,
                group=group,
                role__name__in=allowed_roles
            ).exists()

            if not has_permission:
                return Response({"error": "Only Admins or Owners can add other users."}, status=403)

            user_to_add = get_object_or_404(User, id=user_id)

        # Add the user to GroupMembership
        GroupMembership.objects.get_or_create(group=group, user=user_to_add)

        return Response({"message": f"{user_to_add.email} joined group successfully"}, status=status.HTTP_201_CREATED)

class GroupMembersByGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)

        membership_users = User.objects.filter(group_memberships__group=group)
        role_users = User.objects.filter(groupuserrole__group=group)
        org_admin_users = User.objects.filter(is_org_admin=True)
        all_users = set(membership_users) | set(role_users) | set(org_admin_users) | {group.owner}

        serializer = GroupMemberWithRoleSerializer(all_users, many=True, context={'group': group})
        return Response(serializer.data)

class RemoveGroupMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, group_id, user_id):
        group = get_object_or_404(Group, id=group_id)
        target_user = get_object_or_404(User, id=user_id)
        acting_user = request.user

        if target_user == group.owner:
            return Response({"error": "You cannot remove the group owner."}, status=403)

        # Get roles of acting and target users
        acting_role = GroupUserRole.objects.filter(user=acting_user, group=group).first()
        target_role = GroupUserRole.objects.filter(user=target_user, group=group).first()

        # Role levels for hierarchy
        role_priority = {"Owner": 3, "Admin": 2, "Member": 1}
        acting_level = role_priority.get(acting_role.role.name) if acting_role else 0
        target_level = role_priority.get(target_role.role.name) if target_role else 0

        # Permission check
        if acting_level <= target_level or acting_level == 0:
            return Response({"error": "Permission denied."}, status=403)

        # Remove from GroupMembership
        GroupMembership.objects.filter(group=group, user=target_user).delete()

        # Remove role
        GroupUserRole.objects.filter(group=group, user=target_user).delete()

        return Response({"message": f"User {target_user.email} removed from group."}, status=200)
