"""
Security Bot Enterprise - Authentication System
JWT-based authentication with role-based access control
"""

import jwt
import hashlib
import sqlite3
import secrets
import logging
from datetime import datetime, timedelta
from functools import wraps


class AuthenticationSystem:
    """Enterprise authentication with JWT and RBAC"""
    
    def __init__(self, db_path="security_bot.db", secret_key=None):
        self.db_path = db_path
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.token_expiry = timedelta(hours=8)
        self.setup_logging()
        self.init_auth_database()
        self.create_default_admin()
    
    def setup_logging(self):
        """Setup authentication logging"""
        self.logger = logging.getLogger('AuthSystem')
    
    def init_auth_database(self):
        """Initialize authentication database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    email TEXT,
                    role TEXT DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    token_hash TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Roles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    permissions TEXT,
                    description TEXT
                )
            """)
            
            # Default roles
            default_roles = [
                ('admin', 'all', 'Full system access'),
                ('analyst', 'read,write_reports', 'Security analyst access'),
                ('viewer', 'read', 'Read-only access'),
                ('user', 'read_basic', 'Basic user access')
            ]
            
            cursor.executemany("""
                INSERT OR IGNORE INTO roles (name, permissions, description)
                VALUES (?, ?, ?)
            """, default_roles)
            
            conn.commit()
            conn.close()
            
            self.logger.info("Authentication database initialized")
            
        except Exception as e:
            self.logger.error("Failed to initialize auth database: %s", e)
    
    def create_default_admin(self):
        """Create default admin user if none exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            admin_count = cursor.fetchone()[0]
            
            if admin_count == 0:
                # Create default admin
                salt = secrets.token_hex(32)
                password = "SecurityBot2024!"  # Should be changed on first login
                password_hash = self.hash_password(password, salt)
                
                cursor.execute("""
                    INSERT INTO users (username, password_hash, salt, email, role)
                    VALUES (?, ?, ?, ?, ?)
                """, ("admin", password_hash, salt, "admin@securitybot.com", "admin"))
                
                conn.commit()
                self.logger.info("Default admin user created (username: admin, password: SecurityBot2024!)")
            
            conn.close()
            
        except Exception as e:
            self.logger.error("Failed to create default admin: %s", e)
    
    def hash_password(self, password, salt):
        """Hash password with salt"""
        return hashlib.pbkdf2_hex(password.encode(), salt.encode(), 100000, 64)
    
    def verify_password(self, password, password_hash, salt):
        """Verify password against hash"""
        return self.hash_password(password, salt) == password_hash
    
    def create_user(self, username, password, email=None, role='user'):
        """Create new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                return {'success': False, 'message': 'Username already exists'}
            
            # Create user
            salt = secrets.token_hex(32)
            password_hash = self.hash_password(password, salt)
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, salt, email, role)
                VALUES (?, ?, ?, ?, ?)
            """, (username, password_hash, salt, email, role))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.info("User created: %s (role: %s)", username, role)
            return {'success': True, 'user_id': user_id}
            
        except Exception as e:
            self.logger.error("Failed to create user: %s", e)
            return {'success': False, 'message': str(e)}
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, password_hash, salt, role, is_active
                FROM users WHERE username = ?
            """, (username,))
            
            user_data = cursor.fetchone()
            if not user_data:
                return {'success': False, 'message': 'Invalid credentials'}
            
            user_id, password_hash, salt, role, is_active = user_data
            
            if not is_active:
                return {'success': False, 'message': 'Account disabled'}
            
            if not self.verify_password(password, password_hash, salt):
                return {'success': False, 'message': 'Invalid credentials'}
            
            # Update last login
            cursor.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (user_id,))
            
            conn.commit()
            conn.close()
            
            self.logger.info("User authenticated: %s", username)
            return {
                'success': True,
                'user_id': user_id,
                'username': username,
                'role': role
            }
            
        except Exception as e:
            self.logger.error("Authentication error: %s", e)
            return {'success': False, 'message': 'Authentication failed'}
    
    def generate_token(self, user_id, username, role):
        """Generate JWT token"""
        try:
            payload = {
                'user_id': user_id,
                'username': username,
                'role': role,
                'exp': datetime.utcnow() + self.token_expiry,
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            
            # Store token hash in database
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO sessions (user_id, token_hash, expires_at)
                VALUES (?, ?, ?)
            """, (user_id, token_hash, datetime.utcnow() + self.token_expiry))
            
            conn.commit()
            conn.close()
            
            return token
            
        except Exception as e:
            self.logger.error("Failed to generate token: %s", e)
            return None
    
    def verify_token(self, token):
        """Verify JWT token"""
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Check if token exists in database
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id, expires_at, is_active
                FROM sessions WHERE token_hash = ?
            """, (token_hash,))
            
            session_data = cursor.fetchone()
            if not session_data:
                return {'success': False, 'message': 'Invalid token'}
            
            user_id, expires_at, is_active = session_data
            
            if not is_active:
                return {'success': False, 'message': 'Session expired'}
            
            # Check expiration
            expires_at = datetime.fromisoformat(expires_at.replace('Z', ''))
            if datetime.utcnow() > expires_at:
                # Deactivate expired session
                cursor.execute("""
                    UPDATE sessions SET is_active = 0 WHERE token_hash = ?
                """, (token_hash,))
                conn.commit()
                conn.close()
                return {'success': False, 'message': 'Token expired'}
            
            conn.close()
            
            return {
                'success': True,
                'user_id': payload['user_id'],
                'username': payload['username'],
                'role': payload['role']
            }
            
        except jwt.ExpiredSignatureError:
            return {'success': False, 'message': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'success': False, 'message': 'Invalid token'}
        except Exception as e:
            self.logger.error("Token verification error: %s", e)
            return {'success': False, 'message': 'Token verification failed'}
    
    def revoke_token(self, token):
        """Revoke JWT token"""
        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE sessions SET is_active = 0 WHERE token_hash = ?
            """, (token_hash,))
            
            conn.commit()
            conn.close()
            
            return {'success': True}
            
        except Exception as e:
            self.logger.error("Failed to revoke token: %s", e)
            return {'success': False, 'message': str(e)}
    
    def check_permission(self, role, required_permission):
        """Check if role has required permission"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT permissions FROM roles WHERE name = ?", (role,))
            result = cursor.fetchone()
            
            if not result:
                return False
            
            permissions = result[0].split(',') if result[0] else []
            
            # Admin has all permissions
            if 'all' in permissions:
                return True
            
            # Check specific permission
            return required_permission in permissions
            
        except Exception as e:
            self.logger.error("Permission check error: %s", e)
            return False
    
    def require_auth(self, required_permission=None):
        """Decorator for requiring authentication"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # This would typically extract token from request headers
                # For now, we'll pass token as a parameter
                token = kwargs.get('token')
                if not token:
                    return {'success': False, 'message': 'Authentication required'}
                
                # Verify token
                auth_result = self.verify_token(token)
                if not auth_result['success']:
                    return auth_result
                
                # Check permission
                if required_permission:
                    if not self.check_permission(auth_result['role'], required_permission):
                        return {'success': False, 'message': 'Insufficient permissions'}
                
                # Add user info to kwargs
                kwargs['current_user'] = auth_result
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def login(self, username, password):
        """Complete login process"""
        auth_result = self.authenticate_user(username, password)
        
        if not auth_result['success']:
            return auth_result
        
        token = self.generate_token(
            auth_result['user_id'],
            auth_result['username'],
            auth_result['role']
        )
        
        if not token:
            return {'success': False, 'message': 'Failed to generate token'}
        
        return {
            'success': True,
            'token': token,
            'user': {
                'id': auth_result['user_id'],
                'username': auth_result['username'],
                'role': auth_result['role']
            }
        }
    
    def logout(self, token):
        """Logout user"""
        return self.revoke_token(token)
    
    def get_user_info(self, token):
        """Get user information from token"""
        return self.verify_token(token)


if __name__ == '__main__':
    # Test authentication system
    auth = AuthenticationSystem()
    
    # Test login
    result = auth.login("admin", "SecurityBot2024!")
    if result['success']:
        print(f"Login successful! Token: {result['token'][:50]}...")
        
        # Test token verification
        verify_result = auth.verify_token(result['token'])
        print(f"Token verification: {verify_result}")
    else:
        print(f"Login failed: {result['message']}")