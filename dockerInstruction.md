

1. make sure has `.env` file in both algorithm and frontend :

```env
SUPABASE_URL=https://mhavpdfogtoanjdaluox.supabase.co
SUPABASE_KEY=sb_publishable_WSh3sw_jmKTqJdd7SYf__Q_iSj15XoA
```


2. run algorithm(windows powershell)
```bash
cd algorithm
docker run --rm -it -v ${PWD}:/app -w /app --env-file .env python:3.12-slim sh -c "pip install -r requirements.txt && python main.py"
```

3. run frontend(windows powershell)
```bash
docker run --rm -it -p 8550:8550 -v ${PWD}:/app -w /app --env-file .env python:3.12-slim sh -c "pip install -r requirements.txt && PYTHONPATH=/app/src flet run src/main.py --web --host 0.0.0.0 --port 8550"
```

4. open http://localhost:8550
