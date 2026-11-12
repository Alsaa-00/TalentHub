import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from app.database import Base
from app.models import User, Student, Company, JobListing, Application, ApplicationStatus, Offer
from app.services.offer_service import OfferService
from app.services.eligibility_service import EligibilityService
from app.schemas.offer import OfferCreate
from app.utils.security import hash_password

class TestOfferService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Company & Job
        u_c = User(email="msft@test.com", hashed_password=hash_password("p"), role="company")
        self.db.add(u_c); self.db.flush()
        c = Company(user_id=u_c.id, name="Microsoft")
        self.db.add(c); self.db.flush()
        self.job = JobListing(company_id=c.id, role="SDE 1", package_lpa=24.5, min_cgpa=8.0, max_backlogs=0, drive_date="2026-12-01", season="2026-2027")
        self.db.add(self.job); self.db.flush()

        # Student 1
        u_s = User(email="priya@test.com", hashed_password=hash_password("p"), role="student")
        self.db.add(u_s); self.db.flush()
        self.student = Student(user_id=u_s.id, usn="1MS21CS045", full_name="Priya Nair", email="priya@test.com", branch="CSE", cgpa=9.15, has_accepted_offer=False)
        self.db.add(self.student); self.db.flush()

        # Student 2 (for non-interviewed test)
        u_s2 = User(email="s2@test.com", hashed_password=hash_password("p"), role="student")
        self.db.add(u_s2); self.db.flush()
        self.student2 = Student(user_id=u_s2.id, usn="1MS21CS046", full_name="Student Two", email="s2@test.com", branch="CSE", cgpa=8.0, has_accepted_offer=False)
        self.db.add(self.student2); self.db.flush()

        # Application in INTERVIEWED status (Student 1)
        self.app_interviewed = Application(student_id=self.student.id, job_id=self.job.id, status=ApplicationStatus.INTERVIEWED)
        # Application in APPLIED status (Student 2)
        self.app_applied = Application(student_id=self.student2.id, job_id=self.job.id, status=ApplicationStatus.APPLIED)

        self.db.add(self.app_interviewed)
        self.db.add(self.app_applied)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_refuse_offer_for_non_interviewed_candidate(self):
        # Rule FR-8.1 & FR-8.2: Attempting to issue offer to non-interviewed candidate must be rejected!
        req = OfferCreate(
            application_id=self.app_applied.id,
            designation="SDE 1",
            package_lpa=24.5,
            joining_date="July 2027"
        )
        with self.assertRaises(HTTPException) as cm:
            OfferService.issue_offer(self.db, req)
        self.assertEqual(cm.exception.status_code, 400)
        self.assertIn("must be in INTERVIEWED status", cm.exception.detail)

    def test_issue_offer_and_accept_workflow(self):
        # 1. Issue offer for INTERVIEWED application
        req = OfferCreate(
            application_id=self.app_interviewed.id,
            designation="Software Development Engineer 1",
            package_lpa=24.5,
            joining_date="July 2027"
        )
        offer = OfferService.issue_offer(self.db, req)
        self.assertIsNotNone(offer.id)
        self.assertIsNotNone(offer.offer_letter_key)
        self.assertEqual(self.app_interviewed.status, ApplicationStatus.OFFERED)

        # 2. Student accepts the offer (FR-8.4)
        decided_offer = OfferService.decide_offer(self.db, self.student, offer.id, "ACCEPT")
        self.assertTrue(decided_offer.accepted)
        self.assertEqual(self.app_interviewed.status, ApplicationStatus.ACCEPTED)

        # 3. Student has_accepted_offer flag is updated (FR-8.4)
        self.db.refresh(self.student)
        self.assertTrue(self.student.has_accepted_offer)

        # 4. Student now fails Rule R3 for any future recruitment drives (FR-8.5)
        new_job = JobListing(company_id=1, role="Other Role", min_cgpa=6.0, max_backlogs=0, drive_date="2026-12-10")
        eligibility = EligibilityService.check_eligibility(self.student, new_job)
        self.assertFalse(eligibility.eligible)
        self.assertEqual(eligibility.failed_rule, "R3")
        self.assertIn("Already accepted an offer", eligibility.reason)

if __name__ == "__main__":
    unittest.main()
