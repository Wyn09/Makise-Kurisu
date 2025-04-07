import fastapi
from main import *
import uvicorn
from start_tts_kurisu import start_kurisu
from config import ChatModelResponse
from pydantic import BaseModel

app = fastapi.FastAPI()
# start_kurisu()

class RequestInput(BaseModel):
    user_input: str


@app.post("/input_text")
async def execute_input_text(request_input: RequestInput) -> dict:
    loop = asyncio.get_running_loop()
    await handle_user_inputs(
        chatModel, 
        img2textModel, 
        intentModel, 
        request_input.user_input,  
        loop
    )

    if ChatModelResponse.outputs["translated_response"] != "": 
        return {"response": f"{ChatModelResponse.outputs["response"]}\n\t({ChatModelResponse.outputs["translated_response"]})"}
    
    return  {"response": f"{ChatModelResponse.outputs["response"]}"}


@app.post("/auto_chatWithImg")
async def execute_auto_chatWithImg() -> dict:
    loop = asyncio.get_running_loop()
    await init_next_run_time(loop, Img2TextModelConfig.init_sleep_time, Img2TextModelConfig.state)
    await asyncio.sleep(Img2TextModelConfig.init_sleep_time)
    
    while True:     
        await execute_chatWithImg_sleep_correction(
                chatModel,
                img2textModel,
                loop,
                user_inputs="",
                state=Img2TextModelConfig.state
            )

    if ChatModelResponse.outputs["translated_response"] != "": 
        return {"response": f"{ChatModelResponse.outputs["response"]}\n\t({ChatModelResponse.outputs["translated_response"]})"}
    
    return  {"response": f"{ChatModelResponse.outputs["response"]}"}

@app.post("/chatWithImg")
async def execute_chatWithImg(request_input: RequestInput) -> dict:
    await chatWithImg(chatModel, img2textModel, request_input.user_input)


if __name__ =="__main__":
    uvicorn.run("deploy:app", workers=1)
    
    pass