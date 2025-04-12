from z3 import *
import json

# Load data
with open('students.json') as f:
    data = json.load(f)

students = data["students"]
n_students = len(students)
team_size = data["constraints"]["team_size"]
n_teams = n_students // team_size

# Initialize OMT solver
opt = Optimize()

# Variables: team[i][j] = True if student j is in team i
team = [[Bool(f"team_{i}_student_{j}") for j in range(n_students)] for i in range(n_teams)]

# Constraints
# 1. Each student in exactly one team
for j in range(n_students):
    opt.add(Sum([If(team[i][j], 1, 0) for i in range(n_teams)]) == 1)

# 2. Team size
for i in range(n_teams):
    opt.add(Sum([If(team[i][j], 1, 0) for j in range(n_students)]) == team_size)

# 3. Gender balance
for i in range(n_teams):
    females = Sum([If(And(team[i][j], students[j]["gender"] == "F"), 1, 0) for j in range(n_students)])
    males = Sum([If(And(team[i][j], students[j]["gender"] == "M"), 1, 0) for j in range(n_students)])
    opt.add(females >= data["constraints"]["min_female_per_team"])
    opt.add(males >= data["constraints"]["min_male_per_team"])

# 4. Skill balance: Define average skill per team
avg_skills = [Int(f"avg_team_{i}") for i in range(n_teams)]
for i in range(n_teams):
    opt.add(avg_skills[i] == Sum([If(team[i][j], students[j]["skills"]["coding"], 0) for j in range(n_students)]) / team_size)

# 5. Objective: Minimize the maximum skill gap between teams
max_gap = Int("max_gap")
for i in range(n_teams - 1):
    opt.add(max_gap >= Abs(avg_skills[i] - avg_skills[i + 1]))
opt.minimize(max_gap)  # OMT: Minimize the worst skill gap

# Solve
if opt.check() == sat:
    model = opt.model()
    teams = {f"Team {i}": [students[j]["name"] for j in range(n_students) if model.evaluate(team[i][j])] for i in range(n_teams)}
    print("Teams:", json.dumps(teams, indent=2))
    print("Max skill gap:", model.evaluate(max_gap))
else:
    print("No solution!")