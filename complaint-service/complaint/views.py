from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from . import models, serializers, filters as complaint_filters
from .permissions import IsAuthenticated, IsAdminUser, IsComplaintOwner
from .service_client import ServiceClient
import logging


logger = logging.getLogger(__name__)

class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = models.Complaint.objects.all()
    serializer_class = serializers.ComplaintSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = complaint_filters.ComplaintFilter  # 使用自定义过滤器类
    ordering_fields = ['created_at']
    lookup_field = 'complaint_id'
    # 默认权限设置
    permission_classes = [IsAuthenticated]

    def get_current_user_id(self, request):
        """从请求头获取当前用户ID"""
        user_id = request.META.get('HTTP_X_USER_UUID')
        if user_id:
            try:
                return int(user_id)
            except (ValueError, TypeError):
                return None
        return None

    def get_current_user_roles(self, request):
        """从 UserService 获取当前用户角色信息"""
        user_id = request.META.get('HTTP_X_USER_UUID')
        if not user_id:
            return []

        try:
            user_result = ServiceClient.get("UserService", f"/api/users/{user_id}")
            if user_result["success"]:
                user_data = user_result["data"]
                roles = []
                if user_data.get("privilege", 0) == 1:
                    roles.append("admin")
                return roles
        except Exception as e:
            logger.error(f"获取用户角色信息失败: {e}")

        return []

    def perform_create(self, serializer):
        """创建投诉时自动设置投诉人"""
        current_user_id = self.get_current_user_id(self.request)
        if not current_user_id:
            raise PermissionError("无法识别用户身份")
        # 第一步：微服务通信 - 验证用户是否存在
        # 调用服务: UserService
        # 接口路径: /api/users/{current_user_id}
        # 通信流程:
        #   - ServiceClient.get("UserService", f"/api/users/{current_user_id}")
        #   - 通过Nacos发现UserService实例
        #   - 构造完整URL并发起HTTP GET请求
        #   - 验证用户是否存在

        user_result = ServiceClient.get("UserService", f"/api/users/{current_user_id}")
        if not user_result["success"]:
            raise PermissionError(f"用户验证失败: {user_result['error']}")
        # 用户验证成功，保存投诉信息
        serializer.save(complainer_id=current_user_id)

    def get_queryset(self):
        """根据用户角色返回不同的查询集"""
        queryset = super().get_queryset()
        current_user_id = self.get_current_user_id(self.request)
        user_roles = self.get_current_user_roles(self.request)

        # 管理员可以看到所有投诉
        if 'admin' in user_roles:
            return queryset

        # 普通用户只能看到自己的投诉
        if current_user_id:
            return queryset.filter(complainer_id=current_user_id)

        # 如果无法识别用户，返回空查询集
        return queryset.none()


    def get_permissions(self):
        """
        根据不同操作设置权限
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            # 更新和删除操作需要所有者权限或管理员权限
            permission_classes = [IsComplaintOwner]
        elif self.action == 'create':
            # 创建操作只需要认证
            permission_classes = [IsAuthenticated]
        elif self.action in ['list', 'retrieve']:
            # 查看操作只需要认证
            permission_classes = [IsComplaintOwner]
        else:
            # 其他操作默认需要认证
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['get'])
    def mine(self, request):
        """获取当前用户的所有投诉"""
        user_id = self.get_current_user_id(request)
        complaints = self.queryset.filter(complainer_id=user_id)
        serializer = self.get_serializer(complaints, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def by_user(self, request):
        user_id = request.query_params.get('user_id')
        complaints = self.queryset.filter(complainer_id=user_id)
        serializer = self.get_serializer(complaints, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """获取单个投诉详情，包含关联信息"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # 获取序列化数据
        data = serializer.data

        # 获取投诉人信息
        if instance.complainer_id:
            user_result = ServiceClient.get("UserService", f"/api/users/{instance.complainer_id}")
            if user_result["success"]:
                data['complainer_info'] = user_result["data"]
            else:
                data['complainer_info'] = None
                logger.warning(f"获取投诉人信息失败: {user_result['error']}")

        # 获取被投诉对象信息
        if instance.target_id and instance.target_type is not None:
            if instance.target_type == 0:  # 商品
                product_result = ServiceClient.get("ProductService", f"/api/products/{instance.target_id}")
                if product_result["success"]:
                    data['target_info'] = product_result["data"]
                else:
                    data['target_info'] = None
                    logger.warning(f"获取商品信息失败: {product_result['error']}")
            elif instance.target_type == 1:  # 用户
                target_user_result = ServiceClient.get("UserService", f"/api/users/{instance.target_id}")
                if target_user_result["success"]:
                    data['target_info'] = target_user_result["data"]
                else:
                    data['target_info'] = None
                    logger.warning(f"获取被投诉用户信息失败: {target_user_result['error']}")


        return Response(data)


class ComplaintReviewViewSet(viewsets.ModelViewSet):
    queryset = models.ComplaintReview.objects.all()
    serializer_class = serializers.ComplaintReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = complaint_filters.ComplaintReviewFilter
    ordering_fields = ['created_at']
    lookup_field = 'review_id'

    permission_classes = [IsAdminUser]

    def get_current_user_id(self, request):
        """从请求头获取当前用户ID"""
        user_id = request.META.get('HTTP_X_USER_UUID')
        if user_id:
            try:
                return int(user_id)
            except (ValueError, TypeError):
                return None
        return None

    def get_current_user_roles(self, request):
        """从 UserService 获取当前用户角色信息"""
        user_id = self.get_current_user_id(request)
        if not user_id:
            return []

        try:
            user_result = ServiceClient.get("UserService", f"/api/users/{user_id}")
            if user_result["success"]:
                user_data = user_result["data"]
                roles = []
                # 检查 privilege 字段是否为 1（管理员）
                if user_data.get("privilege", 0) == 1:
                    roles.append("admin")
                return roles
        except Exception as e:
            logger.error(f"获取用户角色信息失败: {e}")

        return []

    def perform_create(self, serializer):
        """创建投诉审核记录"""
        current_user_id = self.get_current_user_id(self.request)
        if not current_user_id:
            raise PermissionError("无法识别用户身份")

        # 验证用户是否存在
        user_result = ServiceClient.get("UserService", f"/api/users/{current_user_id}")
        if not user_result["success"]:
            raise PermissionError(f"用户验证失败: {user_result['error']}")

        # 保存审核信息
        serializer.save(reviewer_id=current_user_id)

    def get_queryset(self):
        """根据用户角色返回不同的查询集"""
        queryset = super().get_queryset()
        current_user_id = self.get_current_user_id(self.request)
        user_roles = self.get_current_user_roles(self.request)

        # 管理员可以看到所有审核记录
        if 'admin' in user_roles:
            return queryset
        # 如果无法识别用户，返回空查询集
        return queryset.none()

    def get_permissions(self):
        """
        根据不同操作设置权限
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            # 更新和删除操作需要管理员权限
            permission_classes = [IsAdminUser]
        elif self.action in ['create', 'list', 'retrieve']:
            # 创建和查看操作需要管理员权限
            permission_classes = [IsAdminUser]
        else:
            # 其他操作默认需要管理员权限
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, *args, **kwargs):
        """获取单个审核详情，包含审核员信息"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # 获取序列化数据
        data = serializer.data

        # 获取审核员信息
        if instance.reviewer_id:
            reviewer_result = ServiceClient.get("UserService", f"/api/users/{instance.reviewer_id}")
            if reviewer_result["success"]:
                data['reviewer_info'] = reviewer_result["data"]
            else:
                data['reviewer_info'] = None
                logger.warning(f"获取审核员信息失败: {reviewer_result['error']}")

        return Response(data)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = models.Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = complaint_filters.TransactionFilter
    ordering_fields = ['created_at']
    lookup_field = 'log_id'
