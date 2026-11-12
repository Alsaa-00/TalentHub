import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User, Student, Company
from app.schemas.auth import StudentRegisterRequest, CompanyRegisterRequest
from app.services.auth_service import AuthService
from app.utils.security import hash_password, verify_password, create_access_token, decode_access_token

class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_password_hashing_and_verification(self):
        pwd = "SecurePassword123!"
        hashed = hash_password(pwd)
        self.assertNotEqual(pwd, hashed)
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("WrongPassword!", hashed))

    def test_jwt_token_generation_and_decode(self):
        payload = {"sub": "student@talenthub.edu", "role": "student", "user_id": 42}
        token = create_access_token(payload)
        self.assertIsInstance(token, str)

        decoded = decode_access_token(token)
        self.assertEqual(decoded["sub"], "student@talenthub.edu")
        self.assertEqual(decoded["role"], "student")
        self.assertEqual(decoded["user_id"], 42)

    def test_student_registration_and_authentication(self):
        req = StudentRegisterRequest(
            email="newstudent@talenthub.edu",
            password="Password123!",
            usn="1MS21CS099",
            full_name="New Student",
            branch="CSE",
            cgpa=8.50,
            active_backlogs=0,
            cleared_backlogs=0,
            consent_given=True
        )

        user, student = AuthService.register_student(self.db, req)
        self.assertIsNotNone(user.id)
        self.assertEqual(user.role, "student")
        self.assertEqual(student.usn, "1MS21CS099")

        # Authenticate with correct credentials
        authenticated_user = AuthService.authenticate_user(self.db, "newstudent@talenthub.edu", "Password123!")
        self.assertEqual(authenticated_user.id, user.id)

        # Token creation
        token = AuthService.create_token_for_user(authenticated_user)
        self.assertEqual(token.role, "student")
        self.assertEqual(token.name, "New Student")

    def test_company_registration(self):
        req = CompanyRegisterRequest(
            email="hr@innovatetech.com",
            password="CompanyPassword123!",
            name="Innovate Tech Corp",
            location="Bengaluru",
            industry="Software"
        )

        user, company = AuthService.register_company(self.db, req)
        self.assertIsNotNone(company.id)
        self.assertEqual(company.name, "Innovate Tech Corp")
        self.assertEqual(user.role, "company")

if __name__ == "__main__":
    unittest.main()
