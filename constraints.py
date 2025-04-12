from z3 import *
import json

with open('students.json') as f:
    data = json.load(f)

students = data["students"]
n_students = len(students)
team_size = data["constraints"]["team_size"]
n_teams = n_students // team_size

solver = Solver()
team = [[Bool(f"team_{i}_student_{j}") for j in range(n_students)] for i in range(n_teams)]

# Constraints
for j in range(n_students):
    solver.add(Sum([If(team[i][j], 1, 0) for i in range(n_teams)]) == 1)

for i in range(n_teams):
    solver.add(Sum([If(team[i][j], 1, 0) for j in range(n_students)]) == team_size)

for i in range(n_teams):
    females = Sum([If(And(team[i][j], students[j]["gender"] == "F"), 1, 0) for j in range(n_students)])
    males = Sum([If(And(team[i][j], students[j]["gender"] == "M"), 1, 0) for j in range(n_students)])
    solver.add(females >= data["constraints"]["min_female_per_team"])
    solver.add(males >= data["constraints"]["min_male_per_team"])

avg_skills = [Int(f"avg_team_{i}") for i in range(n_teams)]
for i in range(n_teams):
    solver.add(avg_skills[i] == Sum([If(team[i][j], students[j]["skills"]["coding"], 0) for j in range(n_students)]) / team_size)
for i in range(n_teams - 1):
    solver.add(Abs(avg_skills[i] - avg_skills[i + 1]) <= data["constraints"]["max_skill_gap"])

if solver.check() == sat:
    model = solver.model()
    teams = {f"Team {i}": [students[j]["name"] for j in range(n_students) if model.evaluate(team[i][j])] for i in range(n_teams)}
    print(json.dumps(teams, indent=2))
else:
    print("No solution!")