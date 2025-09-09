"""
Test runner for Rotax Pro Jet.

This script runs the test suite for the application.
"""

import unittest
import coverage
import sys

def run_tests():
    """Run the test suite."""
    # Start coverage
    cov = coverage.Coverage(
        branch=True,
        include='app.py',
        omit=[
            'tests/*',
            'venv/*',
            '*/site-packages/*'
        ]
    )
    cov.start()
    
    # Discover and run tests
    tests = unittest.TestLoader().discover('tests')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    
    # Stop coverage
    cov.stop()
    cov.save()
    
    print('Coverage Summary:')
    cov.report()
    
    # Generate HTML report
    cov.html_report(directory='coverage_html')
    print('HTML version: coverage_html/index.html')
    
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())