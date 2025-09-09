"""
Run script for Rotax Pro Jet.

This script starts the Flask development server.
"""

from app import app

if __name__ == '__main__':
    app.run(debug=True)