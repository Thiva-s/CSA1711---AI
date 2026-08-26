import heapq

def a_star(graph, start, goal, heuristic):
    open_list = []
    heapq.heappush(open_list, (0, start))

    g_cost = {start: 0}
    parent = {start: None}

    while open_list:
        f, current = heapq.heappop(open_list)

        if current == goal:
            path = []
            while current:
                path.append(current)
                current = parent[current]
            return path[::-1]

        for neighbor, cost in graph[current]:
            new_cost = g_cost[current] + cost

            if neighbor not in g_cost or new_cost < g_cost[neighbor]:
                g_cost[neighbor] = new_cost
                f_cost = new_cost + heuristic[neighbor]
                heapq.heappush(open_list, (f_cost, neighbor))
                parent[neighbor] = current

    return None


# Graph
graph = {
    'A': [('B', 1), ('C', 3)],
    'B': [('D', 2), ('E', 4)],
    'C': [('E', 2)],
    'D': [('F', 3)],
    'E': [('F', 1)],
    'F': []
}

# Heuristic values
heuristic = {
    'A': 5,
    'B': 4,
    'C': 3,
    'D': 2,
    'E': 1,
    'F': 0
}

# Find path
path = a_star(graph, 'A', 'F', heuristic)

print("A* Path:", path)