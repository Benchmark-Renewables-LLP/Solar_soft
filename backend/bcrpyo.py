from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print(pwd_context.hash("demo123"))  # Replace hash for 'demo'
print(pwd_context.hash("admin123")) # Replace hash for 'admin'