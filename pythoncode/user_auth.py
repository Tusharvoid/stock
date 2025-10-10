import streamlit as st
import os
import json

USER_DATA_DIR = "user_data"

if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)

def get_user_file(username):
    return os.path.join(USER_DATA_DIR, f"{username}.json")

def authenticate(username, password):
    user_file = get_user_file(username)
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            data = json.load(f)
        return data.get("password") == password
    return False

def register_user(username, password):
    user_file = get_user_file(username)
    if os.path.exists(user_file):
        return False
    with open(user_file, "w") as f:
        json.dump({"password": password, "stocks": []}, f)
    return True

def get_user_stocks(username):
    user_file = get_user_file(username)
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            data = json.load(f)
        return data.get("stocks", [])
    return []

def add_user_stock(username, stock):
    user_file = get_user_file(username)
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            data = json.load(f)
        data.setdefault("stocks", []).append(stock)
        with open(user_file, "w") as f:
            json.dump(data, f)
        return True
    return False
