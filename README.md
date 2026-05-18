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
## Usage

Run with default settings:
```bash
python main.py
```

Or configure the intervals:
```bash
python main.py --freq 30 --shortterm 7 --longterm 60
```

| Argument | Default | Description |
|---|---|---|
| `--freq` | 60 | Polling frequency in seconds |
| `--shortterm` | 30 | Short-term analysis window in days |
| `--longterm` | 90 | Long-term analysis window in days |