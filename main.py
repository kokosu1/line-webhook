# main.py
import uvicorn
from webhook import app
from scheduler import start_scheduler

start_scheduler()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
