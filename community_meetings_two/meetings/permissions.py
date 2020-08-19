from rest_framework import permissions
from rest_framework.request import Request


class NormalPermiss(permissions.BasePermission):
    message="没有权限！"
    def has_permission(self, request:Request, view):
        if request.user.is_admin:
            return True
        else:
            return False


class MaintainerPermission(permissions.BasePermission):
    """需要Maintainer权限"""
    message = '权限不够！！！'
    level = 1

    def has_permission(self, request, view):  # 对于列表的访问权限
        if request.user.level > self.level:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):  # 对于对象的访问权限
        return self.has_permission(request, view)


class RootPermission(MaintainerPermission):
    """管理员权限"""
    message = '需要管理员权限！！！'
    level = 3