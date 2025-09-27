from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import db, schemas, auth
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test database connection on startup
@app.on_event("startup")
async def startup_event():
    connection_success = await db.test_connection()
    if not connection_success:
        logger.error("Failed to connect to MongoDB!")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Backend is running!"}

@app.get("/test_api.html")
def get_test_page():
    return FileResponse("test_api.html")

@app.post("/register")
async def register(user: schemas.UserCreate):
    try:
        # Check if email is valid
        if not user.email or len(user.email.strip()) == 0:
            raise HTTPException(status_code=400, detail="Email is required")
        
        # Check if password is strong enough
        if not user.password or len(user.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
        
        # Check if user already exists
        existing = await db.users_collection.find_one({"email": user.email.lower()})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password and create user
        hashed_pw = auth.hash_password(user.password)
        user_doc = {
            "email": user.email.lower(),
            "password": hashed_pw,
            "created_at": {"$currentDate": True}
        }
        
        # Insert user into database
        result = await db.users_collection.insert_one(user_doc)
        logger.info(f"User registered successfully with ID: {result.inserted_id}")
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, 
            content={"message": "User registered successfully", "user_id": str(result.inserted_id)}
        )
        
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during registration")

@app.post("/login")
async def login(user: schemas.UserLogin):
    try:
        # Validate input
        if not user.email or len(user.email.strip()) == 0:
            raise HTTPException(status_code=400, detail="Email is required")
        
        if not user.password or len(user.password.strip()) == 0:
            raise HTTPException(status_code=400, detail="Password is required")
        
        # Find user in database
        user_doc = await db.users_collection.find_one({"email": user.email.lower()})
        
        if not user_doc:
            logger.warning(f"Login attempt with non-existent email: {user.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not auth.verify_password(user.password, user_doc["password"]):
            logger.warning(f"Failed login attempt for email: {user.email}")
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        logger.info(f"Successful login for email: {user.email}")
        return {
            "message": "Login successful",
            "user_id": str(user_doc["_id"]),
            "email": user_doc["email"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during login")
