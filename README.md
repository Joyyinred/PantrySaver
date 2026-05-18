## frontend
```bash
cd frontend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flet run
```

## backend
```bash
cd backend
./gradlew bootRun
```

## algorithm
```bash
cd algorithm
python -m venv .venv
source -venv/bin/activate
pip install -r requirements.txt
python main.py
```

Can also be run with own polling frequency:
```bash
python main.py --freq [Frequency in Seconds]
```