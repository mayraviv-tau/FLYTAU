"""
Script to hash existing plain text passwords in the database
Run this once after loading seed.sql with plain text passwords
"""
from werkzeug.security import generate_password_hash
import mysql.connector
from config import Config

def hash_all_passwords():
    """Hash all plain text passwords in the database"""
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            port=Config.DB_PORT
        )
        cursor = conn.cursor(dictionary=True)
        
        # Hash manager passwords
        cursor.execute("SELECT id_number, account_password FROM Manager")
        managers = cursor.fetchall()
        updated_managers = 0
        for mgr in managers:
            password = mgr['account_password']
            # Check if already hashed (werkzeug hashes start with 'pbkdf2:' or 'scrypt:')
            if not password.startswith('pbkdf2:') and not password.startswith('scrypt:'):
                hashed = generate_password_hash(password)
                cursor.execute(
                    "UPDATE Manager SET account_password = %s WHERE id_number = %s",
                    (hashed, mgr['id_number'])
                )
                updated_managers += 1
                print(f"Updated password for manager {mgr['id_number']}")
        
        # Hash customer passwords
        cursor.execute("SELECT email, account_password FROM RegisteredCustomer")
        customers = cursor.fetchall()
        updated_customers = 0
        for cust in customers:
            password = cust['account_password']
            # Check if already hashed
            if not password.startswith('pbkdf2:') and not password.startswith('scrypt:'):
                hashed = generate_password_hash(password)
                cursor.execute(
                    "UPDATE RegisteredCustomer SET account_password = %s WHERE email = %s",
                    (hashed, cust['email'])
                )
                updated_customers += 1
                print(f"Updated password for customer {cust['email']}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✅ Successfully hashed passwords!")
        print(f"   - Managers updated: {updated_managers}")
        print(f"   - Customers updated: {updated_customers}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == '__main__':
    print("Hashing passwords in database...")
    hash_all_passwords()

