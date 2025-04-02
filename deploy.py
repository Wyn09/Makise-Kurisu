import fastapi
from main import *
import uvicorn
from tts_kurisu import start_tts

app = fastapi.FastAPI()
start_tts()

@app.post("/inputText")
async def execute_inputText(user_inputs):
    loop = asyncio.get_running_loop()
    response, translated_text = await handle_user_inputs(
        chatModel, 
        img2textModel, 
        intentModel, 
        user_inputs, 
        CHAT_HISTORY, 
        loop
    )

    if translated_text:
        return {"output": f"{response}\n\t({translated_text})"}
    
    return  {"output": f"{response}"}



if __name__ =="__main__":
    uvicorn.run("deploy:app", workers=2)
    
    pass