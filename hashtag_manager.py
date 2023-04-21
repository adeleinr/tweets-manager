import json
import unittest
from collections import defaultdict, Counter


class HashtagManager:
    def __init__(self):
        self.total_edges = 0
        self.total_degree_sum = 0
        # {"tagA": ["tagB", "tagC"]}
        self.graph = defaultdict(set)
        # {"tagA": (num times tagA is referenced across all tweets)}
        # This is used for figuring out if a tag can be removed from
        # the graph completely when a tweet is deleted
        self.tag_counter = Counter()

    def build_graph(self, tweet_data_file):
        # Using input for reading one line at a time instead of bringing
        # the whole file into memory
        with open(tweet_data_file) as file:
            for line in file:
                tweet = json.loads(line)
                if "entities" in tweet:
                    hashtags = [
                        tag["text"]
                        for tag in tweet["entities"]["hashtags"]
                    ]
                    self.add(hashtags)

    def reset_graph(self):
        self.total_edges = 0
        self.total_degree_sum = 0
        self.graph = defaultdict(set)
        self.tag_counter = Counter()

    def add_edge(self, vertex_a, vertex_b):
        self.graph[vertex_a].add(vertex_b)
        self.total_edges += 1
        self.total_degree_sum += 1

    def delete_edge(self, vertex_a, vertex_b):
        self.graph[vertex_a].remove(vertex_b)
        self.total_edges -= 1
        self.total_degree_sum -= 1

    def compute_average_degree(self):
        if self.graph:
            return self.total_degree_sum/len(self.graph)
        return -1

    def add(self, hashtags):
        if hashtags:
            hashtags = list(set(map(str.lower, hashtags)))
            self.tag_counter.update(hashtags)
            for vertex_a in set(hashtags):
                if vertex_a not in self.graph:
                    self.graph[vertex_a] = set()
                for vertex_b in hashtags:
                    if vertex_a != vertex_b:
                        if vertex_b not in self.graph[vertex_a]:
                            self.add_edge(vertex_a, vertex_b)
                        if vertex_a not in self.graph[vertex_b]:
                            self.add_edge(vertex_b, vertex_a)

    def delete(self, hashtags):
        if hashtags:
            hashtags = list(set(map(str.lower, hashtags)))
            self.tag_counter.subtract(hashtags)
            for vertex_a in hashtags:
                if vertex_a not in self.graph:
                    # In the case try to remove a tweet that was never
                    # added to the graph to begin with, it is a no-op
                    return
                for vertex_b in hashtags:
                    if vertex_a != vertex_b:
                        if vertex_b in self.graph[vertex_a]:
                            self.delete_edge(vertex_a, vertex_b)
                        if vertex_a in self.graph[vertex_b]:
                            self.delete_edge(vertex_b, vertex_a)
                        # If this is the only tweet left that references this
                        # tag then we can remove it
                        if self.tag_counter[vertex_a] == 0:
                            del self.tag_counter[vertex_a]
                            self.graph.pop(vertex_a)
                        if self.tag_counter[vertex_b] == 0:
                            del self.tag_counter[vertex_b]
                            self.graph.pop(vertex_b)

    def load_new_tweets(self, tweets_file):
        self.build_graph(tweets_file)

    def delete_tweet(self, tweet_file):
        # Using input for reading one line at a time instead of bringing
        # the whole file into memory
        with open(tweet_file) as file:
            for line in file:
                tweet = json.loads(line)
                if "entities" in tweet:
                    hashtags = [
                        tag["text"]
                        for tag in tweet["entities"]["hashtags"]
                    ]
                    self.delete(hashtags)


class TestTweetParser(unittest.TestCase):
    hashtag_manager = HashtagManager()

    def test_loading_from_file(self):
        self.hashtag_manager.build_graph("tweets.txt")
        assert (
            abs(self.hashtag_manager.compute_average_degree() - 2.488) <= 0.01
        )
        self.hashtag_manager.reset_graph()

    def test_loading_new_tweets_from_file(self):
        self.hashtag_manager.load_new_tweets("tweets.txt")
        # Loading a dup of the tweet file should yielf no change
        # in the avg degree
        assert (
            abs(self.hashtag_manager.compute_average_degree() - 2.488) <= 0.01
        )
        self.hashtag_manager.reset_graph()

    def test_sunnyday(self):
        self.hashtag_manager.reset_graph()
        self.hashtag_manager.add(["Gretel", "data"])
        self.hashtag_manager.add(["data", "startup", "privacy"])
        self.hashtag_manager.add(["data"])
        self.hashtag_manager.add(["Gretel"])
        self.hashtag_manager.add(["rocketship", "Gretel"])
        self.hashtag_manager.add(["cats", "cats", "cats"])
        assert (
            abs(self.hashtag_manager.compute_average_degree() - 1.67) <= 0.01
        )

    def test_tweets_with_same_tags_arent_counted(self):
        self.hashtag_manager.reset_graph()
        self.hashtag_manager.add(["Gretel", "ai"])
        self.hashtag_manager.add(["Gretel", "ai"])
        self.hashtag_manager.add(["ai", "Gretel"])
        assert (self.hashtag_manager.compute_average_degree() == 1)

    def test_a_tag_duplicated_in_a_tweet_isnt_counted(self):
        self.hashtag_manager.reset_graph()
        self.hashtag_manager.add(["Gretel", "Gretel"])
        assert (self.hashtag_manager.compute_average_degree() == 0)

    def test_case_insensitive(self):
        self.hashtag_manager.reset_graph()
        self.hashtag_manager.add(["Gretel", "ai"])
        self.hashtag_manager.add(["gretel", "ai"])
        assert (self.hashtag_manager.compute_average_degree() == 1)

    def test_case_delete_tweet_tag_added_before(self):
        self.hashtag_manager.reset_graph()
        self.hashtag_manager.add(["Gretel"])
        self.hashtag_manager.add(["dragons", "tacos"])
        self.hashtag_manager.add(["gretel", "ai"])
        # 4 vertices
        assert (self.hashtag_manager.compute_average_degree() == 1)
        self.hashtag_manager.delete(["gretel", "ai"])
        # 3 vertices, 3 edges
        assert (
            abs(self.hashtag_manager.compute_average_degree() - 0.66) <= 0.01
        )

    def test_case_delete_tweet_tag_not_added_before(self):
        self.hashtag_manager.reset_graph()
        self.hashtag_manager.add(["dragons", "tacos"])
        self.hashtag_manager.add(["gretel", "ai"])
        # 4 vertices,  4 edges
        assert (self.hashtag_manager.compute_average_degree() == 1)
        self.hashtag_manager.delete(["gretel", "ai"])
        # 2 vertices, 2 edges
        assert (self.hashtag_manager.compute_average_degree() == 1)

    def test_case_add_delete_add_in_sequence(self):
        self.hashtag_manager.reset_graph()
        self.hashtag_manager.add(["dragons", "tacos"])
        self.hashtag_manager.add(["gretel", "ai"])
        # 4 vertices,  4 edges
        assert (self.hashtag_manager.compute_average_degree() == 1)
        self.hashtag_manager.delete(["gretel", "ai"])
        # 2 vertices, 2 edges
        assert (self.hashtag_manager.compute_average_degree() == 1)
        self.hashtag_manager.add(["gretel", "ai"])
        assert (self.hashtag_manager.compute_average_degree() == 1)


unittest.main()
