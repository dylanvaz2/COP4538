"""
Graph Path Finding Algorithms

This script implements BFS for shortest path in unweighted graph
and Dijkstra's algorithm for cheapest path in weighted graph.
"""

from collections import deque
import heapq

# Unweighted graph adjacency list
unweighted_graph = {
    "A": ["B", "D", "L"],
    "B": ["A", "C", "L"],
    "C": ["B", "E", "F", "D"],
    "D": ["A", "C", "I"],
    "E": ["L", "C", "F", "M"],
    "F": ["C", "E", "G", "M"],
    "G": ["F", "K", "N"],
    "H": ["I", "J", "G"],
    "I": ["D", "H"],
    "J": ["H", "K"],
    "K": ["G", "J"],
    "L": ["A", "B", "E", "M"],
    "M": ["L", "E", "F", "N"],
    "N": ["M", "G"],
}

# Weighted graph adjacency list with weights as list of tuples
weighted_graph = {
    "A": [("B", 15), ("D", 12), ("L", 10)],
    "B": [("A", 15), ("C", 1), ("L", 8)],
    "C": [("B", 1), ("D", 10), ("E", 17), ("F", 25)],
    "D": [("A", 12), ("C", 10), ("I", 22)],
    "E": [("C", 17), ("F", 30), ("L", 18), ("M", 18)],
    "F": [("C", 25), ("E", 30), ("G", 13), ("M", 35)],
    "G": [("F", 13), ("H", 40), ("K", 15), ("N", 5)],
    "H": [("G", 40), ("I", 12), ("J", 23)],
    "I": [("D", 22), ("H", 12)],
    "J": [("H", 23), ("K", 14)],
    "K": [("G", 15), ("J", 14)],
    "L": [("A", 10), ("B", 8), ("E", 18), ("M", 18)],
    "M": [("E", 18), ("F", 35), ("L", 18), ("N", 9)],
    "N": [("G", 5), ("M", 9)],
}

def bfs_shortest_path(graph, start, end):
    """Find shortest path using BFS in unweighted graph."""
    queue = deque([start])
    visited = set([start])
    parent = {start: None}
    level = 0

    while queue:
        level_size = len(queue)
        new_discovered = []

        for _ in range(level_size):
            node = queue.popleft()

            if node == end:
                # Reconstruct path
                path = []
                current = end
                while current is not None:
                    path.append(current)
                    current = parent[current]
                path.reverse()
                print(f"Final shortest path: {' -> '.join(path)}")
                return path

            for neighbor in graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = node
                    queue.append(neighbor)
                    new_discovered.append(neighbor)

        if new_discovered:
            print(f"Level {level}: New nodes discovered: {', '.join(new_discovered)}")
        level += 1

    print("No path found")
    return None

def dijkstra_cheapest_path(graph, start, end):
    """Find cheapest path using Dijkstra's algorithm in weighted graph."""
    queue = [(0, start)]  # (cost, node)
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}

    while queue:
        current_cost, current_node = heapq.heappop(queue)

        if current_cost > distances[current_node]:
            continue

        print(f"Selecting node {current_node} with cost {current_cost}")

        if current_node == end:
            # Reconstruct path
            path = []
            current = end
            while current is not None:
                path.append(current)
                current = previous[current]
            path.reverse()
            total_cost = distances[end]
            print(f"Cheapest path: {' -> '.join(path)}")
            print(f"Total cost: {total_cost}")
            return path, total_cost

        for neighbor, weight in graph[current_node]:
            distance = current_cost + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    print("No path found")
    return None, None

if __name__ == "__main__":
    print("=== Unweighted Graph: BFS Shortest Path from A to K ===")
    bfs_shortest_path(unweighted_graph, 'A', 'K')

    print("\n=== Weighted Graph: Dijkstra Cheapest Path from A to K ===")
    dijkstra_cheapest_path(weighted_graph, 'A', 'K')