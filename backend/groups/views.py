from rest_framework import generics, permissions
from .models import Group, GroupMembership
from .serializers import GroupSerializer, GroupMembershipSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        group = serializer.save(owner=self.request.user)
        # Add owner as a member as well
        GroupMembership.objects.create(group=group, user=self.request.user)

class GroupMembershipListView(generics.ListAPIView):
    serializer_class = GroupMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GroupMembership.objects.filter(user=self.request.user)

class JoinGroupView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        GroupMembership.objects.get_or_create(group=group, user=request.user)
        return Response({'message': 'Joined group successfully'}, status=201)

