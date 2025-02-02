from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import main  # importing your existing main.py
import os

app = FastAPI()

class URLInput(BaseModel):
    urls: List[str]

@app.post("/generate-report/")
async def generate_report(url_input: URLInput):
    try:
        # Convert the list of URLs into a comma-separated string
        urls_string = ",".join(url_input.urls)
        
        # Initiate the chat using the manager and user_proxy from main.py
        main.user_proxy.initiate_chat(
            main.manager, 
            message=urls_string
        )
        
        # Check if the file was created
        filename = "women_empowerment_report.txt"
        if not os.path.exists(filename):
            raise HTTPException(status_code=500, detail="Failed to generate report")
        
        # Return the file
        return FileResponse(
            filename,
            media_type="text/plain",
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 