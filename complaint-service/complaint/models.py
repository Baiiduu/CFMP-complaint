from django.db import models

class Complaint(models.Model):
    """
       投诉模型
    """
    complaint_id = models.BigAutoField(primary_key=True)
    # 注意：在微服务中，我们不再直接引用其他服务的模型
    # 而是存储关联对象的ID
    complainer_id = models.UUIDField()  # 举报用户ID
    target_type = models.SmallIntegerField()  # 举报目标类型: 0-商品, 1-用户
    target_id = models.UUIDField()  # 被举报对象ID  User
    reason = models.TextField()  # 举报原因
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间
    status = models.SmallIntegerField(default=0)  # 状态: 0-待处理, 1-已处理

    class Meta:
        db_table = "complaint"
        ordering = ['-created_at']

class ComplaintReview(models.Model):
    """
       投诉审核模型
    """
    review_id = models.BigAutoField(primary_key=True)
    target_id = models.UUIDField(default="0")   # 被举报对象ID
    target_type = models.SmallIntegerField(default=0)  # 被举报对象类型
    reviewer_id = models.UUIDField()  # 审核员ID  User
    created_at = models.DateTimeField(auto_now_add=True)  # 审核时间
    result = models.CharField(max_length=100)  # 审核结果
    ban_type = models.CharField(max_length=100)  # 封禁类型
    ban_time = models.IntegerField(default=0)  # 封禁时间(天)

    class Meta:
        db_table = "complaint_review"
        ordering = ['-created_at']

class Transaction(models.Model):
    """
       事务日志模型
    """
    log_id = models.BigAutoField(primary_key=True)
    order_id = models.BigIntegerField()  # 订单ID Order
    event = models.CharField(max_length=100)  # 事件描述
    created_at = models.DateTimeField(auto_now_add=True)  # 创建时间

    class Meta:
        db_table = "transaction"
        ordering = ['-created_at']

# 需要注意的微服务改造点：

# 1. 移除了外键引用
# 原来的:
# complainer_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='complainer_id')
#
# 现在的:
# complainer_id = models.BigIntegerField()  # 只存储ID

# 2. 如果需要获取关联对象信息，需要通过API调用其他服务
# 例如获取用户信息需要调用 UserService
# 获取商品信息需要调用 ProductService

# 3. 在微服务架构中，数据一致性通过事件驱动或API调用来保证

