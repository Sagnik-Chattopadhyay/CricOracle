"""
CricOracle: Schema Migration + Latest Squad Population
------------------------------------------------------
1. Adds logo_path to teams table
2. Adds intl_team_id & franchise_team_id to players table
3. Populates latest IPL 2025 & International squads
"""
import sqlite3
from db import SessionLocal, get_canonical_team_name
from models import Team, Player
from sqlalchemy import text

DB_PATH = "cricpredict.db"

# ================================================================
# LOGO MAPPINGS
# ================================================================
IPL_LOGOS = {
    "Chennai Super Kings": "/assets/logos/ipl/csk.webp",
    "Delhi Capitals": "/assets/logos/ipl/dc.webp",
    "Gujarat Titans": "/assets/logos/ipl/gt.webp",
    "Kolkata Knight Riders": "/assets/logos/ipl/kkr.webp",
    "Lucknow Super Giants": "/assets/logos/ipl/lsg.webp",
    "Mumbai Indians": "/assets/logos/ipl/mi.webp",
    "Punjab Kings": "/assets/logos/ipl/pbks.webp",
    "Rajasthan Royals": "/assets/logos/ipl/rr.webp",
    "Royal Challengers Bengaluru": "/assets/logos/ipl/rcb.webp",
    "Sunrisers Hyderabad": "/assets/logos/ipl/srh.webp",
}

INTL_LOGOS = {
    "India": "/assets/logos/intl/ind.png",
    "Australia": "/assets/logos/intl/aus.png",
    "England": "/assets/logos/intl/eng.png",
    "New Zealand": "/assets/logos/intl/nz.png",
    "Pakistan": "/assets/logos/intl/pak.png",
    "South Africa": "/assets/logos/intl/sa.png",
    "Sri Lanka": "/assets/logos/intl/sl.png",
    "Bangladesh": "/assets/logos/intl/ban.png",
    "Afghanistan": "/assets/logos/intl/afg.png",
    "Zimbabwe": "/assets/logos/intl/zim.png",
    "USA": "/assets/logos/intl/usa.png",
}

# ================================================================
# IPL 2025 SQUADS (Latest after mega auction)
# ================================================================
IPL_2025_SQUADS = {
    "Chennai Super Kings": {
        "players": [
            ("Ruturaj Gaikwad", "Batter", "Right-Handed Batsman", None, "India"),
            ("Devon Conway", "Batter", "Left-Handed Batsman", None, "New Zealand"),
            ("Rahul Tripathi", "Batter", "Right-Handed Batsman", None, "India"),
            ("Shivam Dube", "All-rounder", "Left-Handed Batsman", "Left-Arm Medium", "India"),
            ("Ravindra Jadeja", "All-rounder", "Left-Handed Batsman", "Left-Arm Orthodox", "India"),
            ("MS Dhoni", "Wicket-keeper Batter", "Right-Handed Batsman", None, "India"),
            ("Deepak Chahar", "Bowler", "Right-Handed Batsman", "Right-Arm Medium Fast", "India"),
            ("Tushar Deshpande", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "India"),
            ("Matheesha Pathirana", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "Sri Lanka"),
            ("Maheesh Theekshana", "Bowler", "Right-Handed Batsman", "Right-Arm Off Spin", "Sri Lanka"),
            ("Rachin Ravindra", "All-rounder", "Left-Handed Batsman", "Left-Arm Orthodox", "New Zealand"),
            ("Shardul Thakur", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium Fast", "India"),
            ("Noor Ahmad", "Bowler", "Left-Handed Batsman", "Left-Arm Wrist Spin", "Afghanistan"),
            ("Khaleel Ahmed", "Bowler", "Left-Handed Batsman", "Left-Arm Medium Fast", "India"),
            ("Vijay Shankar", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium", "India"),
        ],
    },
    "Mumbai Indians": {
        "players": [
            ("Rohit Sharma", "Batter", "Right-Handed Batsman", "Right-Arm Off Break", "India"),
            ("Suryakumar Yadav", "Batter", "Right-Handed Batsman", None, "India"),
            ("Ishan Kishan", "Wicket-keeper Batter", "Left-Handed Batsman", None, "India"),
            ("Tilak Varma", "Batter", "Left-Handed Batsman", None, "India"),
            ("Hardik Pandya", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium Fast", "India"),
            ("Tim David", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium", "Singapore"),
            ("Jasprit Bumrah", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "India"),
            ("Trent Boult", "Bowler", "Right-Handed Batsman", "Left-Arm Fast", "New Zealand"),
            ("Piyush Chawla", "Bowler", "Right-Handed Batsman", "Right-Arm Leg Spin", "India"),
            ("Dewald Brevis", "Batter", "Right-Handed Batsman", "Right-Arm Leg Spin", "South Africa"),
            ("Naman Dhir", "All-rounder", "Left-Handed Batsman", "Right-Arm Off Break", "India"),
            ("Deepak Hooda", "All-rounder", "Right-Handed Batsman", "Right-Arm Off Break", "India"),
            ("Will Jacks", "All-rounder", "Right-Handed Batsman", "Right-Arm Off Break", "England"),
            ("Ashwani Kumar", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "India"),
            ("Reece Topley", "Bowler", "Left-Handed Batsman", "Left-Arm Fast", "England"),
        ],
    },
    "Royal Challengers Bengaluru": {
        "players": [
            ("Virat Kohli", "Batter", "Right-Handed Batsman", "Right-Arm Medium", "India"),
            ("Rajat Patidar", "Batter", "Right-Handed Batsman", None, "India"),
            ("Faf du Plessis", "Batter", "Right-Handed Batsman", None, "South Africa"),
            ("Phil Salt", "Wicket-keeper Batter", "Right-Handed Batsman", None, "England"),
            ("Glenn Maxwell", "All-rounder", "Right-Handed Batsman", "Right-Arm Off Break", "Australia"),
            ("Liam Livingstone", "All-rounder", "Right-Handed Batsman", "Right-Arm Leg Spin", "England"),
            ("Krunal Pandya", "All-rounder", "Left-Handed Batsman", "Left-Arm Orthodox", "India"),
            ("Bhuvneshwar Kumar", "Bowler", "Right-Handed Batsman", "Right-Arm Medium Fast", "India"),
            ("Josh Hazlewood", "Bowler", "Left-Handed Batsman", "Right-Arm Fast", "Australia"),
            ("Yash Dayal", "Bowler", "Left-Handed Batsman", "Left-Arm Medium Fast", "India"),
            ("Rasikh Salam", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "India"),
            ("Suyash Sharma", "Bowler", "Right-Handed Batsman", "Right-Arm Leg Spin", "India"),
            ("Swapnil Singh", "All-rounder", "Left-Handed Batsman", "Left-Arm Orthodox", "India"),
            ("Jitesh Sharma", "Wicket-keeper Batter", "Right-Handed Batsman", None, "India"),
            ("Tim Southee", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "New Zealand"),
        ],
    },
    "Kolkata Knight Riders": {
        "players": [
            ("Venkatesh Iyer", "All-rounder", "Left-Handed Batsman", "Right-Arm Medium", "India"),
            ("Rinku Singh", "Batter", "Left-Handed Batsman", None, "India"),
            ("Sunil Narine", "All-rounder", "Left-Handed Batsman", "Right-Arm Off Break", "West Indies"),
            ("Andre Russell", "All-rounder", "Right-Handed Batsman", "Right-Arm Fast", "West Indies"),
            ("Angkrish Raghuvanshi", "Batter", "Left-Handed Batsman", None, "India"),
            ("Quinton de Kock", "Wicket-keeper Batter", "Left-Handed Batsman", None, "South Africa"),
            ("Ajinkya Rahane", "Batter", "Right-Handed Batsman", None, "India"),
            ("Varun Chakravarthy", "Bowler", "Right-Handed Batsman", "Right-Arm Leg Spin", "India"),
            ("Harshit Rana", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "India"),
            ("Vaibhav Arora", "Bowler", "Right-Handed Batsman", "Right-Arm Medium Fast", "India"),
            ("Ramandeep Singh", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium", "India"),
            ("Anrich Nortje", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "South Africa"),
            ("Moeen Ali", "All-rounder", "Left-Handed Batsman", "Right-Arm Off Break", "England"),
            ("Spencer Johnson", "Bowler", "Left-Handed Batsman", "Left-Arm Fast", "Australia"),
            ("Manish Pandey", "Batter", "Right-Handed Batsman", None, "India"),
        ],
    },
    "Rajasthan Royals": {
        "players": [
            ("Sanju Samson", "Wicket-keeper Batter", "Right-Handed Batsman", None, "India"),
            ("Yashasvi Jaiswal", "Batter", "Left-Handed Batsman", "Right-Arm Leg Spin", "India"),
            ("Shimron Hetmyer", "Batter", "Left-Handed Batsman", None, "West Indies"),
            ("Riyan Parag", "All-rounder", "Right-Handed Batsman", "Right-Arm Leg Spin", "India"),
            ("Dhruv Jurel", "Wicket-keeper Batter", "Right-Handed Batsman", None, "India"),
            ("Ravichandran Ashwin", "All-rounder", "Right-Handed Batsman", "Right-Arm Off Break", "India"),
            ("Trent Boult", "Bowler", "Right-Handed Batsman", "Left-Arm Fast", "New Zealand"),
            ("Sandeep Sharma", "Bowler", "Right-Handed Batsman", "Right-Arm Medium Fast", "India"),
            ("Yuzvendra Chahal", "Bowler", "Right-Handed Batsman", "Right-Arm Leg Spin", "India"),
            ("Wanindu Hasaranga", "All-rounder", "Right-Handed Batsman", "Right-Arm Leg Spin", "Sri Lanka"),
            ("Jofra Archer", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "England"),
            ("Manoj Bhandage", "All-rounder", "Left-Handed Batsman", "Left-Arm Medium", "India"),
            ("Kunal Rathore", "Batter", "Left-Handed Batsman", None, "India"),
            ("Shubham Dubey", "Batter", "Right-Handed Batsman", None, "India"),
            ("Tushar Deshpande", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "India"),
        ],
    },
    "Delhi Capitals": {
        "players": [
            ("Rishabh Pant", "Wicket-keeper Batter", "Left-Handed Batsman", None, "India"),
            ("David Warner", "Batter", "Left-Handed Batsman", "Right-Arm Leg Spin", "Australia"),
            ("Abishek Porel", "Wicket-keeper Batter", "Left-Handed Batsman", None, "India"),
            ("Jake Fraser-McGurk", "Batter", "Right-Handed Batsman", "Right-Arm Leg Spin", "Australia"),
            ("Tristan Stubbs", "Batter", "Right-Handed Batsman", None, "South Africa"),
            ("Mitchell Marsh", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium Fast", "Australia"),
            ("Axar Patel", "All-rounder", "Left-Handed Batsman", "Left-Arm Orthodox", "India"),
            ("Kuldeep Yadav", "Bowler", "Left-Handed Batsman", "Left-Arm Wrist Spin", "India"),
            ("Anrich Nortje", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "South Africa"),
            ("Ishant Sharma", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "India"),
            ("Mukesh Kumar", "Bowler", "Right-Handed Batsman", "Right-Arm Medium Fast", "India"),
            ("Kamlesh Nagarkoti", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "India"),
            ("Faf du Plessis", "Batter", "Right-Handed Batsman", None, "South Africa"),
            ("Sumit Kumar", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium", "India"),
            ("Jhye Richardson", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "Australia"),
        ],
    },
    "Punjab Kings": {
        "players": [
            ("Shikhar Dhawan", "Batter", "Left-Handed Batsman", None, "India"),
            ("Shreyas Iyer", "Batter", "Right-Handed Batsman", "Right-Arm Leg Spin", "India"),
            ("Jonny Bairstow", "Wicket-keeper Batter", "Right-Handed Batsman", None, "England"),
            ("Prabhsimran Singh", "Wicket-keeper Batter", "Right-Handed Batsman", None, "India"),
            ("Marcus Stoinis", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium", "Australia"),
            ("Sam Curran", "All-rounder", "Left-Handed Batsman", "Left-Arm Medium", "England"),
            ("Arshdeep Singh", "Bowler", "Left-Handed Batsman", "Left-Arm Fast", "India"),
            ("Kagiso Rabada", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "South Africa"),
            ("Rahul Chahar", "Bowler", "Right-Handed Batsman", "Right-Arm Leg Spin", "India"),
            ("Harpreet Brar", "All-rounder", "Left-Handed Batsman", "Left-Arm Orthodox", "India"),
            ("Nathan Ellis", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "Australia"),
            ("Rilee Rossouw", "Batter", "Left-Handed Batsman", None, "South Africa"),
            ("Vishnu Vinod", "Wicket-keeper Batter", "Right-Handed Batsman", None, "India"),
            ("Harshal Patel", "Bowler", "Right-Handed Batsman", "Right-Arm Medium Fast", "India"),
            ("Atharva Taide", "Batter", "Left-Handed Batsman", None, "India"),
        ],
    },
    "Sunrisers Hyderabad": {
        "players": [
            ("Travis Head", "Batter", "Left-Handed Batsman", None, "Australia"),
            ("Abhishek Sharma", "All-rounder", "Left-Handed Batsman", "Left-Arm Orthodox", "India"),
            ("Heinrich Klaasen", "Wicket-keeper Batter", "Right-Handed Batsman", None, "South Africa"),
            ("Aiden Markram", "All-rounder", "Right-Handed Batsman", "Right-Arm Off Break", "South Africa"),
            ("Pat Cummins", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "Australia"),
            ("Marco Jansen", "Bowler", "Left-Handed Batsman", "Left-Arm Fast", "South Africa"),
            ("Bhuvneshwar Kumar", "Bowler", "Right-Handed Batsman", "Right-Arm Medium Fast", "India"),
            ("T Natarajan", "Bowler", "Left-Handed Batsman", "Left-Arm Fast", "India"),
            ("Washington Sundar", "All-rounder", "Left-Handed Batsman", "Right-Arm Off Break", "India"),
            ("Shahbaz Ahmed", "All-rounder", "Left-Handed Batsman", "Left-Arm Orthodox", "India"),
            ("Abdul Samad", "Batter", "Right-Handed Batsman", None, "India"),
            ("Rahul Tripathi", "Batter", "Right-Handed Batsman", None, "India"),
            ("Umran Malik", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "India"),
            ("Jaydev Unadkat", "Bowler", "Left-Handed Batsman", "Left-Arm Medium Fast", "India"),
            ("Nitish Reddy", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium Fast", "India"),
        ],
    },
    "Gujarat Titans": {
        "players": [
            ("Shubman Gill", "Batter", "Right-Handed Batsman", None, "India"),
            ("Sai Sudharsan", "Batter", "Left-Handed Batsman", None, "India"),
            ("David Miller", "Batter", "Left-Handed Batsman", None, "South Africa"),
            ("Wriddhiman Saha", "Wicket-keeper Batter", "Right-Handed Batsman", None, "India"),
            ("Rashid Khan", "All-rounder", "Right-Handed Batsman", "Right-Arm Leg Spin", "Afghanistan"),
            ("Mohammed Shami", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "India"),
            ("Alzarri Joseph", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "West Indies"),
            ("Noor Ahmad", "Bowler", "Left-Handed Batsman", "Left-Arm Wrist Spin", "Afghanistan"),
            ("Mohit Sharma", "Bowler", "Right-Handed Batsman", "Right-Arm Medium Fast", "India"),
            ("Darshan Nalkande", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium", "India"),
            ("Vijay Shankar", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium", "India"),
            ("Kane Williamson", "Batter", "Right-Handed Batsman", "Right-Arm Off Break", "New Zealand"),
            ("Joshua Little", "Bowler", "Left-Handed Batsman", "Left-Arm Fast", "Ireland"),
            ("Sai Kishore", "Bowler", "Left-Handed Batsman", "Left-Arm Orthodox", "India"),
            ("Shahrukh Khan", "Batter", "Right-Handed Batsman", None, "India"),
        ],
    },
    "Lucknow Super Giants": {
        "players": [
            ("KL Rahul", "Wicket-keeper Batter", "Right-Handed Batsman", None, "India"),
            ("Quinton de Kock", "Wicket-keeper Batter", "Left-Handed Batsman", None, "South Africa"),
            ("Nicholas Pooran", "Wicket-keeper Batter", "Left-Handed Batsman", None, "West Indies"),
            ("Devdutt Padikkal", "Batter", "Left-Handed Batsman", None, "India"),
            ("Ayush Badoni", "Batter", "Right-Handed Batsman", "Right-Arm Leg Spin", "India"),
            ("Marcus Stoinis", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium", "Australia"),
            ("Krunal Pandya", "All-rounder", "Left-Handed Batsman", "Left-Arm Orthodox", "India"),
            ("Ravi Bishnoi", "Bowler", "Right-Handed Batsman", "Right-Arm Leg Spin", "India"),
            ("Avesh Khan", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "India"),
            ("Mohsin Khan", "Bowler", "Left-Handed Batsman", "Left-Arm Fast", "India"),
            ("Mark Wood", "Bowler", "Right-Handed Batsman", "Right-Arm Fast", "England"),
            ("Yash Thakur", "Bowler", "Right-Handed Batsman", "Right-Arm Medium Fast", "India"),
            ("Naveen ul Haq", "Bowler", "Left-Handed Batsman", "Right-Arm Medium Fast", "Afghanistan"),
            ("Prerak Mankad", "All-rounder", "Left-Handed Batsman", "Left-Arm Orthodox", "India"),
            ("Arshin Kulkarni", "All-rounder", "Right-Handed Batsman", "Right-Arm Off Break", "India"),
        ],
    },
}

# ================================================================
# INTERNATIONAL SQUADS (Latest T20I/ODI core squads - 2025)
# ================================================================
INTL_SQUADS = {
    "India": [
        ("Rohit Sharma", "Batter", "Right-Handed Batsman", "Right-Arm Off Break"),
        ("Virat Kohli", "Batter", "Right-Handed Batsman", "Right-Arm Medium"),
        ("Suryakumar Yadav", "Batter", "Right-Handed Batsman", None),
        ("Shubman Gill", "Batter", "Right-Handed Batsman", None),
        ("Yashasvi Jaiswal", "Batter", "Left-Handed Batsman", "Right-Arm Leg Spin"),
        ("Rishabh Pant", "Wicket-keeper Batter", "Left-Handed Batsman", None),
        ("Hardik Pandya", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium Fast"),
        ("Ravindra Jadeja", "All-rounder", "Left-Handed Batsman", "Left-Arm Orthodox"),
        ("Jasprit Bumrah", "Bowler", "Right-Handed Batsman", "Right-Arm Fast"),
        ("Mohammed Siraj", "Bowler", "Right-Handed Batsman", "Right-Arm Fast"),
        ("Kuldeep Yadav", "Bowler", "Left-Handed Batsman", "Left-Arm Wrist Spin"),
        ("Ravichandran Ashwin", "All-rounder", "Right-Handed Batsman", "Right-Arm Off Break"),
        ("Mohammed Shami", "Bowler", "Right-Handed Batsman", "Right-Arm Fast"),
        ("Arshdeep Singh", "Bowler", "Left-Handed Batsman", "Left-Arm Fast"),
        ("KL Rahul", "Wicket-keeper Batter", "Right-Handed Batsman", None),
    ],
    "Australia": [
        ("Steve Smith", "Batter", "Right-Handed Batsman", "Right-Arm Leg Spin"),
        ("Travis Head", "Batter", "Left-Handed Batsman", None),
        ("David Warner", "Batter", "Left-Handed Batsman", "Right-Arm Leg Spin"),
        ("Marnus Labuschagne", "Batter", "Right-Handed Batsman", "Right-Arm Leg Spin"),
        ("Mitchell Marsh", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium Fast"),
        ("Glenn Maxwell", "All-rounder", "Right-Handed Batsman", "Right-Arm Off Break"),
        ("Pat Cummins", "Bowler", "Right-Handed Batsman", "Right-Arm Fast"),
        ("Mitchell Starc", "Bowler", "Left-Handed Batsman", "Left-Arm Fast"),
        ("Josh Hazlewood", "Bowler", "Left-Handed Batsman", "Right-Arm Fast"),
        ("Adam Zampa", "Bowler", "Right-Handed Batsman", "Right-Arm Leg Spin"),
        ("Nathan Lyon", "Bowler", "Right-Handed Batsman", "Right-Arm Off Break"),
        ("Alex Carey", "Wicket-keeper Batter", "Left-Handed Batsman", None),
        ("Marcus Stoinis", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium"),
        ("Cameron Green", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium Fast"),
        ("Scott Boland", "Bowler", "Right-Handed Batsman", "Right-Arm Fast"),
    ],
    "England": [
        ("Joe Root", "Batter", "Right-Handed Batsman", "Right-Arm Off Break"),
        ("Ben Stokes", "All-rounder", "Left-Handed Batsman", "Right-Arm Fast"),
        ("Harry Brook", "Batter", "Right-Handed Batsman", None),
        ("Jos Buttler", "Wicket-keeper Batter", "Right-Handed Batsman", None),
        ("Jonny Bairstow", "Wicket-keeper Batter", "Right-Handed Batsman", None),
        ("Mark Wood", "Bowler", "Right-Handed Batsman", "Right-Arm Fast"),
        ("Jofra Archer", "Bowler", "Right-Handed Batsman", "Right-Arm Fast"),
        ("James Anderson", "Bowler", "Left-Handed Batsman", "Right-Arm Fast"),
        ("Moeen Ali", "All-rounder", "Left-Handed Batsman", "Right-Arm Off Break"),
        ("Adil Rashid", "Bowler", "Right-Handed Batsman", "Right-Arm Leg Spin"),
        ("Phil Salt", "Wicket-keeper Batter", "Right-Handed Batsman", None),
        ("Liam Livingstone", "All-rounder", "Right-Handed Batsman", "Right-Arm Leg Spin"),
        ("Sam Curran", "All-rounder", "Left-Handed Batsman", "Left-Arm Medium"),
        ("Chris Woakes", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium Fast"),
        ("Reece Topley", "Bowler", "Left-Handed Batsman", "Left-Arm Fast"),
    ],
    "Pakistan": [
        ("Babar Azam", "Batter", "Right-Handed Batsman", None),
        ("Mohammad Rizwan", "Wicket-keeper Batter", "Right-Handed Batsman", None),
        ("Fakhar Zaman", "Batter", "Left-Handed Batsman", None),
        ("Shaheen Shah Afridi", "Bowler", "Left-Handed Batsman", "Left-Arm Fast"),
        ("Naseem Shah", "Bowler", "Right-Handed Batsman", "Right-Arm Fast"),
        ("Shadab Khan", "All-rounder", "Right-Handed Batsman", "Right-Arm Leg Spin"),
        ("Iftikhar Ahmed", "All-rounder", "Right-Handed Batsman", "Right-Arm Off Break"),
        ("Haris Rauf", "Bowler", "Right-Handed Batsman", "Right-Arm Fast"),
        ("Imam-ul-Haq", "Batter", "Left-Handed Batsman", None),
        ("Abdullah Shafique", "Batter", "Right-Handed Batsman", None),
        ("Usama Mir", "Bowler", "Right-Handed Batsman", "Right-Arm Leg Spin"),
        ("Mohammad Nawaz", "All-rounder", "Left-Handed Batsman", "Left-Arm Orthodox"),
        ("Agha Salman", "All-rounder", "Right-Handed Batsman", "Right-Arm Off Break"),
        ("Saim Ayub", "Batter", "Left-Handed Batsman", "Left-Arm Orthodox"),
        ("Abrar Ahmed", "Bowler", "Right-Handed Batsman", "Right-Arm Leg Spin"),
    ],
    "South Africa": [
        ("Quinton de Kock", "Wicket-keeper Batter", "Left-Handed Batsman", None),
        ("Aiden Markram", "All-rounder", "Right-Handed Batsman", "Right-Arm Off Break"),
        ("David Miller", "Batter", "Left-Handed Batsman", None),
        ("Heinrich Klaasen", "Wicket-keeper Batter", "Right-Handed Batsman", None),
        ("Rassie van der Dussen", "Batter", "Right-Handed Batsman", None),
        ("Marco Jansen", "Bowler", "Left-Handed Batsman", "Left-Arm Fast"),
        ("Kagiso Rabada", "Bowler", "Right-Handed Batsman", "Right-Arm Fast"),
        ("Anrich Nortje", "Bowler", "Right-Handed Batsman", "Right-Arm Fast"),
        ("Lungi Ngidi", "Bowler", "Right-Handed Batsman", "Right-Arm Fast"),
        ("Keshav Maharaj", "Bowler", "Left-Handed Batsman", "Left-Arm Orthodox"),
        ("Tristan Stubbs", "Batter", "Right-Handed Batsman", None),
        ("Temba Bavuma", "Batter", "Right-Handed Batsman", None),
        ("Reeza Hendricks", "Batter", "Right-Handed Batsman", None),
        ("Tabraiz Shamsi", "Bowler", "Right-Handed Batsman", "Left-Arm Wrist Spin"),
        ("Gerald Coetzee", "Bowler", "Right-Handed Batsman", "Right-Arm Fast"),
    ],
    "New Zealand": [
        ("Kane Williamson", "Batter", "Right-Handed Batsman", "Right-Arm Off Break"),
        ("Devon Conway", "Batter", "Left-Handed Batsman", None),
        ("Daryl Mitchell", "All-rounder", "Right-Handed Batsman", "Right-Arm Medium"),
        ("Tom Latham", "Wicket-keeper Batter", "Left-Handed Batsman", None),
        ("Glenn Phillips", "Batter", "Right-Handed Batsman", "Right-Arm Off Break"),
        ("Rachin Ravindra", "All-rounder", "Left-Handed Batsman", "Left-Arm Orthodox"),
        ("Trent Boult", "Bowler", "Right-Handed Batsman", "Left-Arm Fast"),
        ("Tim Southee", "Bowler", "Right-Handed Batsman", "Right-Arm Fast"),
        ("Mitchell Santner", "All-rounder", "Left-Handed Batsman", "Left-Arm Orthodox"),
        ("Matt Henry", "Bowler", "Right-Handed Batsman", "Right-Arm Fast"),
        ("Kyle Jamieson", "Bowler", "Right-Handed Batsman", "Right-Arm Fast"),
        ("Lockie Ferguson", "Bowler", "Right-Handed Batsman", "Right-Arm Fast"),
        ("Finn Allen", "Batter", "Right-Handed Batsman", None),
        ("Will Young", "Batter", "Right-Handed Batsman", None),
        ("Ish Sodhi", "Bowler", "Right-Handed Batsman", "Right-Arm Leg Spin"),
    ],
}


def run_migration():
    """Step 1: Schema migration - add columns"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Add logo_path to teams
    try:
        cursor.execute("ALTER TABLE teams ADD COLUMN logo_path TEXT")
        print("[MIGRATION] Added logo_path to teams table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("[MIGRATION] logo_path already exists in teams")
        else:
            raise
    
    # Add intl_team_id to players
    try:
        cursor.execute("ALTER TABLE players ADD COLUMN intl_team_id INTEGER REFERENCES teams(team_id)")
        print("[MIGRATION] Added intl_team_id to players table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("[MIGRATION] intl_team_id already exists in players")
        else:
            raise
    
    # Add franchise_team_id to players
    try:
        cursor.execute("ALTER TABLE players ADD COLUMN franchise_team_id INTEGER REFERENCES teams(team_id)")
        print("[MIGRATION] Added franchise_team_id to players table")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("[MIGRATION] franchise_team_id already exists in players")
        else:
            raise
    
    conn.commit()
    conn.close()
    print("[MIGRATION] Schema migration complete.\n")


def populate_logos():
    """Step 2: Assign logo_path to teams"""
    db = SessionLocal()
    
    all_logos = {**IPL_LOGOS, **INTL_LOGOS}
    updated = 0
    
    for team_name, logo_path in all_logos.items():
        canonical = get_canonical_team_name(team_name)
        team = db.query(Team).filter(Team.name == canonical).first()
        if not team:
            team = db.query(Team).filter(Team.name.ilike(f"%{canonical}%")).first()
        
        if team:
            db.execute(text(f"UPDATE teams SET logo_path = :path WHERE team_id = :tid"), {"path": logo_path, "tid": team.team_id})
            updated += 1
            print(f"  [LOGO] {team.name} -> {logo_path}")
        else:
            print(f"  [LOGO] WARNING: Team '{team_name}' not found in DB!")
    
    db.commit()
    db.close()
    print(f"\n[LOGOS] Updated {updated} team logos.\n")


def populate_squads():
    """Step 3: Populate latest squads with dual-team mapping"""
    db = SessionLocal()
    
    total_players_updated = 0
    total_players_created = 0
    
    # --- IPL Squads ---
    for franchise_name, data in IPL_2025_SQUADS.items():
        canonical_franchise = get_canonical_team_name(franchise_name)
        franchise = db.query(Team).filter(Team.name == canonical_franchise).first()
        if not franchise:
            franchise = db.query(Team).filter(Team.name.ilike(f"%{canonical_franchise}%")).first()
        
        if not franchise:
            print(f"  [SQUAD] ERROR: Franchise '{franchise_name}' not found!")
            continue
        
        print(f"\n--- Populating {franchise.name} (ID: {franchise.team_id}) ---")
        
        for (pname, role, bat_style, bowl_style, nationality) in data["players"]:
            # Find or create player
            player = db.query(Player).filter(Player.name == pname).first()
            if not player:
                player = db.query(Player).filter(Player.name.ilike(pname)).first()
            
            if not player:
                player = Player(name=pname, role=role, batting_style=bat_style, bowling_style=bowl_style, nationality=nationality)
                db.add(player)
                db.flush()
                total_players_created += 1
                print(f"    [NEW] {pname}")
            else:
                # Update existing player's attributes
                if not player.role: player.role = role
                if not player.batting_style: player.batting_style = bat_style
                if not player.bowling_style and bowl_style: player.bowling_style = bowl_style
                if not player.nationality: player.nationality = nationality
                total_players_updated += 1
            
            # Set franchise team using raw SQL for the new column
            db.execute(text("UPDATE players SET franchise_team_id = :fid WHERE player_id = :pid"), 
                       {"fid": franchise.team_id, "pid": player.player_id})
            
            # Also update the legacy team_id to franchise for IPL context
            player.team_id = franchise.team_id
            
            # Set international team
            intl_team = db.query(Team).filter(
                Team.name == nationality,
                Team.team_type == "International"
            ).first()
            if not intl_team:
                intl_team = db.query(Team).filter(Team.name.ilike(f"%{nationality}%")).first()
            
            if intl_team:
                db.execute(text("UPDATE players SET intl_team_id = :iid WHERE player_id = :pid"),
                           {"iid": intl_team.team_id, "pid": player.player_id})
    
    # --- International Squads ---
    for country_name, players_list in INTL_SQUADS.items():
        intl_team = db.query(Team).filter(Team.name == country_name, Team.team_type == "International").first()
        if not intl_team:
            intl_team = db.query(Team).filter(Team.name.ilike(f"%{country_name}%")).first()
        
        if not intl_team:
            print(f"  [SQUAD] ERROR: International team '{country_name}' not found!")
            continue
        
        print(f"\n--- Populating {intl_team.name} International (ID: {intl_team.team_id}) ---")
        
        for (pname, role, bat_style, bowl_style) in players_list:
            player = db.query(Player).filter(Player.name == pname).first()
            if not player:
                player = db.query(Player).filter(Player.name.ilike(pname)).first()
            
            if not player:
                player = Player(name=pname, role=role, batting_style=bat_style, bowling_style=bowl_style, nationality=country_name)
                db.add(player)
                db.flush()
                total_players_created += 1
                print(f"    [NEW] {pname}")
            else:
                if not player.role: player.role = role
                if not player.batting_style: player.batting_style = bat_style
                if not player.bowling_style and bowl_style: player.bowling_style = bowl_style
                total_players_updated += 1
            
            # Set international team
            db.execute(text("UPDATE players SET intl_team_id = :iid WHERE player_id = :pid"),
                       {"iid": intl_team.team_id, "pid": player.player_id})
    
    db.commit()
    db.close()
    print(f"\n[SQUADS] Created {total_players_created} new players, updated {total_players_updated} existing.")


def verify():
    """Step 4: Verification"""
    db = SessionLocal()
    
    print("\n" + "="*60)
    print("VERIFICATION REPORT")
    print("="*60)
    
    # Check logos
    teams_with_logos = db.execute(text("SELECT name, logo_path FROM teams WHERE logo_path IS NOT NULL")).fetchall()
    print(f"\nTeams with logos: {len(teams_with_logos)}")
    for t in teams_with_logos:
        print(f"  {t[0]}: {t[1]}")
    
    # Check franchise squads
    print("\n--- IPL Franchise Squad Counts ---")
    for franchise_name in IPL_2025_SQUADS.keys():
        canonical = get_canonical_team_name(franchise_name)
        team = db.query(Team).filter(Team.name.ilike(f"%{canonical}%")).first()
        if team:
            count = db.execute(text("SELECT COUNT(*) FROM players WHERE franchise_team_id = :tid"), {"tid": team.team_id}).scalar()
            print(f"  {team.name}: {count} players")
    
    # Check international squads
    print("\n--- International Squad Counts ---")
    for country in INTL_SQUADS.keys():
        team = db.query(Team).filter(Team.name == country).first()
        if not team:
            team = db.query(Team).filter(Team.name.ilike(f"%{country}%")).first()
        if team:
            count = db.execute(text("SELECT COUNT(*) FROM players WHERE intl_team_id = :tid"), {"tid": team.team_id}).scalar()
            print(f"  {team.name}: {count} players")
    
    # Spot check: Virat Kohli
    print("\n--- SPOT CHECK: Virat Kohli ---")
    vk = db.query(Player).filter(Player.name.ilike("%Virat Kohli%")).first()
    if vk:
        franchise_id = db.execute(text("SELECT franchise_team_id FROM players WHERE player_id = :pid"), {"pid": vk.player_id}).scalar()
        intl_id = db.execute(text("SELECT intl_team_id FROM players WHERE player_id = :pid"), {"pid": vk.player_id}).scalar()
        franchise = db.query(Team).get(franchise_id) if franchise_id else None
        intl = db.query(Team).get(intl_id) if intl_id else None
        print(f"  Franchise: {franchise.name if franchise else 'NONE'}")
        print(f"  International: {intl.name if intl else 'NONE'}")
        print(f"  Role: {vk.role}, Bat: {vk.batting_style}")
    
    db.close()


if __name__ == "__main__":
    print("="*60)
    print("CricOracle: Schema Migration + Squad Population")
    print("="*60)
    
    run_migration()
    populate_logos()
    populate_squads()
    verify()
    
    print("\n[DONE] Migration and population complete!")
