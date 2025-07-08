from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from translator import classify_question, get_sql, answer_general
from nasa_api import query_exoplanet
from image_api import fetch_image
from models import QueryRequest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query")
def unified_query(req: QueryRequest):
    try:
        qtype = classify_question(req.user_query)

        if qtype == "SQL":
            try:
                sql = get_sql(req.user_query)
                data = query_exoplanet(sql)
                return {"type": "SQL", "sql": sql, "data": data}
            except Exception as e:
                return {"type": "SQL", "error": str(e)}

        elif qtype == "IMAGE":
            try:
                image = fetch_image(req.user_query)
                if image:
                    return {"type": "IMAGE", "image": image}
                return {"type": "IMAGE", "message": "No image found."}
            except Exception as e:
                return {"type": "IMAGE", "error": str(e)}

        elif qtype == "GENERAL":
            try:
                answer = answer_general(req.user_query)
                return {"type": "GENERAL", "answer": answer}
            except Exception as e:
                return {"type": "GENERAL", "error": str(e)}

        else:
            return {"type": "INVALID", "message": "Please ask an astronomy-related question."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
