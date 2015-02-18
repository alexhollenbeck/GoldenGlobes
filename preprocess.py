print('Loading python libraries')
import json
import pickle
import nltk
import operator
import itertools
import re
import pdb
import sys
from classes import *
from collections import OrderedDict

if(sys.argv[1] =='gg15mini.json'):
    year = 2015
else:
    year = 2013

def createRelation(name, top_listAuthors, listWords, listKeywords, hashtag_list):
    """Creates a relation between tweets, keywords, relations"""

    Relation = relation()
    Relation.name = name
    Relation.reporters = top_listAuthors
    Relation.words_dict = listWords
    Relation.tags = hashtag_list
    Relation.tagwords = listKeywords

    return Relation

def processTweets(jObject, listKeywords, listAuthors, listWords, listUsers, listMentionedUsers):
    """Parses the tweet from the jObject and updates categories"""

    # Initialize objects
    twt = tweet()
    twt.text = jObject['text']
    twt.tweetId = jObject['id']
    athr = author()
    athr.tweets.append(twt)
    athr.userName = jObject['user']['screen_name']
    athr.userId = jObject['user']['id']

    # Extract text
    text = nltk.wordpunct_tokenize(twt.text)
    
    hashtag = False
    mention = False
    retweet = False
    properNoun = False
    recent = False

    # Sort words
    for word in text:
        if hashtag and (word not in listKeywords):
            hashtag = False
            listKeywords[word] = 1
        if hashtag and (word in listKeywords):
            hashtag = False
            votes = listKeywords[word]
            listKeywords[word] = votes + 1
            
        # Increment author and tweet scores
        if retweet and mention:
                mention = False
                retweet = False

        # Create a mentioned user for users not in the list
                if (word not in listUsers) and (word not in listMentionedUsers):

                    mentionedUserAthr = author()
                    mentionedUserAthr.userName = word
                    mentionedUserAthr.score = 1
                    mentionedUserAthr.userId = -1
                    mentionedUserTwt = tweet()
                    mentionedUserTwt.text = twt.text
                    mentionedUserTwt.score = 1
                    mentionedUserTwt.tweetId = -1
                    mentionedUserAthr.tweets.append(mentionedUserTwt)
                    listMentionedUsers[word] = mentionedUserAthr
                    recent = True

                if (word in listMentionedUsers) and not recent:

                    exists = False
                    mentionedUser = listMentionedUsers[word]
                    mentionedUserTwt = tweet()
                    mentionedUserTwt.text = twt.text
                    for mt in mentionedUser.tweets:
                        if mentionedUserTwt.text == mt.text:
                            exists = True
                            mt.score = mt.score + 1
                    if exists != True:
                        mentionedUser.tweets.append(mentionedUserTwt)
                    mentionedUser.score = mentionedUser.score + 1

                if (not recent) and (word in listUsers):

                    id = listUsers[word]
                    mentioned = listAuthors[id]
                    found = False

                    for t in mentioned.tweets:
                        if t.text in twt.text:
                            found = True
                            t.score = t.score + 1

                    if not found:
                        newTweet = tweet()
                        newTweet.text = twt.text
                        mentioned.tweets.append(newTweet)

                    mentioned.score = mentioned.score + 1

        # Categorize twitter symbols
        if '@' in word:
            mention = True
        if 'RT' in word:
            retweet = True
        if '#' in word:
            hashtag = True

        # Increment or add word
        if word not in listWords:
            listWords[word] = 1
        else:
            freq = listWords[word]
            listWords[word] = freq + 1

    # Increment or add author
    if athr.userId not in listAuthors:
        listAuthors[athr.userId] = athr
        listUsers[athr.userName] = athr.userId
    else:
        listAuthors[athr.userId].tweets.append(twt)

def keywordCheck(string):
    """Check to see if the word is not a symbol or short word"""
    if ((string != 'RT') 
    and (string != '#') 
    and (string != '@') 
    and (string != 'the') 
    and (string != 'is') 
    and (string != 'I') 
    and (string != 't')
    and (string != '"')
    and (string != 's')
    and (string != 'and')
    and (string != 'for')
    and (string != 'like')
    and (string != 'not')
    and (string != 'she')
    and (string != 'an')
    and (string != 'in')
    and (string != 'at')
    and (string != 'http')
    and (string != 'it')
    and (string != 'me')
    and (string != 'this')
    and (string != 'my')
    and (string != 'The')
    and (string != 'he')):
        return True
    else:
        return False
            
def main():

    # Initialize
    file_data = []
    json_data = []
    hashtags = {}
    keywords = {}
    words = {} 
    authors = {}
    mentionedUserAuthors = {}
    userIdTable = {}
    properNouns = []
    properPhrases = []
    top_authors = []

    # Data location
    json_file = sys.argv[1]

    # Data loading
    with open(json_file, 'r') as f:   
        text = f.readline()
        json_data = json.loads(text)

    print('Loading libraries COMPLETED.  Pre-processing tweets...')

    # Text parsing
    progress = 0
    for item in json_data:
        progress = progress + 1
        if progress % 10000 == 0:
            print str(progress) + ' tweets processed'
        try:
            processTweets(item, hashtags, authors, words, userIdTable, mentionedUserAuthors)
        except:
            print(item['id'])
            print('An error occurred parsing this line')
            print(item['created_at'])

    # Begin
    print('Loading ', json_file, '...')

    print('Processing keywords')
    for word in words:
        if word in hashtags:
            if word not in keywords:
                keywords[word] = words[word]

    # Strip twitter symbols
    print('Stripping twitter symbols')
    filtered_keywords = {}
    for keyword in keywords:
        if keywordCheck(keyword):
            filtered_keywords[keyword] = keywords[keyword]
    
    # Arrange items by score
    print('Sorting items by popularity')
    hashtagsSorted = OrderedDict(sorted(hashtags.items(), key=lambda hashtags: hashtags[1], reverse=True))
    usersSorted = OrderedDict(sorted(authors.items(), key=lambda authors: authors[1].score, reverse=True))
    sorted_keywords = OrderedDict(sorted(filtered_keywords.items(), key=lambda filtered_keywords: filtered_keywords[1], reverse=True))

    print('Writing top tweets, users, and hashtags to file')

    with open('popular_hashtags'+str(year)+'.txt', 'w') as output:
        for word in hashtagsSorted:
            try:
                output.write(word)
                output.write('\r')
            except:
                output.write('Cannot process hashtag \r')

    with open('popular_users'+str(year)+'.txt', 'w') as output:
        for user in usersSorted:
            try:
                output.write(usersSorted[user].userName)
                output.write(' ')
                output.write(str(usersSorted[user].score))
                output.write('\r')
            except:
                output.write('Cannot process user\r')

    with open('popular_tweets'+str(year)+'.txt', 'w') as output:
        for athr in usersSorted.values():
            i = 0
            if athr.userName == 'goldenglobes':
                pass
            i = i + 1
            if i<2500:
                try:
                    if i<20:
                        output.write(athr.userName)
                        output.write('\r')
                except:
                    print('Cannot interpret username')
                for twt in athr.tweets:
                    try:
                        if i<20:
                            output.write('   ')
                            output.write(twt.text)
                            output.write('\r')
                    except:
                        output.write('Cannot process tweet\r')
    userTweetRelation = createRelation('Golden Globes', usersSorted.values(), words, keywords, hashtags)

    with open('userTweetRelation'+str(year)+'.txt', 'wb') as output:
        pickle.dump(userTweetRelation, output)

    print('Processing Complete')

    return


main()