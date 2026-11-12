import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Student, Company, JobListing, Application, ApplicationStatus
from app.services.application_service import ApplicationService
from app.repositories.job_repository import JobRepository
from app.utils.security import hash_password

class TestShortlistingService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Company
        user_c = User(email="tcs@test.com", hashed_password=hash_password("test"), role="company")
        self.db.add(user_c)
        self.db.flush()
        self.company = Company(user_id=user_c.id, name="TCS")
        self.db.add(self.company)
        self.db.flush()

        # Job with Min CGPA 6.50
        self.job = JobListing(
            company_id=self.company.id,
            role="Systems Engineer",
            package_lpa=7.0,
            min_cgpa=6.50,
            max_backlogs=0,
            drive_date="2026-11-25",
            is_open=True,
            season="2026-2027"
        )
        JobRepository.create(self.db, self.job, branches=[])  # Pool drive

        # Student 1: CGPA 6.50 (Exact boundary - passes!)
        u1 = User(email="s1@test.com", hashed_password=hash_password("p"), role="student")
        self.db.add(u1); self.db.flush()
        self.s1 = Student(user_id=u1.id, usn="1MS21CS001", full_name="Boundary S1", email="s1@test.com", branch="CSE", cgpa=6.50, active_backlogs=0)
        self.db.add(self.s1)

        # Student 2: CGPA 6.40 (Below 6.50 - fails!)
        u2 = User(email="s2@test.com", hashed_password=hash_password("p"), role="student")
        self.db.add(u2); self.db.flush()
        self.s2 = Student(user_id=u2.id, usn="1MS21CS002", full_name="Failing S2", email="s2@test.com", branch="CSE", cgpa=6.40, active_backlogs=0)
        self.db.add(self.s2)

        self.db.flush()

        # Both have submitted applications in APPLIED state
        self.app1 = Application(student_id=self.s1.id, job_id=self.job.id, status=ApplicationStatus.APPLIED)
        self.app2 = Application(student_id=self.s2.id, job_id=self.job.id, status=ApplicationStatus.APPLIED)
        self.db.add(self.app1)
        self.db.add(self.app2)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_batch_shortlist_run(self):
        # Run shortlisting batch
        res = ApplicationService.shortlist_students(self.db, self.job.id)

        self.assertEqual(res.total_processed, 2)
        self.assertEqual(res.shortlisted_count, 1)
        self.assertEqual(res.ineligible_count, 1)

        # Verify DB state
        self.db.refresh(self.app1)
        self.db.refresh(self.app2)

        self.assertEqual(self.app1.status, ApplicationStatus.SHORTLISTED)
        self.assertIsNone(self.app1.ineligibility_reason)

        self.assertEqual(self.app2.status, ApplicationStatus.REJECTED)
        self.assertIsNotNone(self.app2.ineligibility_reason)
        self.assertIn("below the required minimum", self.app2.ineligibility_reason)

    def test_shortlist_idempotency(self):
        # First run
        ApplicationService.shortlist_students(self.db, self.job.id)

        # Second run should give consistent results (already shortlisted tracked)
        res2 = ApplicationService.shortlist_students(self.db, self.job.id)
        self.assertEqual(res2.shortlisted_count, 0)
        self.assertEqual(res2.already_shortlisted_count, 1)

if __name__ == "__main__":
    unittest.main()
