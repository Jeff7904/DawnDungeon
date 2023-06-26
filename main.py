
from dawndungeon import config
from subprocess import Popen
from threading import Thread
import uvicorn

if __name__ == "__main__":
    def start_frontend():
        uvicorn.run(
            "dawndungeon-frontend.app:app",
            host="0.0.0.0",
            port=int(config.get("FRONTEND_PORT")),
            log_level="debug",
            reload=False,
        )
    def start_backend():
        uvicorn.run(
            "dawndungeon.api.app:app",
            host="0.0.0.0",
            port=int(config.get("BACKEND_PORT")),
            log_level="trace",
            reload=False,
        )
    def start_streamlit():
        Popen(["streamlit", "run", "dawndungeon/api/streamlit_app.py", "--server.enableCORS=true", "--server.port=8502"])

    Thread(target=start_streamlit).start()
    start_backend()
    