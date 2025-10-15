# Ladaza AI Agent (Railway)

一键把 Ladaza AI 网页聊天小窗部署到 Railway。

## 部署步骤
1. 在本地解压本项目，或直接把 ZIP 上传到 Railway（New Project → Deploy from ZIP）。
2. 在 Railway 项目里设置环境变量（Variables）：
   - `OPENAI_API_KEY` = 你的 OpenAI Key
   - `MODEL` = gpt-4o-mini（或其他，如 gpt-4.1-mini）
   - `BRAND` = Ladaza
   - `WHATSAPP` = 60177502689
3. 等待部署完成，访问 Railway 提供的域名，如 `https://your-app.up.railway.app/`
4. 首页会显示一个简单页面，右下角 💬 按钮打开聊天小窗。

## 上传产品资料
将你的 CSV 放在 `data/ladaza_products.csv` 格式参考示例，
然后在本地运行：
```
python ingest_ladaza_data.py
```
或把 `INGEST_URL` 设为你的后端域名再运行：
```
INGEST_URL=https://your-app.up.railway.app/ingest python ingest_ladaza_data.py
```

## 接口说明
- `GET /health` 健康检查
- `POST /ingest` 追加知识库项：`{ items: ["文本", ...] }`
- `POST /chat` 聊天：`{ messages: [{role:"user", content:"..."}], session_id:"..." }`

> 当前 RAG 是简单关键词匹配，建议后期替换为向量检索（pgvector / faiss + embeddings）。
