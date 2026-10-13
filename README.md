# ⚽ Football Player Performance Analytics Dashboard

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red?logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.18%2B-3F4F75?logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green)

> **⚠️ SYNTHETIC DATA NOTICE**
> All player names, club names, nationalities, and statistics in this dashboard are
> **entirely synthetic** and generated with `numpy.random.seed(42)` for reproducibility.
> They do **not** represent real-world football players, clubs, or results.
> Do not cite or interpret any figure as a real-world football statistic.

---

## 📋 Project Overview

An interactive, portfolio-quality football (soccer) analytics dashboard built with
**Python + Streamlit**. It lets you explore, filter, compare, and download synthetic
player statistics across five pages:

| Page | What it shows |
|---|---|
| **Overview** | 5 KPI cards, Goals by Team, Top 10 by Rating |
| **Player Analysis** | Side-by-side comparison, Goals vs Assists scatter, Shots vs Goals scatter |
| **Team Analysis** | Goals, Assists, Squad size, Avg Rating — all per club |
| **Position Analysis** | Goals/Assists by role, Rating distribution box plot, Position pie |
| **Data Table** | Searchable + sortable raw stats with CSV download |

---

## 🗂️ Project Structure

```
football-dashboard/
├── app.py                  # Main Streamlit application
├── football_players.csv    # Synthetic dataset (360 rows × 20 columns)
├── generate_data.py        # Script to regenerate the dataset
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## 📊 Dataset Schema

File: `football_players.csv` — **synthetic, seed = 42**

| Column | Type | Description |
|---|---|---|
| player_id | int | Unique player identifier |
| player_name | str | Synthetic full name |
| age | int | 18–35 |
| nationality | str | Synthetic country |
| team | str | One of 10 synthetic clubs |
| position | str | GK / DEF / MID / FWD |
| season | str | 2022-23 or 2023-24 |
| matches_played | int | 12–38 |
| minutes_played | int | Derived from matches × avg minutes |
| goals | int | Position-appropriate range |
| assists | int | Position-appropriate range |
| shots | int | ≥ goals |
| shots_on_target | int | ≤ shots |
| passes | int | Position-appropriate range |
| pass_accuracy | float | 0.62–0.93 |
| dribbles | int | Position-appropriate range |
| tackles | int | Higher for DEF/MID |
| yellow_cards | int | 0–7 |
| red_cards | int | 0–1 |
| rating | float | 5.0–9.5 (weighted composite) |

**Rating formula (all values normalised to 0–1):**
```
rating = 5.0 + (0.35 × goals_norm + 0.25 × assists_norm + 0.25 × pass_accuracy + 0.15 × tackles_norm − card_penalty) × 4.5
```

---

## 🚀 Setup and Run Locally

### Prerequisites

- Python 3.9 or higher
- `pip` package manager

### Steps

```bash
# 1. Clone or download the project
git clone https://github.com/your-username/football-dashboard.git
cd football-dashboard

# 2. (Optional) Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Regenerate the dataset
py generate_data.py        # Windows
# or
python generate_data.py    # macOS / Linux

# 5. Launch the dashboard
streamlit run app.py
```

The app opens automatically in your browser at **http://localhost:8501**.

---

## ☁️ Deploy to Streamlit Community Cloud

1. Push the project to a **public GitHub repository**.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **"New app"** → select your repo, branch (`main`), and set the main file to `app.py`.
4. Click **"Deploy"** — Streamlit Cloud reads `requirements.txt` automatically.
5. Your dashboard will be live at `https://<your-app>.streamlit.app` within minutes.

> No extra configuration files are needed; `requirements.txt` at the repo root is sufficient.

---

## 🎨 Features

- **Dark, modern football-inspired UI** — `#0d1117` background, `#00ff87` green accent
- **Global sidebar filters** — Season, Team, Position, Player (multi-select)
- **Live KPIs** — all five metric cards recalculate from the filtered DataFrame
- **Interactive Plotly charts** — hover tooltips, zoom, pan, download PNG
- **Searchable data table** — filter rows by player name substring
- **CSV download** — one-click export of the currently filtered & searched data
- **Input validation** — empty filter result shows a warning and halts rendering
- **Reproducible data** — `numpy.random.seed(42)` guarantees identical dataset on every run

---

## 🛠️ Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.9+ | Runtime |
| Streamlit | ≥1.32 | Web framework / UI |
| Pandas | ≥2.0 | Data manipulation |
| NumPy | ≥1.26 | Dataset generation |
| Plotly | ≥5.18 | Interactive charts |

---

## 📄 License

MIT — free to use, modify, and distribute. Attribution appreciated.
