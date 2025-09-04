# complaint-service/tests/test_serializers.py
from django.test import TestCase
from complaint.models import Complaint, ComplaintReview, Transaction
from complaint.serializers import (
    ComplaintSerializer,
    ComplaintReviewSerializer,
    TransactionSerializer
)
import uuid


class ComplaintSerializerTest(TestCase):
    def setUp(self):
        self.complaint_attributes = {
            'complainer_id': uuid.uuid4(),
            'target_type': 0,
            'target_id': uuid.uuid4(),
            'reason': '测试投诉原因',
            'status': 0
        }

    def test_complaint_serializer_valid_data(self):
        """测试投诉序列化器处理有效数据"""
        serializer = ComplaintSerializer(data=self.complaint_attributes)
        self.assertTrue(serializer.is_valid())
        complaint = serializer.save()
        self.assertEqual(complaint.complainer_id, self.complaint_attributes['complainer_id'])
        self.assertEqual(complaint.reason, self.complaint_attributes['reason'])

    def test_complaint_serializer_contains_expected_fields(self):
        """测试投诉序列化器包含预期字段"""
        complaint = Complaint.objects.create(**self.complaint_attributes)
        serializer = ComplaintSerializer(complaint)
        expected_fields = [
            'complaint_id', 'complainer_id', 'target_type', 'target_id',
            'reason', 'created_at', 'status'
        ]
        for field in expected_fields:
            self.assertIn(field, serializer.data)


class ComplaintReviewSerializerTest(TestCase):
    def setUp(self):
        self.review_data = {
            'target_id': uuid.uuid4(),
            'target_type': 0,
            'reviewer_id': uuid.uuid4(),
            'result': 'approved',
            'ban_type': 'temporary',
            'ban_time': 7
        }

    def test_review_serializer_valid_data(self):
        """测试审核序列化器处理有效数据"""
        serializer = ComplaintReviewSerializer(data=self.review_data)
        self.assertTrue(serializer.is_valid())
        review = serializer.save()
        self.assertEqual(review.target_id, self.review_data['target_id'])
        self.assertEqual(review.result, self.review_data['result'])

    def test_review_serializer_contains_expected_fields(self):
        """测试审核序列化器包含预期字段"""
        review = ComplaintReview.objects.create(**self.review_data)
        serializer = ComplaintReviewSerializer(review)
        expected_fields = [
            'review_id', 'target_id', 'target_type', 'reviewer_id',
            'created_at', 'result', 'ban_type', 'ban_time'
        ]
        for field in expected_fields:
            self.assertIn(field, serializer.data)

