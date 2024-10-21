# main.py
from fastapi import FastAPI
from routes.whatsapp import router as whatsapp_router

app = FastAPI()

# Incluir todos os routers aqui
app.include_router(whatsapp_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
