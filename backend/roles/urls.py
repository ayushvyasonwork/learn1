from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoleViewSet, PermissionViewSet, GroupUserRoleViewSet,CreatePermissionView

router = DefaultRouter()
router.register(r'roles', RoleViewSet)
router.register(r'permissions', PermissionViewSet)
router.register(r'user-roles', GroupUserRoleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('permissions/create/', CreatePermissionView.as_view(), name='create-permission'),
]
