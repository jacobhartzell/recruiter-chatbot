#!/usr/bin/env python3
"""
Test runner script for the recruiter chatbot project.
"""

import subprocess
import sys
import os


def run_tests():
    """Run the test suite using pytest."""
    print("Running recruiter chatbot test suite...")
    print("=" * 50)
    
    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run pytest with coverage if available
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short"
        ], capture_output=False)
        
        if result.returncode == 0:
            print("\n" + "=" * 50)
            print("✅ All tests passed!")
        else:
            print("\n" + "=" * 50)
            print("❌ Some tests failed!")
            
        return result.returncode
        
    except FileNotFoundError:
        print("❌ Error: pytest not found. Please install pytest first:")
        print("   conda install pytest")
        return 1


def run_specific_test(test_file):
    """Run a specific test file."""
    print(f"Running tests in {test_file}...")
    print("=" * 50)
    
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        f"tests/{test_file}",
        "-v"
    ], capture_output=False)
    
    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test file
        test_file = sys.argv[1]
        if not test_file.startswith("test_"):
            test_file = f"test_{test_file}"
        if not test_file.endswith(".py"):
            test_file = f"{test_file}.py"
            
        exit_code = run_specific_test(test_file)
    else:
        # Run all tests
        exit_code = run_tests()
    
    sys.exit(exit_code)