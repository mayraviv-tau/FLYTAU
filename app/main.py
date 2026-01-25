"""
FLYTAU - Flight Management System
Main Entry Point

To run locally:
1. Make sure MySQL is running with database 'flytau'
2. Run: python main.py
3. Open: http://localhost:5000
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Starting FLYTAU server...")
    print("Local URL: http://localhost:5000")
    print("Make sure MySQL is running with database 'flytau'")
    app.run(debug=True, host='0.0.0.0', port=5000)
