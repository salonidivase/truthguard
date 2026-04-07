from backend.main import app

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

# ✅ THIS LINE IS REQUIRED
if _name_ == "_main_":
    main()
