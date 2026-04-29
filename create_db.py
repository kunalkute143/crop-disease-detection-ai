# create_my_database.py
from app import app
from extensions.db import db
import os

print("=" * 50)
print("🚀 DATABASE CREATION")
print("=" * 50)

# 1. instance folder check
if not os.path.exists('instance'):
    os.makedirs('instance')
    print("📁 Instance folder created")

# 2. Database create
with app.app_context():
    db.create_all()
    print("✅ Database tables created")
    
    # 3. Show path
    db_path = os.path.join('instance', 'database.sqlite3')
    print(f"📂 Database: {os.path.abspath(db_path)}")

print("=" * 50)
print("🎉 DONE! Now run: python app.py")
print("=" * 50)