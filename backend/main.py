from fastapi import FastAPI, HTTPException, status, Depends
from backend import db, schemas, auth
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Backend is running!"}

@app.post("/register")
async def register(user: schemas.UserCreate):
    existing = await db.users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = auth.hash_password(user.password)
    user_doc = {"email": user.email, "password": hashed_pw}
    await db.users_collection.insert_one(user_doc)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "User registered successfully"})

@app.post("/login")
async def login(user: schemas.UserLogin):
    user_doc = await db.users_collection.find_one({"email": user.email})
    if not user_doc or not auth.verify_password(user.password, user_doc["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"message": "Login successful"}
