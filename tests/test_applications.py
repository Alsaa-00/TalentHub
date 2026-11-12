import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from app.database import Base
from app.models import User, Student, Company, JobListing, Application, ApplicationStatus
from app.services.application_service import ApplicationService
from app.repositories.job_repository import JobRepository
from app.utils.security import hash_password

class TestApplicationService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Create company
        user_c = User(email="cmp@test.com", hashed_password=hash_password("test"), role="company")
        self.db.add(user_c)
        self.db.flush()
        self.company = Company(user_id=user_c.id, name="Test Corp")
        self.db.add(self.company)
        self.db.flush()

        # Create Job
        self.job = JobListing(
            company_id=self.company.id,
            role="Dev",
            package_lpa=8.0,
            min_cgpa=7.0,
            max_backlogs=0,
            drive_date="2026-12-01",
            is_open=True,
            season="2026-2027"
        )
        JobRepository.create(self.db, self.job, branches=["CSE"])

        # Eligible Student
        user_s1 = User(email="s1@test.com", hashed_password=hash_password("test"), role="student")
        self.db.add(user_s1)
        self.db.flush()
        self.student_eligible = Student(
            user_id=user_s1.id,
            usn="1MS21CS001",
            full_name="Eligible Student",
            email="s1@test.com",
            branch="CSE",
            cgpa=8.0,
            active_backlogs=0,
            has_accepted_offer=False
        )
        self.db.add(self.student_eligible)

        # Ineligible Student (Low CGPA)
        user_s2 = User(email="s2@test.com", hashed_password=hash_password("test"), role="student")
        self.db.add(user_s2)
        self.db.flush()
        self.student_ineligible = Student(
            user_id=user_s2.id,
            usn="1MS21CS002",
            full_name="Ineligible Student",
            email="s2@test.com",
            branch="CSE",
            cgpa=6.2,  # Below 7.0
            active_backlogs=0,
            has_accepted_offer=False
        )
        self.db.add(self.student_ineligible)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_eligible_student_applies_successfully(self):
        app = ApplicationService.apply_for_job(self.db, self.student_eligible, self.job.id)
        self.assertIsNotNone(app.id)
        self.assertEqual(app.status, ApplicationStatus.APPLIED)
        self.assertEqual(app.student_id, self.student_eligible.id)

    def test_ineligible_student_application_rejected(self):
        with self.assertRaises(HTTPException) as cm:
            ApplicationService.apply_for_job(self.db, self.student_ineligible, self.job.id)
        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("Eligibility check failed", cm.exception.detail)

    def test_duplicate_application_rejected(self):
        # First application succeeds
        ApplicationService.apply_for_job(self.db, self.student_eligible, self.job.id)

        # Second application should be rejected
        with self.assertRaises(HTTPException) as cm:
            ApplicationService.apply_for_job(self.db, self.student_eligible, self.job.id)
        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("already submitted an application", cm.exception.detail)

if __name__ == "__main__":
    unittest.main()
