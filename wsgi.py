from app import create_app
from database.seed import seed_database

application = create_app()

# On a fresh deployment the database is empty, so seed the demo accounts and
# catalog automatically. seed_database() safely skips if data already exists.
seed_database(application)

if __name__ == "__main__":
    application.run()
