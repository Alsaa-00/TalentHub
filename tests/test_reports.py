import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.seed_data import seed_database
from app.services.report_service import ReportService

class TestReportService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Seed full realistic dataset
        seed_database(self.db)

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_placement_statistics_calculation(self):
        stats = ReportService.get_placement_statistics(self.db)
        self.assertEqual(stats.total_registered_students, 6)
        self.assertEqual(stats.total_placed_students, 1)  # Priya Nair is placed
        self.assertAlmostEqual(stats.overall_placement_percentage, (1 / 6 * 100), places=1)
        self.assertEqual(stats.highest_package_lpa, 24.5)
        self.assertTrue(len(stats.branch_breakdown) > 0)

    def test_placed_students_list(self):
        placed = ReportService.get_placed_students(self.db)
        self.assertEqual(len(placed), 1)
        self.assertEqual(placed[0].usn, "1MS21CS045")
        self.assertEqual(placed[0].company_name, "Microsoft Corporation")
        self.assertEqual(placed[0].package_lpa, 24.5)

    def test_export_shortlist_csv(self):
        csv_text = ReportService.export_job_shortlist_csv(self.db, job_id=1)
        self.assertIn("USN,Student Name,Email,Branch,CGPA", csv_text)

if __name__ == "__main__":
    unittest.main()
