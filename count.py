import json

with open('graph_data.json', 'r', encoding='utf-8') as file:
    team_data = json.load(file)

print(len(team_data['nodes']))
print(len(team_data['edges']))