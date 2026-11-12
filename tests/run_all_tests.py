import sys
import unittest
from pathlib import Path

# Add backend directory to sys.path so app modules are discovered
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

def main():
    print("=" * 60)
    print("TalentHub – Comprehensive Test Suite Execution")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(Path(__file__).parent), pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)

    if result.wasSuccessful():
        print("ALL TALENTHUB TESTS PASSED SUCCESSFULLY! [PASS]")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED! [FAIL]")
        sys.exit(1)

if __name__ == "__main__":
    main()
