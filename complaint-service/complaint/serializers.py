from rest_framework import serializers
from . import models

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Complaint
        fields = '__all__'

class ComplaintReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ComplaintReview
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Transaction
        fields = '__all__'
# 1

# 用于响应的复合序列化器
class ComplaintDetailSerializer(serializers.ModelSerializer):
    """
    投诉详情序列化器（包含关联信息）
    """
    # 这些字段将通过API调用其他服务获取
    complainer_info = serializers.SerializerMethodField()
    target_info = serializers.SerializerMethodField()

    class Meta:
        model = models.Complaint
        fields = '__all__'

    def get_complainer_info(self, obj):
        """
        获取举报用户信息（需要通过UserService API获取）
        """
        # 在views.py中实现具体的API调用逻辑
        return None

    def get_target_info(self, obj):
        """
        获取被举报对象信息（需要通过 ProductService 或 UserService API获取）
        """
        # 在views.py中实现具体的API调用逻辑
        return None


class ComplaintReviewDetailSerializer(serializers.ModelSerializer):
    """
    投诉审核详情序列化器
    """
    reviewer_info = serializers.SerializerMethodField()

    class Meta:
        model = models.ComplaintReview
        fields = '__all__'

    def get_reviewer_info(self, obj):
        """
        获取审核员信息（需要通过UserService API获取）
        """
        # 在views.py中实现具体的API调用逻辑
        return None