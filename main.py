import uvicorn
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

from router.route import router
from database_folder.create_session import Base, engine

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(router=router)

@app.get(path="/", tags=["Home Page"])
def HomePage():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Swagger Ui")

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)