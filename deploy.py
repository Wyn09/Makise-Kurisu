import fastapi
from main import *
import uvicorn
from start_tts_kurisu import start_kurisu
from config import ChatModelResponse

app = fastapi.FastAPI()
start_kurisu()


@app.post("/inputText")
async def execute_inputText(user_inputs):
    loop = asyncio.get_running_loop()
    await handle_user_inputs(
        chatModel, 
        img2textModel, 
        intentModel, 
        user_inputs,  
        loop
    )

    if ChatModelResponse.outputs["translated_response"] != "": 
        return {"output": f"{ChatModelResponse.outputs["response"]}\n\t({ChatModelResponse.outputs["translated_response"]})"}
    
    return  {"output": f"{ChatModelResponse.outputs["response"]}"}



if __name__ =="__main__":
    uvicorn.run("deploy:app", workers=1)
    
    pass