from typing import Optional, List
from app.models.student import Student
from app.models.job import JobListing
from app.schemas.eligibility import EligibilityResult

class EligibilityService:
    """
    Evaluates campus placement eligibility rules R1 to R4 in strict order:
    R1: CGPA >= min_cgpa (equal qualifies, FR-4.3)
    R2: active_backlogs <= max_backlogs (cleared backlogs ignored, FR-4.4)
    R3: has_accepted_offer is False (one-company rule season-wide)
    R4: allowed_branches is empty (pool drive) OR contains student.branch
    """

    @staticmethod
    def check_eligibility(student: Student, job: JobListing) -> EligibilityResult:
        allowed = [b.upper() for b in job.allowed_branches] if job.allowed_branches else []
        student_branch = (student.branch or "").strip().upper()

        # Rule R1: CGPA check (Boundary: equal qualifies >=)
        # Rounding to 2 decimal places for floating comparison
        if round(student.cgpa, 2) < round(job.min_cgpa, 2):
            return EligibilityResult(
                eligible=False,
                reason=f"CGPA {student.cgpa:.2f} is below the required minimum of {job.min_cgpa:.2f}",
                failed_rule="R1",
                min_cgpa=job.min_cgpa,
                max_backlogs=job.max_backlogs,
                allowed_branches=allowed,
                student_cgpa=student.cgpa,
                student_backlogs=student.active_backlogs,
                student_branch=student_branch,
                student_has_offer=student.has_accepted_offer,
            )

        # Rule R2: Active backlogs check (Cleared backlogs are tracked separately and do not disqualify)
        if student.active_backlogs > job.max_backlogs:
            return EligibilityResult(
                eligible=False,
                reason=f"Active backlogs ({student.active_backlogs}) exceed the maximum allowed ({job.max_backlogs})",
                failed_rule="R2",
                min_cgpa=job.min_cgpa,
                max_backlogs=job.max_backlogs,
                allowed_branches=allowed,
                student_cgpa=student.cgpa,
                student_backlogs=student.active_backlogs,
                student_branch=student_branch,
                student_has_offer=student.has_accepted_offer,
            )

        # Rule R3: One-company accepted offer rule
        if student.has_accepted_offer:
            return EligibilityResult(
                eligible=False,
                reason="Already accepted an offer from another company this season",
                failed_rule="R3",
                min_cgpa=job.min_cgpa,
                max_backlogs=job.max_backlogs,
                allowed_branches=allowed,
                student_cgpa=student.cgpa,
                student_backlogs=student.active_backlogs,
                student_branch=student_branch,
                student_has_offer=student.has_accepted_offer,
            )

        # Rule R4: Branch eligibility (Empty whitelist means pool drive - all branches allowed)
        if len(allowed) > 0 and student_branch not in allowed:
            allowed_str = ", ".join(allowed)
            return EligibilityResult(
                eligible=False,
                reason=f"Branch '{student_branch}' is not in the drive scope (Eligible: {allowed_str})",
                failed_rule="R4",
                min_cgpa=job.min_cgpa,
                max_backlogs=job.max_backlogs,
                allowed_branches=allowed,
                student_cgpa=student.cgpa,
                student_backlogs=student.active_backlogs,
                student_branch=student_branch,
                student_has_offer=student.has_accepted_offer,
            )

        # All rules passed
        return EligibilityResult(
            eligible=True,
            reason="All eligibility criteria satisfied (CGPA, Backlogs, One-Offer policy, Branch match)",
            failed_rule=None,
            min_cgpa=job.min_cgpa,
            max_backlogs=job.max_backlogs,
            allowed_branches=allowed,
            student_cgpa=student.cgpa,
            student_backlogs=student.active_backlogs,
            student_branch=student_branch,
            student_has_offer=student.has_accepted_offer,
        )
