# Disclaimer:
This code has not been peer reviewed, so it is by no means bulletproof :)

# Assumptions
-Max number of tags is limited by the max size of a tweet which is 280 chars.
-Tags should be case insensitive when building a graph, meaning 'Gretel' and 'gretel' make up the same vertex.
-The api to remove hashtags from tweet or list of tweets just looks at the hashtag list, not the tweet ids

# Approach
-Using a dictionary/hashmap for the graph means that inserting has O(1), and figuring out the edges is O(num_tags^2)
-Deleting a tweet again means figuring out the edges O(num_tags^2) and then removing from each node's adjacency list, which is O(1) since I am using a set.