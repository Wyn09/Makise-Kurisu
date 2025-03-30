import fastapi
from main import read_input

app = fastapi.FastAPI()

@app.route("/inputText")
async def execute_inputText(text_language="zh"):
    read_input(text_language)



if __name__ =="__main__":
    
    pass