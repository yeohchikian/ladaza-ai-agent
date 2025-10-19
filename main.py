from fastapi.staticfiles import StaticFiles
import os, uuid, time
from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx

# Load env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL", "gpt-4o-mini")
BRAND = os.getenv("BRAND", "Ladaza")
WHATSAPP = os.getenv("WHATSAPP", "60177502689")

app = FastAPI(title=f"{BRAND} AI Agent", version="1.0")

# In-memory KB (MVP). You can POST /ingest to add more.
PRODUCT_KB: List[str] = [
    "Ladaza 橙色布艺沙发，贝壳形靠背，宽180cm，布料可拆洗，保养建议使用中性清洁剂。",
    "圆形大理石餐桌，直径120cm，4/6椅可选，啡色皮椅，金属脚，全马包邮（偏远地区询问）。",
    "电视机橱柜：浮悬式，白色+胡桃木抽屉，支持55-75寸电视。"
]

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    session_id: Optional[str] = None
    channel: Optional[str] = "web"

class IngestRequest(BaseModel):
    items: List[str]

def simple_search(query: str, k: int = 3) -> List[str]:
    """Very simple keyword match. Replace with embeddings later."""
    q = query.lower()
    scored = []
    for p in PRODUCT_KB:
        score = sum(w in p.lower() for w in q.split())
        scored.append((score, p))
    return [p for s, p in sorted(scored, key=lambda x: -x[0])[:k] if s > 0] or PRODUCT_KB[:k]

async def llm(messages: List[dict]) -> str:
    if not OPENAI_API_KEY:
        return "⚠️ 后端未配置 OPENAI_API_KEY，请在环境变量中设置后重试。"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {"model": MODEL, "messages": messages, "temperature": 0.2}
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post("https://api.openai.com/v1/chat/completions",
                                 headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

@app.get("/health")
def health():
    return {"ok": True, "ts": time.time(), "brand": BRAND}

@app.post("/ingest")
def ingest(req: IngestRequest):
    PRODUCT_KB.extend(req.items)
    return {"ok": True, "count": len(req.items)}

@app.post("/chat")
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    user_msg = req.messages[-1].content if req.messages else ""
    topk = simple_search(user_msg, k=3)
    system_prompt = (
        f"你是{BRAND}家具店的AI顾问，会使用中文/英文/马来文。"
        "回答要礼貌简洁，基于产品资料；若涉及价格/库存/配送时间，请引导用户联系真人客服。"
    )
    refs = "\n- ".join(topk) if topk else "暂无匹配资料"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"资料参考：\n- {refs}\n用户问题：{user_msg}\n请先用用户语言作答，最后附：联系真人客服 wa.me/{WHATSAPP}"}
    ]
    answer = await llm(messages)
    return {"session_id": session_id, "answer": answer, "refs": topk}
    # Serve static files from "public" folder at the root URL
app.mount("/", StaticFiles(directory="public", html=True), name="public")

