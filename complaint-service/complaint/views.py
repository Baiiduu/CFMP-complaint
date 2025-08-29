from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from . import models, serializers, filters as complaint_filters
from .permissions import IsAuthenticated, IsAdminUser, IsComplaintOwner
from .service_client import ServiceClient
import logging


logger = logging.getLogger(__name__)
class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000 # test

class StandartView(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        list = super().list(request, *args, **kwargs)
        return Response({'data': list.data})

    def retrieve(self, request, *args, **kwargs):#带路径参数的查询#123
        retrieve = super().retrieve(request, *args, **kwargs)
        return Response({'data': retrieve.data})

    def create(self, request, *args, **kwargs):
        create = super().create(request, *args, **kwargs)
        return Response({'data': create.data})

    def update(self, request, *args, **kwargs):
        update = super().update(request, *args, **kwargs)
        return Response({'data': update.data})

class ComplaintView(StandartView):
    permission_classes = [IsAdminUser]
    queryset = models.Complaint.objects.all()
    serializer_class = serializers.ComplaintSerializer
    lookup_field = 'complaint_id'
    pagination_class = StandardPagination


    filter_backends = [DjangoFilterBackend,filters.OrderingFilter]
    filterset_fields = ['complainer_id','target_id','target_type','status','complainer_id']
    ordering_fields = ['created_at']

    @action(methods=['patch'], detail=False, url_path='branch/(?P<target_type>\w+)/(?P<target_id>\d+)', url_name='branch')
    def branch_update(self, request,target_type, target_id):
        queryset = self.get_queryset().filter(
            target_type=target_type,
            target_id=target_id
        )
        if not queryset.exists():
            return Response({'detail':'没有对应的举报'},status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer()
        for complaint in queryset:
            serializer = self.get_serializer(complaint, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

        return Response(status=status.HTTP_202_ACCEPTED)




class ComplaintReviewView(StandartView):
    permission_classes = [IsAdminUser]
    queryset = models.ComplaintReview.objects.all()
    serializer_class = serializers.ComplaintReviewSerializer
    lookup_field = 'review_id'
    pagination_class = StandardPagination

    # filter_class = ComplaintReviewFilter
    filter_backends = [DjangoFilterBackend,filters.OrderingFilter]
    filterset_fields = ['target_id', 'target_type','reviewer_id']
    ordering_fields = ['created_at']



class TransactionViewSet(viewsets.ModelViewSet):
    queryset = models.Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = complaint_filters.TransactionFilter
    ordering_fields = ['created_at']
    lookup_field = 'log_id'
