import fastapi
from fastapi.responses import StreamingResponse
from main import *
import uvicorn
from start_tts_kurisu import start_kurisu
from config import ChatModelResponse
from pydantic import BaseModel
from typing import Optional
app = fastapi.FastAPI()
# tts model api
start_kurisu()

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
async def execute_auto_chatWithImg():
    loop = asyncio.get_running_loop()
    await init_next_run_time(loop, Img2TextModelConfig.init_sleep_time, Img2TextModelConfig.state)
    await asyncio.sleep(Img2TextModelConfig.init_sleep_time)
    async def response_generator():
        
        while True:
            # 执行某些逻辑，调用 execute_chatWithImg_sleep_correction 并更新 ChatModelResponse.outputs
            await execute_chatWithImg_sleep_correction(
                chatModel, img2textModel, asyncio.get_running_loop(), user_input="", state=Img2TextModelConfig.state
            )
            
            # 构造回复文本
            if ChatModelResponse.outputs["translated_response"]:
                yield (
                    f"{ChatModelResponse.outputs['response']}\n"
                    f"({ChatModelResponse.outputs['translated_response']})\n"
                )
            else:
                yield f"{ChatModelResponse.outputs['response']}\n"
            
            # 控制生成间隔
            await asyncio.sleep(1)  # 根据实际情况调整间隔
        
    return StreamingResponse(response_generator(), media_type="text/plain")

@app.post("/chatWithImg")
async def execute_chatWithImg(request_input: Optional[RequestInput]) -> dict:
    await chatWithImg(chatModel, img2textModel, request_input.user_input)

    if ChatModelResponse.outputs["translated_response"] != "": 
        return {"response": f"{ChatModelResponse.outputs["response"]}\n\t({ChatModelResponse.outputs["translated_response"]})"}
    
    return  {"response": f"{ChatModelResponse.outputs["response"]}"}


if __name__ =="__main__":
    uvicorn.run("deploy:app", workers=1)
    
    pass