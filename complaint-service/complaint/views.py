import django_filters
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView
from rest_framework.decorators import api_view, action
from rest_framework import generics, mixins, viewsets, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from . import models
from . import serializers
from rest_framework.views import APIView
from .permissions import IsAdminUser
from .service_client import ServiceClient




class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000 # test

class StandartView(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        list = super().list(request, *args, **kwargs)

       # user_result = ServiceClient.get("OrderService", f"/api/orders/")
       # print("用户9999999999999999")
       # print(user_result)

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

    queryset = models.Complaint.objects.all()
    serializer_class = serializers.ComplaintSerializer
    lookup_field = 'complaint_id'
    pagination_class = StandardPagination
    permission_classes = [IsAdminUser]


    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['complaint_id','target_id','target_type','status','complainer_id']
    ordering_fields = ['created_at']

    @action(methods=['patch'], detail=False, url_path='branch/(?P<target_type>\w+)/(?P<target_id>[^/]+)', url_name='branch')
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


class ComplaintUserView(StandartView):
    queryset = models.Complaint.objects.all()
    serializer_class = serializers.ComplaintSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        complainer_id=request.headers.get('UUID')
        complaint_data = request.data

        # 创建 Complaint 实例但不保存到数据库
        complaint = models.Complaint(
            target_type=complaint_data.get('target_type'),
            target_id=complaint_data.get('target_id'),
            reason=complaint_data.get('reason'),
            complainer_id=complainer_id
        )

        # 手动保存到数据库
        complaint.save()
        serializer = self.get_serializer(complaint)

        return Response({
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class ComplaintReviewView(StandartView):

    queryset = models.ComplaintReview.objects.all()
    serializer_class = serializers.ComplaintReviewSerializer
    lookup_field = 'review_id'
    pagination_class = StandardPagination
    permission_classes = [IsAdminUser]


    # filter_class = ComplaintReviewFilter
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['target_id', 'target_type','reviewer_id']
    ordering_fields = ['created_at']

    def create(self, request, *args, **kwargs):
        # 从请求头获取审核员ID
        reviewer_id = request.headers.get('UUID')
        if not reviewer_id:
            return Response({
                'detail': '缺少审核员ID (UUID header)'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 从请求体获取数据
        review_data = request.data
        # 创建 ComplaintReview 实例
        review = models.ComplaintReview(
            target_id=review_data.get('target_id'),
            target_type=review_data.get('target_type'),
            reviewer_id=reviewer_id,
            result=review_data.get('result'),
            ban_type=review_data.get('ban_type'),
            ban_time=review_data.get('ban_time')
        )

        # 保存到数据库
        review.save()
        serializer = self.get_serializer(review)

        return Response({
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)



class TransactionViewSet(viewsets.ModelViewSet):
    queryset = models.Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer
    filter_backends = [DjangoFilterBackend]
    ordering_fields = ['created_at']
    lookup_field = 'log_id'


