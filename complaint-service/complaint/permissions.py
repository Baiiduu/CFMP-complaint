from rest_framework import permissions

class IsAuthenticated(permissions.BasePermission):
    """
    自定义权限类，仅允许已登录的用户访问。
    """

    def has_permission(self, request, view):
        # 检查是否通过网关认证（检查请求头中的用户信息）
        user_id = request.META.get('HTTP_X_USER_UUID')
        return user_id is not None

class IsAdminUser(permissions.BasePermission):
    """
    自定义权限类，仅允许 privilege == 1 的用户访问。
    """

    def has_permission(self, request, view):
        # 检查用户是否是认证用户，并且其 privilege 等于 1
        from .service_client import ServiceClient

        user_id = request.META.get('HTTP_X_USER_UUID')
        if not user_id:
            return False
        print("用户ID:", user_id)
        try:
            user_result = ServiceClient.get("UserService", f"/api/users/{user_id}")
            print("用户9999999999999999", user_result)
            if user_result["success"]:
                user_data = user_result["data"]
                return user_data.get("privilege", 0) == 1
        except Exception as e:
            print(f"验证用户权限时出错: {e}")
        return False

class IsComplaintOwner(permissions.BasePermission):
    """
    自定义权限类，仅允许投诉所有者或管理员访问。
    """

    def has_object_permission(self, request, view, obj):
        from .service_client import ServiceClient
        # 管理员可以访问所有对象
        user_id = request.META.get('HTTP_X_USER_UUID')
        if not user_id:
            return False

        # 首先检查是否为管理员
        try:
            user_result = ServiceClient.get("UserService", f"/api/users/{user_id}")
            if user_result["success"]:
                user_data = user_result["data"]
                # 如果是管理员，允许访问
                if user_data.get("privilege", 0) == 1:
                    return True
        except Exception as e:
            print(f"验证管理员权限时出错: {e}")
            return False

        # 投诉所有者可以访问自己的投诉
        if user_id:
            try:
                user_id = int(user_id)
                if hasattr(obj, 'complainer_id'):
                    return obj.complainer_id == user_id
            except (ValueError, TypeError):
                pass
        return False




    def has_permission(self, request, view):
        # 基本认证检查
        user_id = request.META.get('HTTP_X_USER_UUID')
        return user_id is not None