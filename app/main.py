from fastapi import FastAPI

app = FastAPI(
    title="Itsyar Backend",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Itsyar Backend Running"}