# Pantry Saver

Pantry Saver is a household food tracking app. Users can sign up, log in, create or join a household, log purchased and discarded food items, and view household waste statistics and personalized recommendations.

The app uses:

- Flet for the frontend
- Supabase Auth for login/signup
- Supabase Database for shared app data
- A Python algorithm worker for calculating household waste ratios and providing recommendations

## Project Structure

```text
project-course-pantry-saver/
├── frontend/
│   ├── requirements.txt
│   └── src/
│       ├── main.py
│       ├── pages/
│       ├── api/
│       ├── components/
│       └── assets/
├── algorithm/
│   ├── requirements.txt
│   ├── main.py
│   ├── worker.py
│   ├── algorithm.py
│   └── db.py
└── README.md
```

## Requirements
- Python 3.10 or newer
- pip
- Internet connection


## Environment Variables

The algorithm worker and frontend need Supabase environment variables.

Create a `.env` file inside the `algorithm` and `frontend` folder:

```env
SUPABASE_URL=https://mhavpdfogtoanjdaluox.supabase.co
SUPABASE_KEY=sb_publishable_WSh3sw_jmKTqJdd7SYf__Q_iSj15XoA
```

## Run Algorithm

### macOS/Linux
```bash
cd algorithm
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Windows Command Prompt
```bash
cd algorithm
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python main.py
```

## Run Frontend

### macOS/Linux
```bash
cd frontend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flet run src/main.py
```

### Windows Command Prompt
```bash
cd frontend
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
flet run src/main.py
```


## How To Use The App
1. Start the algorithm.
2. Start the frontend in a second terminal.
3. Sign up or log in.
4. Create a household or join an existing one.
5. Log a purchased food item.
6. Log a discarded food item with the same name.
7. Open the Statistics and Recommendation page
8. The waste ratio and recommendations should appear after the algorithm has processed the data.




## Algorithm Worker Usage

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