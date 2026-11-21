import os
from app import create_app

application = create_app()

# Auto-seed on first deploy: runs only when admin user doesn't exist yet
with application.app_context():
    try:
        from models.user import User
        if not User.query.filter_by(username='admin').first():
            from database.seed import seed_database
            seed_database(application)
            print("✅ Database seeded with demo data.")
    except Exception as e:
        # DB may not be ready yet — Render will restart and retry
        print(f"⚠️  Seed skipped (DB not ready): {e}")

if __name__ == "__main__":
    application.run()
