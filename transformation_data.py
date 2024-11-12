import json
import networkx as nx
import numpy as np

# Чтение данных из файла
with open('team_data_with_friends.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

G = nx.Graph()
team_members = {}

# Создание графа
for user_key, user_info in data['team'].items():
    member_id = int(user_info['id'])
    # Сохраняем имя пользователя (ключ user_key)
    team_members[member_id] = user_key  

    for friend in user_info.get('friends', []):
        friend_id = int(friend['id'])
        G.add_edge(member_id, friend_id)
        # Сохраняем имя друга
        team_members[friend_id] = friend.get('name', '')  # Сохраняем имя друга

# Центральность по посредничеству
betweenness_centrality = nx.betweenness_centrality(G)

# Определяем пороги для центральных узлов
high_threshold = 0.9  # лучшие 10%
medium_threshold = 0.7  # 30%

sorted_betweenness = sorted(betweenness_centrality.values(), reverse=True)
high_value = sorted_betweenness[int(len(sorted_betweenness) * high_threshold)]
medium_value = sorted_betweenness[int(len(sorted_betweenness) * medium_threshold)]

# Добавляем друзей и друзей друзей в граф
for user_key, user_info in data['team'].items():
    for friend in user_info.get('friends', []):
        if 'friends_of_friend' in friend:
            for fof in friend['friends_of_friend']:
                fof_id = int(fof['id'])
                G.add_edge(friend_id, fof_id)
                team_members[fof_id] = fof.get('name', '')  # Сохраняем имя друга друга
                if 'friend_with' in fof and fof['friend_with']:
                    for fw_id in fof['friend_with']:
                        fw_id = int(fw_id)
                        G.add_edge(fof_id, fw_id)

# Преобразуем узлы и связи для Vis
nodes = []
edges = []

centrality_values = list(betweenness_centrality.values())
top_10_threshold = np.percentile(centrality_values, 90)  # Топ 10%
top_30_threshold = np.percentile(centrality_values, 70)  # Топ 30%

# Формируем список узлов с именами
for node_id in G.nodes(data=True):
    centrality = betweenness_centrality.get(node_id[0], 0)
    
    if centrality >= top_10_threshold:
        color = 'red'  # Топ 10%
    elif centrality >= top_30_threshold:
        color = 'orange'  # Следующие 20%
    else:
        color = 'lightblue'  # Остальные 70%
    
    # Получаем имя пользователя из словаря team_members
    nodes.append({
        "id": node_id[0],
        "name": team_members.get(node_id[0], ""),  # Получаем имя из словаря team_members
        "color": color
    })

# Формируем список рёбер
for edge in G.edges():
    edges.append({"from": edge[0], "to": edge[1]})

# Создаем итоговые данные графа
graph_data = {
    "nodes": nodes,
    "edges": edges
}

# Записываем данные в файл
with open('graph_data.json', 'w', encoding='utf-8') as f:
    json.dump(graph_data, f, ensure_ascii=False, indent=4)