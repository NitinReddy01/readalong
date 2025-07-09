from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import webbrowser
import os
import torch
torch.set_num_threads(1)

import lambdaTTS
import lambdaSpeechToScore
import lambdaGetSample
import asyncio
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor  
# --- FastAPI Setup ---
app = FastAPI()

# --- CORS Setup ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



MAX_WORKERS = 3
executor = ProcessPoolExecutor(max_workers=MAX_WORKERS) 



async def run_inference(model_fn, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, model_fn, *args)
# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/metrics")
async def performance_metrics():
    return {
        "memory_usage": psutil.Process().memory_info().rss,
        "cpu_percent": psutil.cpu_percent(),
        "active_connections": len(asyncio.all_tasks())
    }


@app.post("/getAudioFromText")
async def get_audio_from_text(request: Request):
    body = await request.json()
    event = {'body': json.dumps(body)}
    return JSONResponse(lambdaTTS.lambda_handler(event, []))


@app.post("/getSample")
async def get_sample(request: Request):
    body = await request.json()
    event = {'body': json.dumps(body)}
    return JSONResponse(lambdaGetSample.lambda_handler(event, []))


@app.post("/GetAccuracyFromRecordedAudio")
async def get_accuracy_from_recorded_audio(request: Request):
    try:
        body =  await request.json()
        event = {'body': json.dumps(body)}
        # output =  await asyncio.get_event_loop().run_in_executor(
        #     executor,
        #     lambdaSpeechToScore.lambda_handler,
        #     event,
        #     []
        # )
        output=await lambdaSpeechToScore.lambda_handler(event, [])
        print("Output:", output)
        return JSONResponse(output)
    except Exception as e:
        print("Error:", str(e))
        return JSONResponse(
            status_code=200,
            content={
                'headers': {
                    'Access-Control-Allow-Headers': '*',
                    'Access-Control-Allow-Credentials': "true",
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                                'error': str(e)
              

            }
        )

# --- Run with Uvicorn ---
if __name__ == "__main__":
    print(os.system("pwd"))
    uvicorn.run("main:app", host="0.0.0.0", port=5551, reload=True)
