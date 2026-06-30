from fastapi import FastAPI

app = FastAPI(
    title="NovaPOS API",
    version="0.1.0",
    description="Backend oficial de NovaPOS"
)


@app.get("/")
def health_check():
    return {
        "app": "NovaPOS",
        "status": "running",
        "version": "0.1.0"
    }