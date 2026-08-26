colors = ['Red', 'Green', 'Blue']

graph = {
    'A': ['B', 'C'],
    'B': ['A', 'C', 'D'],
    'C': ['A', 'B', 'D'],
    'D': ['B', 'C']
}

color = {}

def is_safe(node, c):
    for neighbor in graph[node]:
        if neighbor in color and color[neighbor] == c:
            return False
    return True

def map_coloring(node):
    if node == len(graph):
        return True

    place = list(graph.keys())[node]

    for c in colors:
        if is_safe(place, c):
            color[place] = c

            if map_coloring(node + 1):
                return True

            del color[place]

    return False

map_coloring(0)

print("Map Coloring:")
for region in color:
    print(region, ":", color[region])