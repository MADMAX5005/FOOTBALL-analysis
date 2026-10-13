import numpy as np
import pandas as pd

np.random.seed(42)

clubs = [
    'FC Zenith', 'Athletic United', 'City Rovers', 'Dynamo FC',
    'Red Star SC', 'Northern Vale', 'Coastal FC', 'Iron Bridge FC',
    'Summit City', 'Riverside Athletic'
]
nationalities = [
    'English', 'Spanish', 'French', 'Brazilian', 'German', 'Italian',
    'Argentine', 'Dutch', 'Portuguese', 'Belgian', 'Nigerian',
    'Senegalese', 'Japanese', 'Mexican', 'Colombian'
]
seasons = ['2022-23', '2023-24']

# 2 GK + 6 DEF + 6 MID + 4 FWD = 18 players per club × 10 clubs = 180 players
pos_counts = {'GK': 2, 'DEF': 6, 'MID': 6, 'FWD': 4}

first_names = [
    'Luca','Carlos','James','Mohamed','David','Andre','Paulo','Kenji','Diego','Marco',
    'Finn','Ibrahim','Oliver','Rafael','Sergio','Toni','Luis','Emil','Henri','Ryan',
    'Jordan','Alexei','Yusuf','Stefan','Matteo','Gabriel','Tom','Eric','Owen','Leon',
    'Nathan','Kevin','Nico','Pierre','Sam','Alex','Ben','Max','Noah','Jake',
    'Ethan','Adam','Amir','Takuya','Rui','Jakub','Sven','Koen','Artur','Mehdi',
    'Dante','Victor','Hugo','Felix','Elias','Simon','Oscar','Cian','Ronan','Zach',
]
last_names = [
    'Silva','Costa','Müller','Dubois','Rossi','Fernandez','Santos','Nakamura','García','Taylor',
    'Johnson','Martin','Lopez','Andersen','Novak','Becker','Diallo','Okafor','Mensah','Berg',
    'Nguyen','Reyes','Castro','Petit','Kowalski','Moura','Vargas','Mota','Dembele','Kane',
    'Suarez','Benzema','Ramos','Alves','Neves','Cruz','Pinto','Fonseca','Guerreiro','Salah',
    'Mane','Keane','Giggs','Scholes','Vieira','Pirlo','Zola','Cafu','Roberto','Litmanen',
    'Herrera','Romero','Falcao','Vidal','Thiago','Modric','Kroos','Busquets','Iniesta','Xavi',
]

used_names = set()

def unique_name():
    while True:
        fn = first_names[np.random.randint(len(first_names))]
        ln = last_names[np.random.randint(len(last_names))]
        name = f'{fn} {ln}'
        if name not in used_names:
            used_names.add(name)
            return name

# Build player roster (same players appear in both seasons)
roster = []
pid = 1
for club in clubs:
    for pos, count in pos_counts.items():
        for _ in range(count):
            roster.append({
                'player_id':   pid,
                'player_name': unique_name(),
                'age':         int(np.random.randint(18, 36)),
                'nationality': nationalities[np.random.randint(len(nationalities))],
                'team':        club,
                'position':    pos,
            })
            pid += 1

# Stat ranges keyed by position
stat_ranges = {
    'GK':  {
        'goals': (0, 1),   'assists': (0, 1),
        'shots': (0, 2),   'shots_on_target': (0, 1),
        'passes': (300, 700), 'pass_acc': (0.65, 0.82),
        'dribbles': (0, 3),  'tackles': (5, 25),
    },
    'DEF': {
        'goals': (0, 5),   'assists': (0, 7),
        'shots': (2, 25),  'shots_on_target': (1, 12),
        'passes': (500, 900), 'pass_acc': (0.72, 0.90),
        'dribbles': (5, 30),  'tackles': (30, 90),
    },
    'MID': {
        'goals': (1, 14),  'assists': (2, 16),
        'shots': (10, 70), 'shots_on_target': (4, 35),
        'passes': (700, 1200), 'pass_acc': (0.78, 0.93),
        'dribbles': (15, 70),  'tackles': (20, 70),
    },
    'FWD': {
        'goals': (3, 30),   'assists': (1, 14),
        'shots': (20, 120), 'shots_on_target': (8, 60),
        'passes': (200, 600), 'pass_acc': (0.62, 0.84),
        'dribbles': (20, 80), 'tackles': (5, 30),
    },
}

rows = []
for season in seasons:
    for p in roster:
        pos = p['position']
        sr  = stat_ranges[pos]

        matches  = int(np.random.randint(12, 38))
        avg_min  = np.random.uniform(45, 90)
        minutes  = int(min(matches * avg_min, matches * 90))

        goals   = int(np.random.randint(sr['goals'][0],   sr['goals'][1]   + 1))
        assists = int(np.random.randint(sr['assists'][0], sr['assists'][1] + 1))
        shots   = int(np.random.randint(max(sr['shots'][0], goals), sr['shots'][1] + 1))
        sot_hi  = min(shots + 1, sr['shots_on_target'][1] + 1)
        sot_lo  = min(goals, shots)
        sot     = int(np.random.randint(sot_lo, max(sot_lo + 1, sot_hi)))
        passes   = int(np.random.randint(sr['passes'][0], sr['passes'][1]   + 1))
        pass_acc = round(float(np.random.uniform(sr['pass_acc'][0], sr['pass_acc'][1])), 3)
        dribbles = int(np.random.randint(sr['dribbles'][0], sr['dribbles'][1] + 1))
        tackles  = int(np.random.randint(sr['tackles'][0],  sr['tackles'][1]  + 1))
        yellows  = int(np.random.randint(0, 8))
        reds     = int(np.random.randint(0, 2))

        # Weighted composite rating in range 5.0–9.5
        g_denom  = sr['goals'][1]   if sr['goals'][1]   > 0 else 1
        a_denom  = sr['assists'][1] if sr['assists'][1] > 0 else 1
        g_norm   = goals   / g_denom
        a_norm   = assists / a_denom
        t_norm   = tackles / sr['tackles'][1]
        card_pen = yellows * 0.05 + reds * 0.20
        raw      = 0.35 * g_norm + 0.25 * a_norm + 0.25 * pass_acc + 0.15 * t_norm - card_pen
        rating   = round(max(5.0, min(9.5, 5.0 + raw * 4.5)), 2)

        rows.append({
            'player_id':       p['player_id'],
            'player_name':     p['player_name'],
            'age':             p['age'],
            'nationality':     p['nationality'],
            'team':            p['team'],
            'position':        p['position'],
            'season':          season,
            'matches_played':  matches,
            'minutes_played':  minutes,
            'goals':           goals,
            'assists':         assists,
            'shots':           shots,
            'shots_on_target': sot,
            'passes':          passes,
            'pass_accuracy':   pass_acc,
            'dribbles':        dribbles,
            'tackles':         tackles,
            'yellow_cards':    yellows,
            'red_cards':       reds,
            'rating':          rating,
        })

df = pd.DataFrame(rows)
df.to_csv('football_players.csv', index=False)
print(f'Generated {len(df)} rows, {df["player_id"].nunique()} unique players, {df["season"].nunique()} seasons')
print(df['position'].value_counts().to_string())
print(df[['goals','assists','rating']].describe().round(2).to_string())
