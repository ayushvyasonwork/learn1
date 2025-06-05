from django.urls import path
from .views import GroupListCreateView, GroupMembershipListView, JoinGroupView

urlpatterns = [
    path('', GroupListCreateView.as_view(), name='group-list-create'),
    path('memberships/', GroupMembershipListView.as_view(), name='group-memberships'),
    path('<int:group_id>/join/', JoinGroupView.as_view(), name='join-group'),

]
