"""
Migration script to add ProcessedImage table to the database.
Run this script to create the new table in your database.
"""

from app import app, db
from models import ProcessedImage
from datetime import datetime

def migrate():
    """Add the ProcessedImage table to the database"""
    with app.app_context():
        print("Creating ProcessedImage table...")
        
        # Create the table
        db.create_all()
        
        # Verify the table was created
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'processed_image' in tables:
            print("✅ ProcessedImage table created successfully!")
            print(f"📊 All tables: {', '.join(tables)}")
        else:
            print("❌ ProcessedImage table was not created")
            print(f"📊 Existing tables: {', '.join(tables)}")
        
        print("\n✨ Migration complete!")
        print("\nTo verify, you can check with:")
        print("  SELECT * FROM processed_image;")

if __name__ == '__main__':
    migrate()
















