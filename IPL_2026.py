import pandas as pd
df = pd.read_csv('ipl_2026_deliveries.csv')
print(df.shape)
print(df.columns)
print(df.head())
df.isnull().sum()
df.duplicated().sum()
df["total_runs"]= df["runs_of_bat"] + df["extras"]

def over_phase(over):
    if over <= 6:
        return 'Powerplay'
    elif over <= 15:
        return 'Middle'
    else:
        return 'Death'
df['over_phase'] = df['over'].apply(over_phase)

df['is_wicket'] = df['player_dismissed'].notna().astype(int)
print(df[['total_runs', 'over_phase', 'is_wicket']].head())

team_runs = (
    df.groupby('batting_team')['total_runs'].sum().sort_values(ascending=False)
)
print(team_runs)

team_wickets = (
    df.groupby('bowling_team')['is_wicket'].sum().sort_values(ascending=False)
)
print(team_wickets)

powerplay_runs = (
    df[df['over_phase'] == 'Powerplay'].groupby('batting_team')['total_runs'].sum().sort_values(ascending=False)
)
print(powerplay_runs)

death_runs = (
    df[df['over_phase'] == 'Death'].groupby('batting_team')['total_runs'].sum().sort_values(ascending=False)
)
print(death_runs)

top_batters = (
    df.groupby('striker')['runs_of_bat'].sum().sort_values(ascending=False).head(10)
)
print(top_batters)

top_bowlers = (
    df.groupby("bowler")["is_wicket"].sum().sort_values(ascending=False).head(10)
)
print(top_bowlers)

balls_faced = (
    df[(df['wide'] == 0 )].groupby('striker').size().sort_values(ascending=False)
)
print(balls_faced)

batter_runs = df.groupby('striker')['runs_of_bat'].sum()

strike_rate = (
(batter_runs / balls_faced) * 100).sort_values(ascending=False)

qualified_batters = strike_rate[balls_faced >= 100].sort_values(ascending=False)
print(qualified_batters.head(10))

# Runs conceded
bowler_runs = (
    df.groupby('bowler')['total_runs']
    .sum()
)


balls_bowled = (
    df[
        (df['wide'] == 0) &
        (df['noballs'] == 0)
    ]
    .groupby('bowler')
    .size()
)

overs_bowled = balls_bowled / 6
economy = bowler_runs / overs_bowled
qualified_bowlers = economy[
    overs_bowled >= 10
].sort_values()

print(qualified_bowlers.head(10))

rcb_matches = df[
    (df['batting_team'] == 'RCB') |
    (df['bowling_team'] == 'RCB')
]

print(rcb_matches.head())

match_summary = (
    df.groupby(["match_id", "batting_team"])
    .agg(
        total_runs=('total_runs','sum'),
        wickets=('is_wicket','sum')
    )
    .reset_index()
)
print(match_summary.head())

rcb_summary = (
    match_summary[match_summary['batting_team'] == 'RCB']

)
print(rcb_summary)
print(rcb_summary['total_runs'].describe())

team_metrics = (
    df.groupby('batting_team')
    .agg(
        total_runs=('total_runs', 'sum'),
        total_wickets_lost=('is_wicket', 'sum'),
        total_boundaries=('runs_of_bat',
                          lambda x: ((x == 4) | (x == 6)).sum()),
        total_sixes=('runs_of_bat',
                      lambda x: (x == 6).sum()),
        avg_runs_per_ball=('total_runs', 'mean')
    )
    .reset_index()
)

print(team_metrics)

bowling_metrics = (
    df.groupby('bowling_team')
    .agg(
        wickets_taken=('is_wicket', 'sum'),
        runs_conceded=('total_runs', 'sum')
    )
    .reset_index()
)

print(bowling_metrics)

team_analysis = pd.merge(
    team_metrics,
    bowling_metrics,
    left_on='batting_team',
    right_on='bowling_team'
)

team_analysis.drop(columns=['bowling_team'], inplace=True)

print(team_analysis)

rcb_analysis = team_analysis[
    team_analysis['batting_team'] == 'RCB'
]

print(rcb_analysis.T)

final_df = df.copy()

final_df['is_boundary'] = (
    (final_df['runs_of_bat'] == 4) |
    (final_df['runs_of_bat'] == 6)
).astype(int)

final_df['is_six'] = (
    final_df['runs_of_bat'] == 6
).astype(int)

final_df['is_dot_ball'] = (
    final_df['total_runs'] == 0
).astype(int)

final_df['is_legal_ball'] = (
    (final_df['wide'] == 0) &
    (final_df['noballs'] == 0)
).astype(int)

final_df.to_csv(
    "ipl_2026_cleaned.csv",
    index=False
)

print("Clean dataset exported successfully!")