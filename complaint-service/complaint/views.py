from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from . import models, serializers, filters as complaint_filters

class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = models.Complaint.objects.all()
    serializer_class = serializers.ComplaintSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = complaint_filters.ComplaintFilter  # 使用自定义过滤器类
    ordering_fields = ['created_at']
    lookup_field = 'complaint_id'

    @action(detail=False, methods=['get'])
    def by_user(self, request):
        user_id = request.query_params.get('user_id')
        complaints = self.queryset.filter(complainer_id=user_id)
        serializer = self.get_serializer(complaints, many=True)
        return Response(serializer.data)

class ComplaintReviewViewSet(viewsets.ModelViewSet):
    queryset = models.ComplaintReview.objects.all()
    serializer_class = serializers.ComplaintReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = complaint_filters.ComplaintReviewFilter
    ordering_fields = ['created_at']
    lookup_field = 'review_id'

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = models.Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = complaint_filters.TransactionFilter
    ordering_fields = ['created_at']
    lookup_field = 'log_id'