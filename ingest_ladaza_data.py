# Upload CSV rows into the Agent KB via /ingest
import csv, requests, os
API = os.environ.get('INGEST_URL', 'https://your-railway-app-url/ingest')

items = []
with open('data/ladaza_products.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for r in reader:
        text = f"{r['名称']} | 尺寸:{r['尺寸']} | 材质:{r['材质']} | 特点:{r['特点']} | 备注:{r['备注']}"
        items.append(text)

res = requests.post(API, json={'items': items})
print('✅ 上传完成:', res.json())
