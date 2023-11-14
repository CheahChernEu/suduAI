import uvicorn
from fastapi import FastAPI, File, UploadFile

from ingest import Ingest
from llm import SuduLLM


sudu_LLM = SuduLLM()

app = FastAPI()


@app.post("/upload")
async def upload(metadata, file: UploadFile = File(...)):
    ingest_pdf = Ingest("chroma_db", metadata)
    
    content = await file.read()
    with open('test.pdf', 'wb') as file:  
        file.write(content)
    response = ingest_pdf.run("test.pdf")
    return response
    
    
@app.post("/chat")
async def upload(msg, metadata):
    
    # ## Create the sudu llm
    sudu_LLM.create_sudu()

    # Infer
    response = sudu_LLM.infer_sudu({'query': msg}, metadata)

    result = {
            'model_output': response['model_output'],
            'source_document': ''
        }

    return result

    

if __name__ == "__main__":
    uvicorn.run('main:app', host="0.0.0.0", port=8005, reload=True)