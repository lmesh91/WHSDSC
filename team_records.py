import csv

def calculate_record(csv_file):
    records = {}

    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            home_team = row['HomeTeam']
            away_team = row['AwayTeam']
            home_score = int(row['HomeScore'])
            away_score = int(row['AwayScore'])

            # Update records for home team
            if home_team not in records:
                records[home_team] = {'wins': 0, 'draws': 0, 'losses': 0}
            if home_score > away_score:
                records[home_team]['wins'] += 1
            elif home_score == away_score:
                records[home_team]['draws'] += 1
            else:
                records[home_team]['losses'] += 1

            # Update records for away team
            if away_team not in records:
                records[away_team] = {'wins': 0, 'draws': 0, 'losses': 0}
            if away_score > home_score:
                records[away_team]['wins'] += 1
            elif away_score == home_score:
                records[away_team]['draws'] += 1
            else:
                records[away_team]['losses'] += 1

    return records

def write_records_to_csv(records, output_file):
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Team', 'Wins', 'Draws', 'Losses'])
        for team, record in records.items():
            writer.writerow([team, record['wins'], record['draws'], record['losses']])

def main():
    csv_file = input("Enter the path to the CSV file: ")
    output_file = input("Enter the path to the output CSV file: ")
    try:
        records = calculate_record(csv_file)
        write_records_to_csv(records, output_file)
        print("Team records have been written to", output_file)
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()
