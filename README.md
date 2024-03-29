# Disclaimer:
This code has not been peer reviewed, so it is by no means bulletproof :). There are probably many other edge cases to test still.

# Assumptions
1. Max number of tags is limited by the max size of a tweet which is 280 chars.
2. Tags should be case insensitive when building a graph, meaning 'Gretel' and 'gretel' make up the same vertex.
3. The api to remove hashtags from tweet or list of tweets just looks at the hashtag list, not the tweet ids

# Approach
Using a dictionary/hashmap for the graph means that inserting has O(1), and figuring out the edges is O(num_tags^2)

Deleting a tweet again means figuring out the edges O(num_tags^2) and then removing from each node's adjacency list, which is O(1) since I am using a set.

As far as keeping a large graph in memory there are packages out there (which I haven't used btw) that minimize the mem footprint of graphs, like StellarGraph I think.

# To Run
To run all unit tests including sanity unit tests that run agains the tweets.txt file:
`python hashtag_manager.py`
