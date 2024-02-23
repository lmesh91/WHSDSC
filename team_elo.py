import csv
from math import pow,floor

# IDEA: LOOK AT HOW FAR OFF THE PREDICTIONS ARE FROM ACTUAL GAME OUTCOMES TO ADJUST

team_records = {}

# Initial Elo ratings for each team
INITIAL_RATING = 1500

# K-factor determines how much the Elo ratings change after each match
K_FACTOR = 10

# Home Team Advantage (elo)
HT_ADV = 0

# Weights for different factors
W_SCORE = 0
W_XG = 0
W_SHOTS = 0
W_CORNERS = 0
W_PK_GOAL = 0
W_PK_SHOTS = 0
W_TOP = 0


# Function to calculate the expected score of a team against another
def expected_score(home_rating, away_rating):
    return 1 / (1 + pow(10, (away_rating - (home_rating + HT_ADV)) / 400))

# Function to update Elo ratings based on match results and game factors
def update_ratings(home_rating, away_rating, home_result, home_score, away_score, home_xg, away_xg, home_shots, away_shots, home_corners, away_corners, home_pk_goal, away_pk_goal, home_pk_shots, away_pk_shots, home_top):
    home_expected = expected_score(home_rating, away_rating)
    away_expected = expected_score(away_rating, home_rating)

    # Calculate weightings for game factors
    home_factor = 1 + W_SCORE * (home_score - away_score) + W_XG * (home_xg - away_xg) + W_SHOTS * (home_shots - away_shots) + W_CORNERS * (home_corners - away_corners) + W_PK_GOAL * (home_pk_goal - away_pk_goal) + W_PK_SHOTS * (home_pk_shots - away_pk_shots) + W_TOP * home_top
    away_factor = 1 + W_SCORE * (away_score - home_score) + W_XG * (away_xg - home_xg) + W_SHOTS * (away_shots - home_shots) + W_CORNERS * (away_corners - home_corners) + W_PK_GOAL * (away_pk_goal - home_pk_goal) + W_PK_SHOTS * (away_pk_shots - home_pk_shots) + W_TOP * (1 - home_top)

    if home_result == 1:  # Home team wins
        home_score = 1
        away_score = 0
    elif home_result == 0.5:  # Draw
        home_score = 0.5
        away_score = 0.5
    else:  # Away team wins
        home_score = 0
        away_score = 1

    # Update Elo ratings based on game factors and match result
    home_new_rating = home_rating + K_FACTOR * (home_score - home_expected) * home_factor
    away_new_rating = away_rating + K_FACTOR * (away_score - away_expected) * away_factor

    return home_new_rating, away_new_rating

# Function to read match data from CSV file and update Elo ratings
def update_elo_from_csv(csv_file):
    team_ratings = {}

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            home_team = row['HomeTeam']
            away_team = row['AwayTeam']
            home_xg = float(row['Home_xG'])
            away_xg = float(row['Away_xG'])
            home_shots = int(row['Home_shots'])
            away_shots = int(row['Away_shots'])
            home_corners = int(row['Home_corner'])
            away_corners = int(row['Away_corner'])
            home_pk_goal = int(row['Home_PK_Goal'])
            away_pk_goal = int(row['Away_PK_Goal'])
            home_pk_shots = int(row['Home_PK_shots'])
            away_pk_shots = int(row['Away_PK_shots'])
            home_top = float(row['Home_ToP'])
            home_score = int(row['HomeScore'])
            away_score = int(row['AwayScore'])

            if home_team not in team_ratings:
                team_ratings[home_team] = INITIAL_RATING
            if away_team not in team_ratings:
                team_ratings[away_team] = INITIAL_RATING
            if home_team not in team_records:
                team_records[home_team] = 0
            if away_team not in team_records:
                team_records[away_team] = 0

            home_rating = team_ratings[home_team]
            away_rating = team_ratings[away_team]

            home_result = 1 if home_score > away_score else (0.5 if home_score == away_score else 0)

            if (home_result == 1):
                team_records[home_team] += 3
            if (home_result == 0):
                team_records[away_team] += 3
            if (home_result == 0.5):
                team_records[home_team] += 1
                team_records[away_team] += 1

            home_new_rating, away_new_rating = update_ratings(home_rating, away_rating, home_result, home_score, away_score, home_xg, away_xg, home_shots, away_shots, home_corners, away_corners, home_pk_goal, away_pk_goal, home_pk_shots, away_pk_shots, home_top)

            team_ratings[home_team] = home_new_rating
            team_ratings[away_team] = away_new_rating

    return team_ratings

# Function to make predictions based on Elo ratings
def make_predictions(csv_file, team_ratings):
    correct_predictions = 0
    total_games = 0

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            home_team = row['HomeTeam']
            away_team = row['AwayTeam']
            home_rating = team_ratings[home_team]
            away_rating = team_ratings[away_team]
            home_record = team_records[home_team]
            away_record = team_records[away_team]
            home_score = int(row['HomeScore'])
            away_score = int(row['AwayScore'])
            print(f"{home_team} ({floor(home_rating)}) {home_score} - {away_score} ({floor(away_rating)}) {away_team}")

            # Predict the outcome based on Elo ratings
            K = 1000
            home_expected = expected_score(home_rating, away_rating)
            #home_expected = expected_score(home_record*K, away_record*K)
            #print(home_expected)

            # Compare prediction with actual outcome
            if (home_score > away_score):
                #correct_predictions += 1 if home_expected > 0.5 else 0
                correct_predictions += home_expected
            if (home_score < away_score):
                #correct_predictions += 0 if home_expected > 0.5 else 1
                correct_predictions += 1-home_expected
            if (home_score == away_score):
                #correct_predictions += 0.5
                correct_predictions += 1 - (2 * abs(home_expected - 0.5))

            total_games += 1

    return correct_predictions, total_games

def write_ratings_to_csv(ratings, output_file):
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Team', 'Elo Rating'])
        for team, rating in ratings.items():
            writer.writerow([team, rating])

def main():
    csv_file = "NSL_regular_season_data_2.csv"#input("Enter the path to the CSV file: ")
    output_file = "NSL_elo.csv"#input("Enter the path to the output CSV file: ")
    try:
        team_ratings = update_elo_from_csv(csv_file)
        correct_predictions, total_games = make_predictions(csv_file, team_ratings)
        write_ratings_to_csv(team_ratings, output_file)
        print(f"Regular season games predicted correctly: {correct_predictions}/{total_games} ({100*correct_predictions/total_games}%)")
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
