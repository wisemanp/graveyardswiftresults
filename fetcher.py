import requests
from bs4 import BeautifulSoup
import pandas as pd
import subprocess
import os
import sys 

def fetch_results():
    with open('/Users/pwise/Library/Mobile Documents/com~apple~CloudDocs/teamId.txt', 'r') as file:
        team_id = file.read().strip()
        print('Team ID:', team_id)
        if team_id == 'test':
            test = True
            team_id = '539296'
    if test:
        url = "https://results.resultsbase.net/myresults.aspx?CId=8&RId=20442&EId=1&AId=539296"
    else:
        url = f"https://results.resultsbase.net/myresults.aspx?CId=8&RId=20854&EId=1&AId={team_id}"
    print('Fetching results from:', url)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        html = ""
    soup = BeautifulSoup(html, "html.parser")
    
    # Extract table data
    tables = soup.find_all("table", class_="table table-bordered table-sm small")
    print('Found tables:', len(tables))
    target_table = tables[0]
    rows = target_table.find_all("tr")
    
    data = []
    for row in rows[1:]:  # Skip header
        cols = row.find_all("td")
        if len(cols) < 3:
            continue
        name_raw = cols[0].get_text(separator="\n").strip()
        leg_label, name = name_raw.split("\n") if "\n" in name_raw else (name_raw, "")
        leg_time = cols[2].get_text(strip=True)
        data.append({
            "Lap": leg_label.replace("Lap ", "").strip(),
            "Runner": name.strip("() "),
            "Leg Time": leg_time
        })
    
    # If this is a test, limit the data to simulate halfway-through-the-race
    #if test:
        #halfway_index = len(data) // 2
        #data = data[:halfway_index]
    print('GOT DATA', data)
    return pd.DataFrame(data)

def push_results_to_github(repo_path, filename="results.csv"):
    """
    Save data as JSON to filename inside repo_path, commit, and push to GitHub.
    """
    print("Pushing results to GitHub...")
    print("Current working directory:", os.getcwd())
    print('Repo path:', repo_path)
    os.chdir(repo_path)
    print("Current working directory:", os.getcwd())
    print('Filename:', filename)
    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Update relay results"], cwd=repo_path, check=True)
        subprocess.run(["git", "push"], cwd=repo_path, check=True)
        print("Pushed updated results to GitHub")
    except subprocess.CalledProcessError as e:
        print("Git command failed:", e)


   

if __name__ == "__main__":
    results = fetch_results()
    print("Fetched results:", results)
    results.to_csv('results.csv', index=False)  # Save results to a CSV file
    push_results_to_github(repo_path='/Users/pwise/data/running/endure/results/graveyardswiftresults/')
    # You can add code here to process the results further or save them to a file
