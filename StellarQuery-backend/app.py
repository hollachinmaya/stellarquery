from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from translator import classify_question, get_sql, get_adql, answer_general
from nasa_api import query_exoplanet
from gaia_api import query_gaia
from models import QueryRequest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 Store conversation history per user
user_histories = {}


@app.post("/query")
def unified_query(req: QueryRequest):
    try:
        # ⚡ Use a dummy user_id (for now) - replace with real authentication later
        user_id = "default_user"

        # 🧠 Initialize history for user if not present
        if user_id not in user_histories:
            user_histories[user_id] = []

        # Append user query to conversation history
        user_histories[user_id].append({"role": "user", "content": req.user_query})

        # Detect query type
        qtype = classify_question(req.user_query, user_histories[user_id])
        print(f"📝 Detected query type: {qtype}")

        if qtype == "SQL":
            sql = get_sql(req.user_query, user_histories[user_id])
            print(f"📄 SQL generated: {sql}")

            data = query_exoplanet(sql)
            user_histories[user_id].append({"role": "assistant", "content": f"SQL: {sql}"})
            return {"type": "SQL", "sql": sql, "data": data}

        elif qtype == "IMAGE":
            image = fetch_image(req.user_query)
            if image:
                user_histories[user_id].append({"role": "assistant", "content": f"Image: {image['title']}"})
                return {"type": "IMAGE", "image": image}
            user_histories[user_id].append({"role": "assistant", "content": "No image found."})
            return {"type": "IMAGE", "message": "No image found."}

        elif qtype == "GENERAL":
            answer = answer_general(req.user_query, user_histories[user_id])
            user_histories[user_id].append({"role": "assistant", "content": answer})
            return {"type": "GENERAL", "answer": answer}

        elif qtype == "GAIA":
            adql = get_adql(req.user_query, user_histories[user_id])
            print(f"📄 ADQL generated: {adql}")

            data = query_gaia(adql)
            user_histories[user_id].append({"role": "assistant", "content": f"ADQL: {adql}"})
            return {"type": "GAIA", "adql": adql, "data": data}

        else:
            user_histories[user_id].append({"role": "assistant", "content": "Invalid question."})
            return {"type": "INVALID", "message": "Please ask an astronomy-related question."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
