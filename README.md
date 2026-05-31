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
│   ├── run_worker.py
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

The algorithm worker needs Supabase environment variables. The frontend already contains the public Supabase URL and anon key used by the app.

Create a `.env` file in the project root or inside the `algorithm` folder:

```env
SUPABASE_URL=https://mhavpdfogtoanjdaluox.supabase.co
SUPABASE_KEY=sb_publishable_WSh3sw_jmKTqJdd7SYf__Q_iSj15XoA
```

## Run Algorithm

The instructions vary slightly depending on your system. There are 2 files to run, one for the frontend and one for the recommendation worker. The worker acts as the backend algorithm process and is not part of the mobile ui.

Here come instructions for backend (algorithm):

### macOS/Linux

```bash
cd algorithm
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 run_worker.py
```

### Windows Command Prompt

```bash
cd algorithm
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python run_worker.py
```

## Run Frontend

These are the instructions for UI (frontend):

### macOS/Linux

```bash
cd frontend
python3 -m venv .venv
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
7. Open the Statistics and Recommendation page.
8. The waste ratio and recommendations should appear after the algorithm has processed the data.

## Admin Access

The admin menu is reached from the normal login screen. Log in with the admin Supabase Auth account:

```text
Email: admin@pantrysaver.se
Password: 123456
```

## MAPE Recommendation Loop

The recommendation engine lives in `algorithm/` and runs as a MAPE loop:

- Monitor: find Supabase households where `households.modified = true`
- Analyze: read purchase/discard history and calculate waste ratios
- Plan: choose `ask`, `tip`, or `alert` recommendations using waste ratio, discard frequency, purchase history, recency, item categories, feedback weights, and recommendation score
- Execute: render Supabase `recommendation_templates.template_text` values by replacing `!ITEM!`, then write active rows to `recommendations`

The frontend logs household events, shows active recommendations, and sends feedback that updates `item_intelligence`. Positive feedback marks a recommendation as helpful and can strengthen future recommendations for that item. Negative feedback marks it as not useful and decreases the item weight so similar future recommendations become less likely. Alert feedback also cools down over time: after 30 days the item weight can partly recover, and after 90 days it can reset to the default. The stored recommendation score is used to choose the strongest card type when more than one recommendation could apply to the same item.

The worker runs in the backend. This keeps the frontend responsible for UI only, while the MAPE loop lives in `algorithm/`.

The worker files are split by responsibility:

- `run_worker.py`: terminal entry point; run this file.
- `worker.py`: Supabase orchestration; reads modified households and writes recommendations.
- `algorithm.py`: recommendation planning and scoring logic.
- `db.py`: Supabase client setup.

## Algorithm Worker Usage

Run with default settings:

```bash
python run_worker.py
```

Or configure the intervals:

```bash
python run_worker.py --freq 30 --shortterm 7 --longterm 60
```

| Argument | Default | Description |
|---|---|---|
| `--freq` | 60 | Polling frequency in seconds |
| `--shortterm` | 30 | Short-term analysis window in days |
| `--longterm` | 90 | Long-term analysis window in days |
