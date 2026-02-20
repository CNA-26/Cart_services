import psycopg2  # type: ignore
from psycopg2.extras import RealDictCursor  # type: ignore
import os
import urllib.parse
from dotenv import load_dotenv


load_dotenv()

 
# För lokal development, använder .env fil
# För deployment, använder OpenShift environment variables
# Stöder både DATABASE_URL och individuella variabler

def get_db_config():
    """Get database configuration from environment variables or DATABASE_URL"""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Parse DATABASE_URL
        parsed = urllib.parse.urlparse(database_url)
        return {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path.lstrip('/'),
            'user': parsed.username,
            'password': parsed.password
        }
    else:
        # Fallback till individuella miljövariabler
        return {
            'host': os.getenv('DB_HOST') or os.getenv('POSTGRESQL_SERVICE_HOST') or 'postgresql',
            'port': int(os.getenv('DB_PORT') or os.getenv('POSTGRESQL_SERVICE_PORT') or '5432'),
            'database': os.getenv('DB_NAME') or os.getenv('POSTGRESQL_DATABASE') or os.getenv('DATABASE_NAME') or 'sampledb',
            'user': os.getenv('DB_USER') or os.getenv('POSTGRESQL_USER') or os.getenv('DATABASE_USER') or 'userVNQ', 
            'password': os.getenv('DB_PASSWORD') or os.getenv('POSTGRESQL_PASSWORD') or os.getenv('DATABASE_PASSWORD') or 'cxulDFiUcmTHqp34'
        }

DB_CONFIG = get_db_config()

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_database():
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS carts (
                user_id VARCHAR(255) PRIMARY KEY,
                total_price DECIMAL(10,2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
       
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart_items (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) REFERENCES carts(user_id),
                product_id INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully")
        return True
    except Exception as e:
        print(f"Database initialization error: {e}")
        if conn:
            conn.close()
        return False

def get_cart(user_id):
    """Get cart för user"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get cart info
        cursor.execute("SELECT * FROM carts WHERE user_id = %s", (user_id,))
        cart = cursor.fetchone()
        
        # Get cart items
        cursor.execute("""
            SELECT product_id, name, price, quantity, image_url 
            FROM cart_items WHERE user_id = %s
        """, (user_id,))
        items = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if cart:
            return {
                "user_id": cart['user_id'],
                "items": [dict(item) for item in items],
                "total_price": float(cart['total_price'])
            }
        else:
            return {
                "user_id": user_id,
                "items": [],
                "total_price": 0.0
            }
    except Exception as e:
        print(f"Error getting cart: {e}")
        if conn:
            conn.close()
        return None

def add_item_to_cart(user_id, item):
    """Add item to cart"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Create cart if doesn't exist
        cursor.execute("""
            INSERT INTO carts (user_id) VALUES (%s) 
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id,))
        
        
        cursor.execute("""
            SELECT * FROM cart_items WHERE user_id = %s AND product_id = %s
        """, (user_id, item['product_id']))
        existing_item = cursor.fetchone()
        
        if existing_item:
           
            cursor.execute("""
                UPDATE cart_items SET quantity = quantity + %s 
                WHERE user_id = %s AND product_id = %s
            """, (item['quantity'], user_id, item['product_id']))
        else:
            
            cursor.execute("""
                INSERT INTO cart_items (user_id, product_id, name, price, quantity, image_url)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, item['product_id'], item['name'], item['price'], item['quantity'], item['image_url']))
        
      
        cursor.execute("""
            UPDATE carts SET total_price = (
                SELECT COALESCE(SUM(price * quantity), 0) 
                FROM cart_items WHERE user_id = %s
            ) WHERE user_id = %s
        """, (user_id, user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return get_cart(user_id)
    except Exception as e:
        print(f"Error adding item to cart: {e}")
        if conn:
            conn.close()
        return None

def remove_item_from_cart(user_id, product_id):
    """Remove item"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
    
        cursor.execute("""
            SELECT * FROM cart_items WHERE user_id = %s AND product_id = %s
        """, (user_id, product_id))
        removed_item = cursor.fetchone()
        
        if not removed_item:
            cursor.close()
            conn.close()
            return {"error": "Item not found in cart"}
        
      
        cursor.execute("""
            DELETE FROM cart_items WHERE user_id = %s AND product_id = %s
        """, (user_id, product_id))
        
    
        cursor.execute("""
            UPDATE carts SET total_price = (
                SELECT COALESCE(SUM(price * quantity), 0) 
                FROM cart_items WHERE user_id = %s
            ) WHERE user_id = %s
        """, (user_id, user_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        cart = get_cart(user_id)
        return {
            "message": "Item removed",
            "removed_item": dict(removed_item),
            "cart": cart
        }
    except Exception as e:
        print(f"Error removing item from cart: {e}")
        if conn:
            conn.close()
        return None