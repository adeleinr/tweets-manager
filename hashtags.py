import fileinput
import json
from collections import defaultdict

class HashtagManager:
    def __init__(self, tweets_data_file):
        self.average_degree = 0
        self.total_vertices = 0
        self.total_edges = 0
        self.total_degree_sum = 0
        self.graph = defaultdict(set)
        self._build_graph(tweets_data_file)

    def _build_graph(self, tweet_data_file):
        # Using input for reading one line at a time instead of bringing the whole file into memory
        for line in fileinput.input([tweet_data_file]):
            tweet = json.loads(line)
            if "entities" in tweet:
                print(tweet["entities"]["hashtags"])
                hashtags = tweet["entities"]["hashtags"][0]["text"]
                self._add(hashtags)

    def compute_average_degree(self):
        if self.graph:
            return self.total_degree_sum/self.total_vertices
        return -1

    def _add(self, hashtags):
        for vertex_a in hashtags:
            # Not using map change all to lower to reduce
            # iterations over the list
            vertex_a = vertex_a.lower()
            if vertex_a not in self.graph:
                self.graph[vertex_a] = set()
                self.total_vertices += 1
            for vertex_b in hashtags:
                vertex_b = vertex_b.lower()
                if vertex_a != vertex_b:
                    if vertex_b not in self.graph[vertex_a]:
                        self.graph[vertex_a].add(vertex_b)
                        self.total_edges += 1
                        self.total_degree_sum += 1
                    if vertex_b not in self.graph:
                        self.total_vertices += 1
                    if vertex_a not in self.graph[vertex_b]:
                        self.graph[vertex_b].add(vertex_a)
                        self.total_edges += 1
                        self.total_degree_sum += 1

    def add_new_tweets(self, tweets_file):
        self._build_graph(tweets_file)


hashtag_manager = HashtagManager("tweets_test.txt")
print(hashtag_manager.graph)
print(hashtag_manager.total_vertices)
print(hashtag_manager.total_degree_sum)
print(hashtag_manager.compute_average_degree())

print(hashtag_manager.add_new_tweets("new_tweets_test.txt"))
print(hashtag_manager.total_vertices)
print(hashtag_manager.total_degree_sum)
print(hashtag_manager.compute_average_degree())
