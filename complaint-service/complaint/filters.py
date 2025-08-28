import django_filters
from django.utils import timezone
from . import models

class ComplaintFilter(django_filters.FilterSet):
    complainer_id = django_filters.NumberFilter(field_name='complainer_id')
    target_type = django_filters.NumberFilter(field_name='target_type')
    target_id = django_filters.NumberFilter(field_name='target_id')
    status = django_filters.NumberFilter(field_name='status')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    # 按日期范围过滤
    date_from = django_filters.DateFilter(method='filter_by_date_from')
    date_to = django_filters.DateFilter(method='filter_by_date_to')

    class Meta:
        model = models.Complaint
        fields = ['complainer_id', 'target_type', 'target_id', 'status']

    def filter_by_date_from(self, queryset, name, value):
        """按起始日期过滤"""
        if value:
            start_datetime = timezone.make_aware(
                timezone.datetime.combine(value, timezone.datetime.min.time())
            )
            return queryset.filter(created_at__gte=start_datetime)
        return queryset

    def filter_by_date_to(self, queryset, name, value):
        """按结束日期过滤"""
        if value:
            end_datetime = timezone.make_aware(
                timezone.datetime.combine(value, timezone.datetime.max.time())
            )
            return queryset.filter(created_at__lte=end_datetime)
        return queryset

class TransactionFilter(django_filters.FilterSet):
    # 按订单ID过滤
    order_id = django_filters.NumberFilter(field_name='order_id')
    # 按事件类型过滤
    event = django_filters.CharFilter(field_name='event', lookup_expr='icontains')
    # 按创建日期过滤
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    # 按日期范围过滤
    date_from = django_filters.DateFilter(method='filter_by_date_from')
    date_to = django_filters.DateFilter(method='filter_by_date_to')

    class Meta:
        model = models.Transaction
        fields = ['order_id', 'event']

    def filter_by_date_from(self, queryset, name, value):
        """按起始日期过滤"""
        if value:
            start_datetime = timezone.make_aware(
                timezone.datetime.combine(value, timezone.datetime.min.time())
            )
            return queryset.filter(created_at__gte=start_datetime)
        return queryset

    def filter_by_date_to(self, queryset, name, value):
        """按结束日期过滤"""
        if value:
            end_datetime = timezone.make_aware(
                timezone.datetime.combine(value, timezone.datetime.max.time())
            )
            return queryset.filter(created_at__lte=end_datetime)
        return queryset