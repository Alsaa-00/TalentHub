import io
import csv
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.config import CURRENT_SEASON
from app.models.student import Student
from app.models.company import Company
from app.models.job import JobListing
from app.models.application import Application, ApplicationStatus
from app.models.interview import InterviewSlot
from app.models.offer import Offer
from app.repositories.student_repository import StudentRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.job_repository import JobRepository
from app.repositories.application_repository import ApplicationRepository
from app.repositories.interview_repository import InterviewRepository
from app.repositories.offer_repository import OfferRepository
from app.schemas.dashboard import StudentDashboardOut, CompanyDashboardOut, AdminDashboardOut
from app.schemas.reports import PlacementStatisticsOut, PlacedStudentOut, BranchStatistics
from app.services.interview_service import InterviewService
from app.services.offer_service import OfferService

class ReportService:
    @staticmethod
    def get_student_dashboard(db: Session, student: Student) -> StudentDashboardOut:
        all_jobs = JobRepository.get_all(db, is_open=True)
        from app.services.eligibility_service import EligibilityService
        eligible_count = sum(1 for j in all_jobs if EligibilityService.check_eligibility(student, j).eligible)

        apps = ApplicationRepository.get_by_student(db, student.id)
        interviews = InterviewRepository.get_by_student(db, student.id)
        offers = OfferRepository.get_by_student(db, student.id)

        formatted_interviews = [InterviewService.format_interview_out(i) for i in interviews[:5]]
        formatted_offers = [OfferService.format_offer_out(o) for o in offers]

        return StudentDashboardOut(
            student_id=student.id,
            full_name=student.full_name,
            usn=student.usn,
            branch=student.branch,
            cgpa=student.cgpa,
            active_backlogs=student.active_backlogs,
            has_accepted_offer=student.has_accepted_offer,
            total_eligible_jobs=eligible_count,
            total_applications=len(apps),
            total_interviews=len(interviews),
            total_offers=len(offers),
            recent_applications=apps[:5],
            upcoming_interviews=formatted_interviews,
            received_offers=formatted_offers,
        )

    @staticmethod
    def get_company_dashboard(db: Session, company: Company) -> CompanyDashboardOut:
        jobs = JobRepository.get_by_company(db, company.id)
        job_ids = [j.id for j in jobs]

        total_applicants = 0
        total_shortlisted = 0
        total_interviews = 0
        total_offers_issued = 0
        total_offers_accepted = 0

        if job_ids:
            total_applicants = db.query(Application).filter(Application.job_id.in_(job_ids)).count()
            total_shortlisted = db.query(Application).filter(
                Application.job_id.in_(job_ids),
                Application.status.in_([
                    ApplicationStatus.SHORTLISTED,
                    ApplicationStatus.INTERVIEW_SCHEDULED,
                    ApplicationStatus.INTERVIEWED,
                    ApplicationStatus.OFFERED,
                    ApplicationStatus.ACCEPTED
                ])
            ).count()
            total_interviews = db.query(InterviewSlot).join(Application).filter(Application.job_id.in_(job_ids)).count()
            offers = db.query(Offer).join(Application).filter(Application.job_id.in_(job_ids)).all()
            total_offers_issued = len(offers)
            total_offers_accepted = sum(1 for o in offers if o.accepted)

        return CompanyDashboardOut(
            company_id=company.id,
            company_name=company.name,
            total_jobs=len(jobs),
            total_applicants=total_applicants,
            total_shortlisted=total_shortlisted,
            total_interviews_scheduled=total_interviews,
            total_offers_issued=total_offers_issued,
            total_offers_accepted=total_offers_accepted,
            recent_jobs=jobs[:5],
        )

    @staticmethod
    def get_admin_dashboard(db: Session) -> AdminDashboardOut:
        total_students = StudentRepository.count(db)
        total_placed = StudentRepository.count_placed(db)
        placement_pct = round((total_placed / total_students * 100), 1) if total_students > 0 else 0.0

        total_companies = CompanyRepository.count(db)
        total_jobs = JobRepository.count(db)
        total_apps = ApplicationRepository.count(db)
        status_counts = ApplicationRepository.count_by_status(db)
        total_shortlisted = status_counts.get(ApplicationStatus.SHORTLISTED, 0)
        total_interviews = InterviewRepository.count(db)
        total_offers = OfferRepository.count(db)

        # Branch-wise placed count
        branch_stats = db.query(
            Student.branch, func.count(Student.id)
        ).filter(Student.has_accepted_offer.is_(True)).group_by(Student.branch).all()
        branch_placed_dict = {b: count for b, count in branch_stats}

        # Package statistics from accepted offers
        accepted_offers = db.query(Offer).filter(Offer.accepted.is_(True)).all()
        packages = [o.package_lpa for o in accepted_offers]
        avg_package = round(sum(packages) / len(packages), 2) if packages else 0.0
        highest_package = max(packages) if packages else 0.0

        return AdminDashboardOut(
            total_students=total_students,
            total_companies=total_companies,
            total_jobs=total_jobs,
            total_applications=total_apps,
            total_shortlisted=total_shortlisted,
            total_interviews=total_interviews,
            total_offers=total_offers,
            total_placed_students=total_placed,
            placement_percentage=placement_pct,
            average_package_lpa=avg_package,
            highest_package_lpa=highest_package,
            branch_wise_placed=branch_placed_dict,
            season=CURRENT_SEASON,
        )

    @staticmethod
    def get_placement_statistics(db: Session) -> PlacementStatisticsOut:
        total_students = StudentRepository.count(db)
        total_placed = StudentRepository.count_placed(db)
        placement_pct = round((total_placed / total_students * 100), 1) if total_students > 0 else 0.0

        total_companies = CompanyRepository.count(db)
        total_jobs = JobRepository.count(db)
        total_apps = ApplicationRepository.count(db)
        total_offers = OfferRepository.count(db)
        total_accepted = OfferRepository.count_accepted(db)
        status_distribution = ApplicationRepository.count_by_status(db)

        # Offer packages
        accepted_offers = db.query(Offer).filter(Offer.accepted.is_(True)).all()
        packages = [o.package_lpa for o in accepted_offers]
        avg_pkg = round(sum(packages) / len(packages), 2) if packages else 0.0
        max_pkg = max(packages) if packages else 0.0
        min_pkg = min(packages) if packages else 0.0

        # Branch breakdown
        branches = db.query(Student.branch).distinct().all()
        branch_list = [b[0] for b in branches if b[0]]

        breakdown = []
        for br in sorted(branch_list):
            st_count = db.query(Student).filter(Student.branch == br).count()
            pl_count = db.query(Student).filter(Student.branch == br, Student.has_accepted_offer.is_(True)).count()
            pct = round((pl_count / st_count * 100), 1) if st_count > 0 else 0.0

            # Packages for branch
            br_offers = db.query(Offer).join(Application).join(Student).filter(
                Student.branch == br, Offer.accepted.is_(True)
            ).all()
            br_pkgs = [o.package_lpa for o in br_offers]
            br_avg = round(sum(br_pkgs) / len(br_pkgs), 2) if br_pkgs else 0.0
            br_max = max(br_pkgs) if br_pkgs else 0.0

            breakdown.append(BranchStatistics(
                branch=br,
                total_students=st_count,
                placed_students=pl_count,
                placement_percentage=pct,
                average_package_lpa=br_avg,
                highest_package_lpa=br_max,
            ))

        return PlacementStatisticsOut(
            season=CURRENT_SEASON,
            total_registered_students=total_students,
            total_placed_students=total_placed,
            overall_placement_percentage=placement_pct,
            total_companies_visiting=total_companies,
            total_jobs_posted=total_jobs,
            total_applications=total_apps,
            total_offers_issued=total_offers,
            total_offers_accepted=total_accepted,
            average_package_lpa=avg_pkg,
            highest_package_lpa=max_pkg,
            lowest_package_lpa=min_pkg,
            branch_breakdown=breakdown,
            status_distribution=status_distribution,
        )

    @staticmethod
    def get_placed_students(db: Session) -> List[PlacedStudentOut]:
        accepted_offers = db.query(Offer).filter(Offer.accepted.is_(True)).all()
        results = []
        for o in accepted_offers:
            app = o.application
            st = app.student if app else None
            jb = app.job if app else None
            cmp = jb.company if jb else None

            if st and jb and cmp:
                results.append(PlacedStudentOut(
                    student_id=st.id,
                    usn=st.usn,
                    full_name=st.full_name,
                    branch=st.branch,
                    cgpa=st.cgpa,
                    company_name=cmp.name,
                    job_role=jb.role,
                    package_lpa=o.package_lpa,
                    offer_letter_key=o.offer_letter_key,
                    accepted_date=o.decision_at or o.issued_at,
                ))
        return results

    @staticmethod
    def export_job_shortlist_csv(db: Session, job_id: int) -> str:
        """FR-9.3: Export the shortlist of a drive as a CSV file."""
        job = JobRepository.get_by_id(db, job_id)
        if not job:
            raise Exception("Job not found")

        apps = ApplicationRepository.get_by_job(db, job_id)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["USN", "Student Name", "Email", "Branch", "CGPA", "Active Backlogs", "Application Status", "Applied Date"])

        for app in apps:
            st = app.student
            writer.writerow([
                st.usn,
                st.full_name,
                st.email,
                st.branch,
                st.cgpa,
                st.active_backlogs,
                app.status,
                app.applied_at.strftime("%Y-%m-%d %H:%M:%S") if app.applied_at else "",
            ])

        return output.getvalue()
