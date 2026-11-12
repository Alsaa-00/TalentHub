from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.student import Student
from app.models.company import Company
from app.models.job import JobListing, JobAllowedBranch
from app.models.application import Application, ApplicationStatus
from app.models.interview import InterviewSlot
from app.models.offer import Offer
from app.utils.security import hash_password
from app.config import CURRENT_SEASON

def seed_database(db: Session) -> dict:
    """Populates realistic seed data for college demonstration."""
    # 1. Clean existing tables in reverse dependency order
    db.query(Offer).delete()
    db.query(InterviewSlot).delete()
    db.query(Application).delete()
    db.query(JobAllowedBranch).delete()
    db.query(JobListing).delete()
    db.query(Company).delete()
    db.query(Student).delete()
    db.query(User).delete()
    db.commit()

    now = datetime.now(timezone.utc)

    # 2. Placement Coordinator / Admin
    admin_user = User(
        email="admin@talenthub.edu",
        hashed_password=hash_password("AdminPassword123!"),
        role="admin",
        is_active=True,
    )
    db.add(admin_user)
    db.commit()

    # 3. Companies
    companies_data = [
        {
            "email": "campus@tcs.com",
            "password": "CompanyPass123!",
            "name": "Tata Consultancy Services (TCS)",
            "description": "Global leader in IT services, consulting, and business solutions.",
            "website": "https://www.tcs.com",
            "location": "Bengaluru / Mumbai",
            "industry": "Information Technology",
        },
        {
            "email": "university@microsoft.com",
            "password": "CompanyPass123!",
            "name": "Microsoft Corporation",
            "description": "Global technology innovator empowering every person and organization.",
            "website": "https://www.microsoft.com",
            "location": "Bengaluru / Hyderabad",
            "industry": "Software & Cloud",
        },
        {
            "email": "careers@infosys.com",
            "password": "CompanyPass123!",
            "name": "Infosys Limited",
            "description": "Next-generation digital services and consulting leader.",
            "website": "https://www.infosys.com",
            "location": "Bengaluru / Pune",
            "industry": "IT & Digital Services",
        },
        {
            "email": "recruiting@google.com",
            "password": "CompanyPass123!",
            "name": "Google",
            "description": "Organizing the world's information and making it universally accessible.",
            "website": "https://careers.google.com",
            "location": "Bengaluru / Hyderabad",
            "industry": "Internet & AI",
        },
    ]

    company_objs = {}
    for cd in companies_data:
        u = User(
            email=cd["email"],
            hashed_password=hash_password(cd["password"]),
            role="company",
            is_active=True,
        )
        db.add(u)
        db.flush()
        c = Company(
            user_id=u.id,
            name=cd["name"],
            description=cd["description"],
            website=cd["website"],
            contact_email=cd["email"],
            location=cd["location"],
            industry=cd["industry"],
        )
        db.add(c)
        db.flush()
        company_objs[cd["name"]] = c

    # 4. Students
    students_data = [
        {
            "email": "rahul.sharma@talenthub.edu",
            "password": "StudentPass123!",
            "usn": "1MS21CS001",
            "full_name": "Rahul Sharma",
            "branch": "CSAI",
            "cgpa": 8.20,
            "active_backlogs": 0,
            "cleared_backlogs": 1,
            "phone": "+91 98765 43210",
            "skills": "Python, PyTorch, SQL, FastAPI, Docker",
            "has_accepted_offer": False,
        },
        {
            "email": "priya.nair@talenthub.edu",
            "password": "StudentPass123!",
            "usn": "1MS21CS045",
            "full_name": "Priya Nair",
            "branch": "CSE",
            "cgpa": 9.15,
            "active_backlogs": 0,
            "cleared_backlogs": 0,
            "phone": "+91 98765 43211",
            "skills": "C++, Algorithms, Distributed Systems, Go",
            "has_accepted_offer": True,
        },
        {
            "email": "amit.verma@talenthub.edu",
            "password": "StudentPass123!",
            "usn": "1MS21EC012",
            "full_name": "Amit Verma",
            "branch": "ECE",
            "cgpa": 6.50,
            "active_backlogs": 0,
            "cleared_backlogs": 1,
            "phone": "+91 98765 43212",
            "skills": "Embedded Systems, Verilog, C, Python",
            "has_accepted_offer": False,
        },
        {
            "email": "sneha.patil@talenthub.edu",
            "password": "StudentPass123!",
            "usn": "1MS21IS033",
            "full_name": "Sneha Patil",
            "branch": "ISE",
            "cgpa": 6.45,
            "active_backlogs": 0,
            "cleared_backlogs": 0,
            "phone": "+91 98765 43213",
            "skills": "Web Development, React, Node.js",
            "has_accepted_offer": False,
        },
        {
            "email": "karthik.rao@talenthub.edu",
            "password": "StudentPass123!",
            "usn": "1MS21ME022",
            "full_name": "Karthik Rao",
            "branch": "MECH",
            "cgpa": 7.80,
            "active_backlogs": 1,
            "cleared_backlogs": 0,
            "phone": "+91 98765 43214",
            "skills": "CAD, MATLAB, Automation, Python",
            "has_accepted_offer": False,
        },
        {
            "email": "ananya.reddy@talenthub.edu",
            "password": "StudentPass123!",
            "usn": "1MS21CV008",
            "full_name": "Ananya Reddy",
            "branch": "CIVIL",
            "cgpa": 7.20,
            "active_backlogs": 0,
            "cleared_backlogs": 0,
            "phone": "+91 98765 43215",
            "skills": "AutoCAD, Structural Analysis, GIS",
            "has_accepted_offer": False,
        },
    ]

    student_objs = {}
    for sd in students_data:
        u = User(
            email=sd["email"],
            hashed_password=hash_password(sd["password"]),
            role="student",
            is_active=True,
        )
        db.add(u)
        db.flush()
        s = Student(
            user_id=u.id,
            usn=sd["usn"],
            full_name=sd["full_name"],
            email=sd["email"],
            branch=sd["branch"],
            cgpa=sd["cgpa"],
            active_backlogs=sd["active_backlogs"],
            cleared_backlogs=sd["cleared_backlogs"],
            phone=sd["phone"],
            skills=sd["skills"],
            has_accepted_offer=sd["has_accepted_offer"],
            consent_given=True,
        )
        db.add(s)
        db.flush()
        student_objs[sd["usn"]] = s

    # 5. Job Listings
    tcs = company_objs["Tata Consultancy Services (TCS)"]
    msft = company_objs["Microsoft Corporation"]
    infy = company_objs["Infosys Limited"]
    goog = company_objs["Google"]

    future_date = (now + timedelta(days=7)).strftime("%Y-%m-%d")
    future_date_2 = (now + timedelta(days=14)).strftime("%Y-%m-%d")

    jobs_data = [
        {
            "company_id": tcs.id,
            "role": "Systems Engineer / Digital Associate",
            "description": "Campus pool drive for core and digital software roles across development and cloud infrastructure.",
            "season": CURRENT_SEASON,
            "package_lpa": 7.2,
            "min_cgpa": 6.5,
            "max_backlogs": 0,
            "drive_date": future_date,
            "location": "Pan-India",
            "is_open": True,
            "branches": [],  # Pool drive: empty = all branches
        },
        {
            "company_id": msft.id,
            "role": "Software Development Engineer (SDE 1)",
            "description": "Join the Azure Core Engineering team building hyper-scale cloud platforms.",
            "season": CURRENT_SEASON,
            "package_lpa": 24.5,
            "min_cgpa": 8.0,
            "max_backlogs": 0,
            "drive_date": future_date,
            "location": "Bengaluru / Hyderabad",
            "is_open": True,
            "branches": ["CSE", "CSAI", "ISE"],
        },
        {
            "company_id": infy.id,
            "role": "Specialist Programmer (Power Programmer)",
            "description": "High-impact software engineering role focusing on algorithmic problem solving and full-stack architecture.",
            "season": CURRENT_SEASON,
            "package_lpa": 9.5,
            "min_cgpa": 7.0,
            "max_backlogs": 1,
            "drive_date": future_date_2,
            "location": "Bengaluru / Mysuru",
            "is_open": True,
            "branches": ["CSE", "ECE", "ISE", "CSAI"],
        },
        {
            "company_id": goog.id,
            "role": "Software Engineer, University Graduate",
            "description": "Design, test, deploy, and maintain large-scale software solutions.",
            "season": CURRENT_SEASON,
            "package_lpa": 32.0,
            "min_cgpa": 8.5,
            "max_backlogs": 0,
            "drive_date": future_date_2,
            "location": "Bengaluru",
            "is_open": True,
            "branches": ["CSE", "CSAI"],
        },
    ]

    job_objs = []
    for jd in jobs_data:
        j = JobListing(
            company_id=jd["company_id"],
            role=jd["role"],
            description=jd["description"],
            season=jd["season"],
            package_lpa=jd["package_lpa"],
            min_cgpa=jd["min_cgpa"],
            max_backlogs=jd["max_backlogs"],
            drive_date=jd["drive_date"],
            location=jd["location"],
            is_open=jd["is_open"],
        )
        db.add(j)
        db.flush()
        for b in jd["branches"]:
            db.add(JobAllowedBranch(job_id=j.id, branch=b))
        db.flush()
        job_objs.append(j)

    tcs_job, msft_job, infy_job, goog_job = job_objs

    # 6. Applications with diverse workflow stages
    # App 1: Priya Nair -> Microsoft -> ACCEPTED offer
    app_priya_msft = Application(
        student_id=student_objs["1MS21CS045"].id,
        job_id=msft_job.id,
        status=ApplicationStatus.ACCEPTED,
        applied_at=now - timedelta(days=10),
        updated_at=now - timedelta(days=1),
    )
    db.add(app_priya_msft)
    db.flush()

    # Interview rounds for Priya
    int_priya_r1 = InterviewSlot(
        application_id=app_priya_msft.id,
        round_no=1,
        round_name="Coding & Data Structures",
        scheduled_at=now - timedelta(days=5),
        venue="Microsoft Teams - Online",
        passed=True,
        notes="Candidate showed exceptional algorithmic mastery in dynamic programming.",
    )
    int_priya_r2 = InterviewSlot(
        application_id=app_priya_msft.id,
        round_no=2,
        round_name="System Architecture & Design",
        scheduled_at=now - timedelta(days=3),
        venue="Microsoft Teams - Online",
        passed=True,
        notes="Strong understanding of distributed cache and consistency models.",
    )
    db.add(int_priya_r1)
    db.add(int_priya_r2)
    db.flush()

    # Offer for Priya
    offer_priya = Offer(
        application_id=app_priya_msft.id,
        designation="Software Development Engineer 1",
        package_lpa=24.5,
        offer_letter_key="TH-2026-MSFT-88F4A1",
        joining_date="July 2027",
        terms="Full-time permanent role with stock grants and health coverage.",
        accepted=True,
        declined=False,
        issued_at=now - timedelta(days=2),
        decision_at=now - timedelta(days=1),
    )
    db.add(offer_priya)

    # App 2: Rahul Sharma -> Infosys -> SHORTLISTED, interview scheduled
    app_rahul_infy = Application(
        student_id=student_objs["1MS21CS001"].id,
        job_id=infy_job.id,
        status=ApplicationStatus.INTERVIEW_SCHEDULED,
        applied_at=now - timedelta(days=4),
        updated_at=now - timedelta(days=2),
    )
    db.add(app_rahul_infy)
    db.flush()

    int_rahul = InterviewSlot(
        application_id=app_rahul_infy.id,
        round_no=1,
        round_name="Technical & Problem Solving Round",
        scheduled_at=now + timedelta(days=2),
        venue="Placement Cell Lab 3 (Systems Block)",
        passed=None,
        notes="Please bring your updated resume and university ID card.",
    )
    db.add(int_rahul)

    # App 3: Rahul Sharma -> TCS -> SHORTLISTED
    app_rahul_tcs = Application(
        student_id=student_objs["1MS21CS001"].id,
        job_id=tcs_job.id,
        status=ApplicationStatus.SHORTLISTED,
        applied_at=now - timedelta(days=3),
        updated_at=now - timedelta(days=1),
    )
    db.add(app_rahul_tcs)

    # App 4: Amit Verma (ECE, 6.50 CGPA) -> TCS -> APPLIED (Exact boundary match!)
    app_amit_tcs = Application(
        student_id=student_objs["1MS21EC012"].id,
        job_id=tcs_job.id,
        status=ApplicationStatus.APPLIED,
        applied_at=now - timedelta(days=2),
        updated_at=now - timedelta(days=2),
    )
    db.add(app_amit_tcs)

    # App 5: Karthik Rao (MECH, 1 backlog) -> Infosys -> APPLIED (Allowed: max 1 backlog)
    app_karthik_infy = Application(
        student_id=student_objs["1MS21ME022"].id,
        job_id=infy_job.id,
        status=ApplicationStatus.APPLIED,
        applied_at=now - timedelta(days=1),
        updated_at=now - timedelta(days=1),
    )
    db.add(app_karthik_infy)

    db.commit()

    return {
        "status": "success",
        "message": "TalentHub demonstration seed data created successfully.",
        "counts": {
            "users": db.query(User).count(),
            "students": db.query(Student).count(),
            "companies": db.query(Company).count(),
            "jobs": db.query(JobListing).count(),
            "applications": db.query(Application).count(),
            "interviews": db.query(InterviewSlot).count(),
            "offers": db.query(Offer).count(),
        },
    }
