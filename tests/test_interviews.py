import unittest
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from app.database import Base
from app.models import User, Student, Company, JobListing, Application, ApplicationStatus, InterviewSlot
from app.services.interview_service import InterviewService
from app.schemas.interview import InterviewSlotCreate, InterviewSlotUpdate
from app.utils.security import hash_password

class TestInterviewService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Company & Job
        u_c = User(email="c@t.com", hashed_password=hash_password("p"), role="company")
        self.db.add(u_c); self.db.flush()
        c = Company(user_id=u_c.id, name="Google")
        self.db.add(c); self.db.flush()
        j = JobListing(company_id=c.id, role="SWE", package_lpa=30.0, min_cgpa=8.0, max_backlogs=0, drive_date="2026-11-20")
        self.db.add(j); self.db.flush()

        # Student & Application
        u_s = User(email="s@t.com", hashed_password=hash_password("p"), role="student")
        self.db.add(u_s); self.db.flush()
        s = Student(user_id=u_s.id, usn="1MS21CS001", full_name="Student One", email="s@t.com", branch="CSE", cgpa=9.0)
        self.db.add(s); self.db.flush()

        self.app = Application(student_id=s.id, job_id=j.id, status=ApplicationStatus.SHORTLISTED)
        self.db.add(self.app)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_schedule_interview_transitions_status(self):
        req = InterviewSlotCreate(
            application_id=self.app.id,
            round_no=1,
            round_name="Coding Round",
            scheduled_at=datetime.now(timezone.utc) + timedelta(days=2),
            venue="Lab 3",
            notes="Bring Laptop"
        )

        slot = InterviewService.schedule_interview(self.db, req)
        self.assertIsNotNone(slot.id)
        self.assertEqual(slot.round_no, 1)

        # Application status should be updated to INTERVIEW_SCHEDULED
        self.db.refresh(self.app)
        self.assertEqual(self.app.status, ApplicationStatus.INTERVIEW_SCHEDULED)

    def test_record_passed_result_transitions_to_interviewed(self):
        req = InterviewSlotCreate(
            application_id=self.app.id,
            round_no=1,
            round_name="System Design",
            scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
            venue="Google Meet"
        )
        slot = InterviewService.schedule_interview(self.db, req)

        # Record pass
        update_req = InterviewSlotUpdate(passed=True, notes="Excellent design skills.")
        InterviewService.record_result(self.db, slot.id, update_req)

        self.db.refresh(slot)
        self.db.refresh(self.app)
        self.assertTrue(slot.passed)
        self.assertEqual(self.app.status, ApplicationStatus.INTERVIEWED)

if __name__ == "__main__":
    unittest.main()
