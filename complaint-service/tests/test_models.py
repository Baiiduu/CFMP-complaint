# complaint-service/tests/test_models.py
from django.test import TestCase
from complaint.models import Complaint, ComplaintReview, Transaction
import uuid


class ComplaintModelTest(TestCase):
    def setUp(self):
        self.complaint_data = {
            'complainer_id': uuid.uuid4(),
            'target_type': 0,
            'target_id': uuid.uuid4(),
            'reason': '测试投诉原因',
            'status': 0
        }
        self.complaint = Complaint.objects.create(**self.complaint_data)

    def test_complaint_creation(self):
        """测试投诉创建"""
        self.assertEqual(self.complaint.complainer_id, self.complaint_data['complainer_id'])
        self.assertEqual(self.complaint.target_type, self.complaint_data['target_type'])
        self.assertEqual(self.complaint.target_id, self.complaint_data['target_id'])
        self.assertEqual(self.complaint.reason, self.complaint_data['reason'])
        self.assertEqual(self.complaint.status, self.complaint_data['status'])
        self.assertIsNotNone(self.complaint.created_at)


    def test_complaint_ordering(self):
        """测试投诉按创建时间倒序排列"""
        complaint2 = Complaint.objects.create(
            complainer_id=uuid.uuid4(),
            target_type=1,
            target_id=uuid.uuid4(),
            reason='第二个投诉'
        )
        complaints = Complaint.objects.all()
        self.assertGreater(complaints[0].created_at, complaints[1].created_at)


class ComplaintReviewModelTest(TestCase):
    def setUp(self):
        self.review_data = {
            'target_id': uuid.uuid4(),
            'target_type': 0,
            'reviewer_id': uuid.uuid4(),
            'result': 'approved',
            'ban_type': 'temporary',
            'ban_time': 7
        }
        self.review = ComplaintReview.objects.create(**self.review_data)

    def test_review_creation(self):
        """测试审核创建"""
        self.assertEqual(self.review.target_id, self.review_data['target_id'])
        self.assertEqual(self.review.target_type, self.review_data['target_type'])
        self.assertEqual(self.review.reviewer_id, self.review_data['reviewer_id'])
        self.assertEqual(self.review.result, self.review_data['result'])
        self.assertEqual(self.review.ban_type, self.review_data['ban_type'])
        self.assertEqual(self.review.ban_time, self.review_data['ban_time'])
        self.assertIsNotNone(self.review.created_at)

