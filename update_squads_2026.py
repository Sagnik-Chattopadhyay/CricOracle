import json
from db import SessionLocal
from models import Player, Team
from sqlalchemy import text

# Consolidate the 2026 data scraped from ESPNcricinfo
# IPL 2026 squads + India/International T20 2026 squads

SQUAD_DATA = {
    "FRANCHISE": {
        "Chennai Super Kings": [
            {"name": "Ruturaj Gaikwad", "role": "Batter (c)"}, 
            {"name": "Dewald Brevis", "role": "Middle order Batter"}, 
            {"name": "MS Dhoni", "role": "Wicketkeeper Batter"}, 
            {"name": "Kartik Sharma", "role": "Wicketkeeper Batter"}, 
            {"name": "Sarfaraz Khan", "role": "Middle order Batter"}, 
            {"name": "Ayush Mhatre", "role": "Top order Batter"}, 
            {"name": "Urvil Patel", "role": "Wicketkeeper Batter"}, 
            {"name": "Sanju Samson", "role": "Wicketkeeper Batter"}, 
            {"name": "Aman Khan", "role": "Allrounder"}, 
            {"name": "Shivam Dube", "role": "Allrounder"}, 
            {"name": "Zak Foulkes", "role": "Allrounder"}, 
            {"name": "Ramakrishna Ghosh", "role": "Bowling Allrounder"}, 
            {"name": "Anshul Kamboj", "role": "Bowling Allrounder"}, 
            {"name": "Jamie Overton", "role": "Bowling Allrounder"}, 
            {"name": "Matthew Short", "role": "Batting Allrounder"}, 
            {"name": "Prashant Veer", "role": "Bowling Allrounder"}, 
            {"name": "Khaleel Ahmed", "role": "Bowler"}, 
            {"name": "Rahul Chahar", "role": "Bowler"}, 
            {"name": "Shreyas Gopal", "role": "Bowler"}, 
            {"name": "Gurjapneet Singh", "role": "Bowler"}, 
            {"name": "Matt Henry", "role": "Bowler"}, 
            {"name": "Akeal Hosein", "role": "Bowler"}, 
            {"name": "Spencer Johnson", "role": "Bowler"}, 
            {"name": "Mukesh Choudhary", "role": "Bowler"}
        ],
        "Mumbai Indians": [
            {"name": "Hardik Pandya", "role": "Allrounder (c)"}, 
            {"name": "Quinton de Kock", "role": "Wicketkeeper Batter"}, 
            {"name": "Danish Malewar", "role": "Middle order Batter"}, 
            {"name": "Robin Minz", "role": "Wicketkeeper Batter"}, 
            {"name": "Ryan Rickelton", "role": "Wicketkeeper Batter"}, 
            {"name": "Sherfane Rutherford", "role": "Middle order Batter"}, 
            {"name": "Rohit Sharma", "role": "Batter"}, 
            {"name": "Suryakumar Yadav", "role": "Batter"}, 
            {"name": "Atharva Ankolekar", "role": "Allrounder"}, 
            {"name": "Raj Bawa", "role": "Allrounder"}, 
            {"name": "Corbin Bosch", "role": "Allrounder"}, 
            {"name": "Will Jacks", "role": "Allrounder"}, 
            {"name": "Mayank Rawat", "role": "Allrounder"}, 
            {"name": "Naman Dhir", "role": "Allrounder"}, 
            {"name": "Mitchell Santner", "role": "Allrounder"}, 
            {"name": "Shardul Thakur", "role": "Allrounder"}, 
            {"name": "Tilak Varma", "role": "Allrounder"}, 
            {"name": "Ashwani Kumar", "role": "Bowler"}, 
            {"name": "Trent Boult", "role": "Bowler"}, 
            {"name": "Jasprit Bumrah", "role": "Bowler"}, 
            {"name": "Deepak Chahar", "role": "Bowler"}, 
            {"name": "AM Ghazanfar", "role": "Bowler"}, 
            {"name": "Mayank Markande", "role": "Bowler"}, 
            {"name": "Vijaykumar Vyshak", "role": "Bowler"}, 
            {"name": "Mohd Izhar", "role": "Bowler"}, 
            {"name": "Raghu Sharma", "role": "Bowler"}
        ],
        "Royal Challengers Bengaluru": [
            {"name": "Rajat Patidar", "role": "Top order Batter (c)"}, 
            {"name": "Jordan Cox", "role": "Wicketkeeper Batter"}, 
            {"name": "Tim David", "role": "Middle order Batter"}, 
            {"name": "Virat Kohli", "role": "Top order Batter"}, 
            {"name": "Devdutt Padikkal", "role": "Top order Batter"}, 
            {"name": "Phil Salt", "role": "Wicketkeeper Batter"}, 
            {"name": "Jitesh Sharma", "role": "Wicketkeeper Batter"}, 
            {"name": "Jacob Bethell", "role": "Batting Allrounder"}, 
            {"name": "Kanishk Chouhan", "role": "Bowling Allrounder"}, 
            {"name": "Venkatesh Iyer", "role": "Allrounder"}, 
            {"name": "Vihaan Malhotra", "role": "Batting Allrounder"}, 
            {"name": "Mangesh Yadav", "role": "Allrounder"}, 
            {"name": "Krunal Pandya", "role": "Allrounder"}, 
            {"name": "Romario Shepherd", "role": "Bowling Allrounder"}, 
            {"name": "Abhinandan Singh", "role": "Bowler"}, 
            {"name": "Satvik Deswal", "role": "Bowler"}, 
            {"name": "Jacob Duffy", "role": "Bowler"}, 
            {"name": "Josh Hazlewood", "role": "Bowler"}, 
            {"name": "Bhuvneshwar Kumar", "role": "Bowler"}, 
            {"name": "Vicky Ostwal", "role": "Bowler"}, 
            {"name": "Rasikh Salam", "role": "Bowler"}, 
            {"name": "Suyash Sharma", "role": "Bowler"}
        ],
        "Kolkata Knight Riders": [
            {"name": "Ajinkya Rahane", "role": "Top order Batter (c)"}, 
            {"name": "Rinku Singh", "role": "Middle order Batter (vc)"}, 
            {"name": "Finn Allen", "role": "Top order Batter"}, 
            {"name": "Tejasvi Dahiya", "role": "Wicketkeeper Batter"}, 
            {"name": "Manish Pandey", "role": "Top order Batter"}, 
            {"name": "Rovman Powell", "role": "Middle order Batter"}, 
            {"name": "Angkrish Raghuvanshi", "role": "Top order Batter"}, 
            {"name": "Ramandeep Singh", "role": "Middle order Batter"}, 
            {"name": "Sarthak Ranjan", "role": "Opening Batter"}, 
            {"name": "Tim Seifert", "role": "Wicketkeeper Batter"}, 
            {"name": "Rahul Tripathi", "role": "Top order Batter"}, 
            {"name": "Sunil Narine", "role": "Bowling Allrounder"}, 
            {"name": "Rachin Ravindra", "role": "Batting Allrounder"}, 
            {"name": "Anukul Roy", "role": "Allrounder"}, 
            {"name": "Daksh Kamra", "role": "Allrounder"}, 
            {"name": "Vaibhav Arora", "role": "Bowler"}, 
            {"name": "Saurabh Dubey", "role": "Bowler"}, 
            {"name": "Kartik Tyagi", "role": "Bowler"}, 
            {"name": "Blessing Muzarabani", "role": "Bowler"}, 
            {"name": "Matheesha Pathirana", "role": "Bowler"}, 
            {"name": "Navdeep Saini", "role": "Bowler"}, 
            {"name": "Cameron Green", "role": "Allrounder"}
        ],
        "Rajasthan Royals": [
            {"name": "Riyan Parag", "role": "Top order Batter (c)"}, 
            {"name": "Aman Rao", "role": "Opening Batter"}, 
            {"name": "Shubham Dubey", "role": "Middle order Batter"}, 
            {"name": "Shimron Hetmyer", "role": "Middle order Batter"}, 
            {"name": "Yashasvi Jaiswal", "role": "Opening Batter"}, 
            {"name": "Dhruv Jurel", "role": "Wicketkeeper Batter"}, 
            {"name": "Lhuan-dre Pretorius", "role": "Wicketkeeper Batter"}, 
            {"name": "Ravi Singh", "role": "Middle order Batter"}, 
            {"name": "Vaibhav Sooryavanshi", "role": "Top order Batter"}, 
            {"name": "Donovan Ferreira", "role": "Allrounder"}, 
            {"name": "Ravindra Jadeja", "role": "Allrounder"}, 
            {"name": "Dasun Shanaka", "role": "Allrounder"}, 
            {"name": "Jofra Archer", "role": "Bowler"}, 
            {"name": "Brijesh Sharma", "role": "Bowler"}, 
            {"name": "Nandre Burger", "role": "Bowler"}, 
            {"name": "Tushar Deshpande", "role": "Bowler"}, 
            {"name": "Kwena Maphaka", "role": "Bowler"}, 
            {"name": "Adam Milne", "role": "Bowler"}, 
            {"name": "Sushant Mishra", "role": "Bowler"}, 
            {"name": "Vignesh Puthur", "role": "Bowler"}, 
            {"name": "Ravi Bishnoi", "role": "Bowler"}, 
            {"name": "Sandeep Sharma", "role": "Bowler"}
        ],
        "Delhi Capitals": [
            {"name": "Axar Patel", "role": "Allrounder (c)"}, 
            {"name": "Abishek Porel", "role": "Wicketkeeper Batter"}, 
            {"name": "David Miller", "role": "Middle order Batter"}, 
            {"name": "Karun Nair", "role": "Top order Batter"}, 
            {"name": "Pathum Nissanka", "role": "Top order Batter"}, 
            {"name": "Sahil Parakh", "role": "Top order Batter"}, 
            {"name": "KL Rahul", "role": "Wicketkeeper Batter"}, 
            {"name": "Nitish Rana", "role": "Middle order Batter"}, 
            {"name": "Prithvi Shaw", "role": "Opening Batter"}, 
            {"name": "Tristan Stubbs", "role": "Wicketkeeper Batter"}, 
            {"name": "Sameer Rizvi", "role": "Allrounder"}, 
            {"name": "Ashutosh Sharma", "role": "Batting Allrounder"}, 
            {"name": "Madhav Tiwari", "role": "Allrounder"}, 
            {"name": "Auqib Nabi", "role": "Bowler"}, 
            {"name": "Dushmantha Chameera", "role": "Bowler"}, 
            {"name": "Kyle Jamieson", "role": "Bowler"}, 
            {"name": "Kuldeep Yadav", "role": "Bowler"}, 
            {"name": "Mukesh Kumar", "role": "Bowler"}, 
            {"name": "T Natarajan", "role": "Bowler"}, 
            {"name": "Lungi Ngidi", "role": "Bowler"}, 
            {"name": "Vipraj Nigam", "role": "Bowler"}
        ],
        "Punjab Kings": [
            {"name": "Shreyas Iyer", "role": "Top order Batter (c)"}, 
            {"name": "Priyansh Arya", "role": "Opening Batter"}, 
            {"name": "Pyla Avinash", "role": "Batter"}, 
            {"name": "Harnoor Singh", "role": "Batter"}, 
            {"name": "Prabhsimran Singh", "role": "Wicketkeeper Batter"}, 
            {"name": "Vishnu Vinod", "role": "Wicketkeeper Batter"}, 
            {"name": "Nehal Wadhera", "role": "Top order Batter"}, 
            {"name": "Azmatullah Omarzai", "role": "Allrounder"}, 
            {"name": "Cooper Connolly", "role": "Batting Allrounder"}, 
            {"name": "Marco Jansen", "role": "Bowling Allrounder"}, 
            {"name": "Musheer Khan", "role": "Allrounder"}, 
            {"name": "Mitchell Owen", "role": "Allrounder"}, 
            {"name": "Shashank Singh", "role": "Batting Allrounder"}, 
            {"name": "Marcus Stoinis", "role": "Batting Allrounder"}, 
            {"name": "Suryansh Shedge", "role": "Batting Allrounder"}, 
            {"name": "Arshdeep Singh", "role": "Bowler"}, 
            {"name": "Xavier Bartlett", "role": "Bowler"}, 
            {"name": "Yuzvendra Chahal", "role": "Bowler"}, 
            {"name": "Praveen Dubey", "role": "Bowler"}, 
            {"name": "Ben Dwarshuis", "role": "Bowler"}, 
            {"name": "Lockie Ferguson", "role": "Bowler"}, 
            {"name": "Harpreet Brar", "role": "Bowler"}
        ],
        "Gujarat Titans": [
            {"name": "Shubman Gill", "role": "Top order Batter (c)"}, 
            {"name": "Anuj Rawat", "role": "Wicketkeeper Batter"}, 
            {"name": "Tom Banton", "role": "Wicketkeeper Batter"}, 
            {"name": "Jos Buttler", "role": "Wicketkeeper Batter"}, 
            {"name": "Kumar Kushagra", "role": "Wicketkeeper Batter"}, 
            {"name": "Sai Sudharsan", "role": "Top order Batter"}, 
            {"name": "M Shahrukh Khan", "role": "Batter"}, 
            {"name": "Jason Holder", "role": "Bowling Allrounder"}, 
            {"name": "Glenn Phillips", "role": "Allrounder"}, 
            {"name": "Rashid Khan", "role": "Bowling Allrounder"}, 
            {"name": "Nishant Sindhu", "role": "Allrounder"}, 
            {"name": "Manav Suthar", "role": "Bowling Allrounder"}, 
            {"name": "Rahul Tewatia", "role": "Bowling Allrounder"}, 
            {"name": "Washington Sundar", "role": "Bowling Allrounder"}, 
            {"name": "Arshad Khan", "role": "Bowler"}, 
            {"name": "Ashok Sharma", "role": "Bowler"}, 
            {"name": "Gurnoor Brar", "role": "Bowler"}, 
            {"name": "Kulwant Khejroliya", "role": "Bowler"}, 
            {"name": "Mohammed Siraj", "role": "Bowler"}, 
            {"name": "Prasidh Krishna", "role": "Bowler"}, 
            {"name": "Kagiso Rabada", "role": "Bowler"}, 
            {"name": "Sai Kishore", "role": "Bowler"}
        ],
        "Lucknow Super Giants": [
            {"name": "Rishabh Pant", "role": "Wicketkeeper Batter (c)"}, 
            {"name": "Abdul Samad", "role": "Batter"}, 
            {"name": "Akshat Raghuwanshi", "role": "Middle order Batter"}, 
            {"name": "Ayush Badoni", "role": "Batter"}, 
            {"name": "Matthew Breetzke", "role": "Batter"}, 
            {"name": "Mukul Choudhary", "role": "Middle order Batter"}, 
            {"name": "Himmat Singh", "role": "Batter"}, 
            {"name": "Josh Inglis", "role": "Wicketkeeper Batter"}, 
            {"name": "Aiden Markram", "role": "Middle order Batter"}, 
            {"name": "Nicholas Pooran", "role": "Wicketkeeper Batter"}, 
            {"name": "Wanindu Hasaranga", "role": "Allrounder"}, 
            {"name": "Arshin Kulkarni", "role": "Allrounder"}, 
            {"name": "Akash Singh", "role": "Bowler"}, 
            {"name": "Avesh Khan", "role": "Bowler"}, 
            {"name": "Mohammed Shami", "role": "Bowler"}, 
            {"name": "Mohsin Khan", "role": "Bowler"}, 
            {"name": "Anrich Nortje", "role": "Bowler"}, 
            {"name": "Prince Yadav", "role": "Bowler"}, 
            {"name": "Digvesh Rathi", "role": "Bowler"}, 
            {"name": "Manimaran Siddharth", "role": "Bowler"}, 
            {"name": "Arjun Tendulkar", "role": "Bowler"}, 
            {"name": "Naman Tiwari", "role": "Bowler"}
        ],
        "Sunrisers Hyderabad": [
            {"name": "Ishan Kishan", "role": "Wicketkeeper Batter (c)"}, 
            {"name": "Salil Arora", "role": "Wicketkeeper Batter"}, 
            {"name": "Travis Head", "role": "Middle order Batter"}, 
            {"name": "Heinrich Klaasen", "role": "Wicketkeeper Batter"}, 
            {"name": "Ravichandran Smaran", "role": "Batter"}, 
            {"name": "Aniket Verma", "role": "Batter"}, 
            {"name": "Abhishek Sharma", "role": "Batting Allrounder"}, 
            {"name": "Brydon Carse", "role": "Bowling Allrounder"}, 
            {"name": "Harsh Dubey", "role": "Bowling Allrounder"}, 
            {"name": "Krains Fuletra", "role": "Bowling Allrounder"}, 
            {"name": "Liam Livingstone", "role": "Batting Allrounder"}, 
            {"name": "Kamindu Mendis", "role": "Allrounder"}, 
            {"name": "Nitish Kumar Reddy", "role": "Batting Allrounder"}, 
            {"name": "Harshal Patel", "role": "Bowling Allrounder"}, 
            {"name": "Shivam Mavi", "role": "Bowling Allrounder"}, 
            {"name": "Shivang Kumar", "role": "Bowling Allrounder"}, 
            {"name": "Amit Kumar", "role": "Bowler"}, 
            {"name": "Pat Cummins", "role": "Bowler"}, 
            {"name": "Praful Hinge", "role": "Bowler"}, 
            {"name": "Eshan Malinga", "role": "Bowler"}, 
            {"name": "David Payne", "role": "Bowler"}, 
            {"name": "Sakib Hussain", "role": "Bowler"}, 
            {"name": "Jaydev Unadkat", "role": "Bowler"}
        ]
    },
    "INTERNATIONAL": {
        "India": [
            {"name": "Suryakumar Yadav", "role": "Batter (c)"}, 
            {"name": "Ishan Kishan", "role": "Wicketkeeper Batter"}, 
            {"name": "Sanju Samson", "role": "Wicketkeeper Batter"}, 
            {"name": "Rinku Singh", "role": "Middle order Batter"}, 
            {"name": "Axar Patel", "role": "Allrounder (vc)"}, 
            {"name": "Abhishek Sharma", "role": "Batting Allrounder"}, 
            {"name": "Shivam Dube", "role": "Allrounder"}, 
            {"name": "Hardik Pandya", "role": "Allrounder"}, 
            {"name": "Tilak Varma", "role": "Batting Allrounder"}, 
            {"name": "Washington Sundar", "role": "Bowling Allrounder"}, 
            {"name": "Arshdeep Singh", "role": "Bowler"}, 
            {"name": "Jasprit Bumrah", "role": "Bowler"}, 
            {"name": "Kuldeep Yadav", "role": "Bowler"}, 
            {"name": "Mohammed Siraj", "role": "Bowler"}, 
            {"name": "Varun Chakravarthy", "role": "Bowler"}
        ],
        "Australia": [
            {"name": "Mitchell Marsh", "role": "Allrounder (c)"},
            {"name": "Tim David", "role": "Middle order Batter"},
            {"name": "Travis Head", "role": "Middle order Batter"},
            {"name": "Josh Inglis", "role": "Wicketkeeper Batter"},
            {"name": "Matt Renshaw", "role": "Batter"},
            {"name": "Steven Smith", "role": "Top order Batter"},
            {"name": "Cooper Connolly", "role": "Batting Allrounder"},
            {"name": "Cameron Green", "role": "Batting Allrounder"},
            {"name": "Glenn Maxwell", "role": "Batting Allrounder"},
            {"name": "Marcus Stoinis", "role": "Batting Allrounder"},
            {"name": "Xavier Bartlett", "role": "Bowler"},
            {"name": "Ben Dwarshuis", "role": "Bowler"},
            {"name": "Nathan Ellis", "role": "Bowler"},
            {"name": "Matthew Kuhnemann", "role": "Bowler"},
            {"name": "Adam Zampa", "role": "Bowler"}
        ],
        "Pakistan": [
            {"name": "Salman Agha", "role": "Allrounder (c)"},
            {"name": "Babar Azam", "role": "Batter"},
            {"name": "Fakhar Zaman", "role": "Opening Batter"},
            {"name": "Khawaja Nafay", "role": "Wicketkeeper Batter"},
            {"name": "Sahibzada Farhan", "role": "Middle order Batter"},
            {"name": "Usman Khan", "role": "Wicketkeeper Batter"},
            {"name": "Faheem Ashraf", "role": "Bowling Allrounder"},
            {"name": "Muhammad Nawaz", "role": "Allrounder"},
            {"name": "Saim Ayub", "role": "Allrounder"},
            {"name": "Shadab Khan", "role": "Allrounder"},
            {"name": "Abrar Ahmed", "role": "Bowler"},
            {"name": "Naseem Shah", "role": "Bowler"},
            {"name": "Shaheen Shah Afridi", "role": "Bowler"}
        ],
        "England": [
            {"name": "Harry Brook", "role": "Middle order Batter (c)"},
            {"name": "Tom Banton", "role": "Wicketkeeper Batter"},
            {"name": "Jos Butler", "role": "Wicketkeeper Batter"},
            {"name": "Phil Salt", "role": "Wicketkeeper Batter"},
            {"name": "Jacob Bethell", "role": "Batting Allrounder"},
            {"name": "Sam Curran", "role": "Allrounder"},
            {"name": "Liam Dawson", "role": "Allrounder"},
            {"name": "Will Jacks", "role": "Batting Allrounder"},
            {"name": "Jamie Overton", "role": "Bowling Allrounder"},
            {"name": "Rehan Ahmed", "role": "Bowling Allrounder"},
            {"name": "Jofra Archer", "role": "Bowler"},
            {"name": "Adil Rashid", "role": "Bowler"}
        ]
    }
}

def update_squads():
    db = SessionLocal()
    print("=== CRICORACLE: 2026 SQUAD REFRESH EXECUTION ===")
    
    # 1. Clear ALL current squad mappings to avoid stale data
    print("[1/5] Resetting current squad mappings...")
    db.execute(text("UPDATE players SET franchise_team_id = NULL, intl_team_id = NULL"))
    db.commit()

    # 2. Map Franchise Squads (IPL 2026)
    print("\n[2/5] Mapping Franchise Squads...")
    for team_name, players in SQUAD_DATA["FRANCHISE"].items():
        team = db.query(Team).filter(Team.name.like(f"%{team_name}%")).first()
        if not team:
            print(f"  [WARN] Team not found: {team_name}")
            continue
        
        print(f"  Updating {team_name} ({len(players)} players)...")
        for p_data in players:
            name = p_data["name"]
            role = p_data["role"].replace(" (c)", "").replace(" (vc)", "")
            
            # Find or Create Player
            player = db.query(Player).filter(Player.name == name).first()
            if not player:
                # Add new player
                player = Player(
                    name=name,
                    role=role,
                    nationality=team.name if team.team_type == "International" else "India" # Default india if unknown
                )
                db.add(player)
                db.flush()
                print(f"    [NEW] {name} added to database.")
            
            # Update role and styles
            player.role = role
            player.franchise_team_id = team.team_id
    
    db.commit()

    # 3. Map International Squads
    print("\n[3/5] Mapping International Squads...")
    for country, players in SQUAD_DATA["INTERNATIONAL"].items():
        team = db.query(Team).filter(Team.name == country).first()
        if not team:
            print(f"  [WARN] Team not found: {country}")
            continue
            
        print(f"  Updating {country} ({len(players)} players)...")
        for p_data in players:
            name = p_data["name"]
            role = p_data["role"].replace(" (c)", "").replace(" (vc)", "")
            
            player = db.query(Player).filter(Player.name == name).first()
            if not player:
                player = Player(name=name, role=role, nationality=country)
                db.add(player)
                db.flush()
            
            player.intl_team_id = team.team_id
            player.nationality = country # Sync nationality

    db.commit()

    # 4. Handle Specific Left Players (Verification)
    print("\n[4/5] Verifying 'Left' Players...")
    left_players = ["Mayank Agarwal", "Devon Conway", "Pat Cummins"]
    for name in left_players:
        player = db.query(Player).filter(Player.name.like(f"%{name}%")).first()
        if player:
            # Check if they are in any of the NEW squads
            # If not found in our fresh SQUAD_DATA, they will have NULL ids already
            print(f"  {name}: Franchise={player.franchise_team_id}, International={player.intl_team_id}")

    # 5. Final Stats
    total_players = db.query(Player).count()
    mapped_franchise = db.query(Player).filter(Player.franchise_team_id != None).count()
    mapped_intl = db.query(Player).filter(Player.intl_team_id != None).count()
    
    print("\n=== REFRESH COMPLETE ===")
    print(f"  Total Players in DB: {total_players}")
    print(f"  Players in IPL 2026 Squads: {mapped_franchise}")
    print(f"  Players in Intl 2026 Squads: {mapped_intl}")
    
    db.close()

if __name__ == "__main__":
    update_squads()
