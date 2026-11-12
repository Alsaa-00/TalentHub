import unittest
from app.models.student import Student
from app.models.job import JobListing, JobAllowedBranch
from app.services.eligibility_service import EligibilityService

class TestEligibilityService(unittest.TestCase):
    def setUp(self):
        # Base student: Rahul
        self.student = Student(
            id=1,
            usn="1MS21CS001",
            full_name="Rahul Sharma",
            email="rahul@talenthub.edu",
            branch="CSAI",
            cgpa=8.20,
            active_backlogs=0,
            cleared_backlogs=2,
            has_accepted_offer=False,
        )

        # Base pool job: TCS
        self.job = JobListing(
            id=1,
            company_id=1,
            role="Systems Engineer",
            min_cgpa=6.50,
            max_backlogs=0,
            drive_date="2026-11-20",
            is_open=True,
        )

    def test_eligible_student_passes_all_rules(self):
        res = EligibilityService.check_eligibility(self.student, self.job)
        self.assertTrue(res.eligible)
        self.assertIsNone(res.failed_rule)

    def test_rule_r1_cgpa_boundary_cases(self):
        # 6.49 < 6.50 -> INELIGIBLE (Rule R1)
        self.student.cgpa = 6.49
        res = EligibilityService.check_eligibility(self.student, self.job)
        self.assertFalse(res.eligible)
        self.assertEqual(res.failed_rule, "R1")
        self.assertIn("below the required minimum", res.reason)

        # 6.50 >= 6.50 -> ELIGIBLE (Boundary: exact equal qualifies)
        self.student.cgpa = 6.50
        res = EligibilityService.check_eligibility(self.student, self.job)
        self.assertTrue(res.eligible)
        self.assertIsNone(res.failed_rule)

        # 6.51 >= 6.50 -> ELIGIBLE
        self.student.cgpa = 6.51
        res = EligibilityService.check_eligibility(self.student, self.job)
        self.assertTrue(res.eligible)

    def test_rule_r2_active_vs_cleared_backlogs(self):
        # Student with 0 active backlogs and 5 cleared backlogs -> ELIGIBLE (FR-4.4)
        self.student.cgpa = 7.5
        self.student.active_backlogs = 0
        self.student.cleared_backlogs = 5
        self.job.max_backlogs = 0

        res = EligibilityService.check_eligibility(self.student, self.job)
        self.assertTrue(res.eligible)

        # Student with 1 active backlog when max allowed is 0 -> INELIGIBLE (Rule R2)
        self.student.active_backlogs = 1
        res = EligibilityService.check_eligibility(self.student, self.job)
        self.assertFalse(res.eligible)
        self.assertEqual(res.failed_rule, "R2")
        self.assertIn("Active backlogs", res.reason)

    def test_rule_r3_one_company_accepted_offer(self):
        # Student who has accepted an offer from another company this season -> INELIGIBLE (Rule R3)
        self.student.cgpa = 8.5
        self.student.active_backlogs = 0
        self.student.has_accepted_offer = True

        res = EligibilityService.check_eligibility(self.student, self.job)
        self.assertFalse(res.eligible)
        self.assertEqual(res.failed_rule, "R3")
        self.assertIn("Already accepted an offer", res.reason)

    def test_rule_r4_branch_restrictions_and_pool_drive(self):
        self.student.branch = "MECH"
        self.student.cgpa = 8.0
        self.student.active_backlogs = 0
        self.student.has_accepted_offer = False

        # Empty allowed_branches = Pool drive open to all branches -> ELIGIBLE
        res_pool = EligibilityService.check_eligibility(self.student, self.job)
        self.assertTrue(res_pool.eligible)

        # Non-empty allowed_branches acting as whitelist: ['CSE', 'CSAI']
        # MECH student -> INELIGIBLE (Rule R4)
        self.job.allowed_branches_rel = [
            JobAllowedBranch(job_id=1, branch="CSE"),
            JobAllowedBranch(job_id=1, branch="CSAI"),
        ]

        res_branch = EligibilityService.check_eligibility(self.student, self.job)
        self.assertFalse(res_branch.eligible)
        self.assertEqual(res_branch.failed_rule, "R4")
        self.assertIn("Branch 'MECH' is not in the drive scope", res_branch.reason)

if __name__ == "__main__":
    unittest.main()
