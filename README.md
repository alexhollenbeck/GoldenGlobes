# GoldenGlobes - Tasha McKinney, Alex Hollenbeck, Shikhar Mohan, Zak Allen
>NLP project to extract Golden Globes winners and other information from Twitter data

We detected the winners from the entire corpus of tweets by reorganizing the corpus and sorting by popular twitter users (attributing a score to each author determined by use of relevant hashtags, keywords, number of mentions and retweets) and the tweets they sent out during the event. In addition to this, we used regular expressions to extract unigrams and bigrams for relevant tasks. We searched tweets for keywords indicating the award and the winner, split the tweet to two components (one that contained the actor name and the other that contained the award name). We also stripped the official GG award names to simpler, more concise names because those were commonly used in tweets. 

We tried detecting nominees using the method above, however the highest percentage we obtained was 62% correct according to the autograder, so we decided 


### GUI

We used Flask and the results of running goldenglobes.py to show the winners, hosts, nominees of the awards in 2015 and 2013. We used the names provided by the python script to pull Wikipedia images and info. 

#### Fun Goals

1. Best & Worst Dressed  (using 2 methods)
2. Who was drunk at the golden globes? 

	Method 1: Regex (function name - BestAndWorstDressed, findDrunkPeople)

	Similar to how we found winners, we used regular expessions/keywords to obtain a subset of tweets relating to dresses people wore during the awards. The results of this was quite accurate, even more so than the alchemy api version. 

	Method 2: Alchemy API (function name - dressed, drunk)

	Here we let Alchemy do most of the work. 

	Dressed - Here we narrowed down tweets to a subset and then used sentiment analysis to order the tweets. Getting the best dressed, we chose the top 5 from that list and worst dressed was the bottom 5.
	Drunk - After narrowing a subset of the tweets down to the ones that were relevant, we were able to use entity extraction for actress/actor names associated with being drunk. 

	The cool thing about alchemy was that it let us extract and display relevant tweets for both fun goals.


To run the project in command line for 2015. For 2013 replace the year. - `python goldenglobes.py 2015`
To run the web GUI - `python goldenglobes.py web` This will start the Flask app & server
