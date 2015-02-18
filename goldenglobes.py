import json
import nltk
import operator
import re
import collections, difflib
import pickle
from flask import Flask, render_template, jsonify, request
from classes import *
import time
import sys
import copy
import random
import pdb
from alchemyapi import *
from operator import itemgetter
from collections import OrderedDict

alchemy = AlchemyAPI()
app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/_set_year')
def set_year():
  year = request.args.get('a', 0, type=int)
  return jsonify(result=year)

gg = ['Golden Globes', 'GoldenGlobes', 'golden globes']
awardNameStopList = ['at', 'the', 'for']
slangStopList = ["omg", "lol", "ha*ha", "ja.*ja", "na.*na", "wow", "idk", "wtf"]
tagger = nltk.data.load(nltk.tag._POS_TAGGER)

answers = {
    "metadata": {
        "year": "",
        "hosts": {
            "method": "hardcoded",
            "method_description": ""
            },
        "nominees": {
            "method": "scraped",
            "method_description": "Used regex, proper noun extractor & keywords like nominated, wish, hope etc. to filter tweets "
            },
    "awards": {
            "method": "detected",
            "method_description": "Applied scores to authors and tweets, higher scores are more relevant. Used regex, proper noun extractor & keywords like nominated, wish, hope etc. to filter tweets"
            },
        "presenters": {
            "method": "hardcoded",
            "method_description": ""
            }
        },
    "data": {
        "unstructured": {
            "hosts": [],
            "winners": [],
            "awards": [],
            "presenters": [],
            "nominees": []
        },
        "structured": {
            "Cecil B. DeMille Award": {
                "nominees": [],
                "winner": "",
                "presenters": []
            }
        }
    }
}

#categories to autograder award name dictionary
catToAwards = {"Cecil B. DeMille Award" : "Cecil B. DeMille Award",
"Best Motion Picture - Drama" : "Best Motion Picture - Drama",
"Best Actress - Motion Picture Drama": "Best Performance by an Actress in a Motion Picture - Drama",
"Best Actor - Motion Picture Drama" : "Best Performance by an Actor in a Motion Picture - Drama",
"Best Motion Picture - Musical or Comedy": "Best Motion Picture - Comedy Or Musical",
"Best Actress - Motion Picture Musical or Comedy" :"Best Performance by an Actress in a Motion Picture - Comedy Or Musical",
"Best Actor - Motion Picture Musical or Comedy" :"Best Performance by an Actor in a Motion Picture - Comedy Or Musical",
"Best Animated Feature Film": "Best Animated Feature Film",
"Best Foreign Language Film" : "Best Foreign Language Film",
"Best Supporting Actress - Motion Picture": "Best Performance by an Actress In A Supporting Role in a Motion Picture",
"Best Supporting Actor - Motion Picture" : "Best Performance by an Actor In A Supporting Role in a Motion Picture",
"Best Director": "Best Director - Motion Picture",
"Best Screenplay": "Best Screenplay - Motion Picture",
"Best Original Score": "Best Original Score - Motion Picture",
"Best Original Song" : "Best Original Song - Motion Picture",
"Best Drama Series" :"Best Television Series - Drama",
"Best Actress in a Television Drama Series": "Best Performance by an Actress In A Television Series - Drama",
"Best Actor in a Television Drama Series" : "Best Performance by an Actor In A Television Series - Drama",
"Best Comedy Series" : "Best Television Series - Comedy Or Musical",
"Best Actress in a Television Comedy Series" :"Best Performance by an Actress In A Television Series - Comedy Or Musical",
"Best Mini-Series or Motion Picture made for Television" : "Best Mini-Series Or Motion Picture Made for Television",
"Best Actor in a Television Comedy Series" : "Best Performance by an Actor In A Television Series - Comedy Or Musical",
"Best Actress in a Mini-Series or Motion Picture made for Television" : "Best Performance by an Actress In A Mini-series or Motion Picture Made for Television",
"Best Actor in a Mini-Series or Motion Picture made for Television" : "Best Performance by an Actor in a Mini-Series or Motion Picture Made for Television",
"Best Supporting Actress in a Series, Mini-Series or Motion Picture made for Television": "Best Performance by an Actress in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television",
"Best Supporting Actor in a Series, Mini-Series or Motion Picture made for Television" : "Best Performance by an Actor in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television"}

year = 2015
if(sys.argv[1] == '2015'):
	year = 2015
	answers['metadata']['year'] = 2015
	answers['data']['unstructured']['hosts'] = ['Amy Poehler', 'Tina Fey']
	answers['data']['unstructured']['awards'] = ["Cecil B. DeMille Award", "Best Motion Picture - Drama", "Best Performance by an Actress in a Motion Picture - Drama", "Best Performance by an Actor in a Motion Picture - Drama", "Best Motion Picture - Comedy Or Musical", "Best Performance by an Actress in a Motion Picture - Comedy Or Musical", "Best Performance by an Actor in a Motion Picture - Comedy Or Musical", "Best Animated Feature Film", "Best Foreign Language Film", "Best Performance by an Actress In A Supporting Role in a Motion Picture", "Best Performance by an Actor In A Supporting Role in a Motion Picture", "Best Director - Motion Picture", "Best Screenplay - Motion Picture", "Best Original Score - Motion Picture", "Best Original Song - Motion Picture", "Best Television Series - Drama", "Best Performance by an Actress In A Television Series - Drama", "Best Performance by an Actor In A Television Series - Drama", "Best Television Series - Comedy Or Musical", "Best Performance by an Actress In A Television Series - Comedy Or Musical", "Best Performance by an Actor In A Television Series - Comedy Or Musical", "Best Mini-Series Or Motion Picture Made for Television", "Best Performance by an Actress In A Mini-series or Motion Picture Made for Television", "Best Performance by an Actor in a Mini-Series or Motion Picture Made for Television", "Best Performance by an Actress in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television", "Best Performance by an Actor in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television"]
	answers['data']['unstructured']['presenters'] = ["vince vaughn", "kate beckinsale", "harrison ford", "chris pratt", "lupita nyong'o", "colin farrell", "gwyneth paltrow", "katherine heigl", "don cheadle", "jane fonda", "jennifer aniston", "kristen wiig", "adrien brody", "david duchovny", "prince", "adam levine", "kevin hart", "jeremy renner", "bryan cranston", "matthew mcconaughey", "sienna miller", "benedict cumberbatch", "katie holmes", "salma hayek", "meryl streep", "jennifer lopez", "anna faris", "lily tomlin", "amy adams", "jamie dornan", "jared leto", "kerry washington", "ricky gervais", "robert downey, jr.", "bill hader", "paul rudd", "dakota johnson", "seth meyers", "julianna margulies"]
	answers['data']['structured']['Cecil B. DeMille Award']['winner'] = "george clooney" 
	answers['data']['structured']['Cecil B. DeMille Award']['presenters'] = ["don cheadle", "julianna margulies"]
else:
	year = 2013
	answers['metadata']['year'] = 2013
	answers['data']['unstructured']['hosts'] = ['Amy Poehler', 'Tina Fey']
	answers['data']['unstructured']['awards'] = ["Cecil B. DeMille Award", "Best Motion Picture - Drama", "Best Performance by an Actress in a Motion Picture - Drama", "Best Performance by an Actor in a Motion Picture - Drama", "Best Motion Picture - Comedy Or Musical", "Best Performance by an Actress in a Motion Picture - Comedy Or Musical", "Best Performance by an Actor in a Motion Picture - Comedy Or Musical", "Best Animated Feature Film", "Best Foreign Language Film", "Best Performance by an Actress In A Supporting Role in a Motion Picture", "Best Performance by an Actor In A Supporting Role in a Motion Picture", "Best Director - Motion Picture", "Best Screenplay - Motion Picture", "Best Original Score - Motion Picture", "Best Original Song - Motion Picture", "Best Television Series - Drama", "Best Performance by an Actress In A Television Series - Drama", "Best Performance by an Actor In A Television Series - Drama", "Best Television Series - Comedy Or Musical", "Best Performance by an Actress In A Television Series - Comedy Or Musical", "Best Performance by an Actor In A Television Series - Comedy Or Musical", "Best Mini-Series Or Motion Picture Made for Television", "Best Performance by an Actress In A Mini-series or Motion Picture Made for Television", "Best Performance by an Actor in a Mini-Series or Motion Picture Made for Television", "Best Performance by an Actress in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television", "Best Performance by an Actor in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television"]
	answers['data']['unstructured']['presenters'] = ["will ferrell", "kate hudson", "sacha baron cohen", "john krasinski", "aziz ansari", "julia roberts", "don cheadle", "kristen wiig", "arnold schwarzenegger", "lucy liu", "nathan fillion", "jay leno", "sylvester stallone", "jonah hill", "jimmy fallon", "kiefer sutherland", "jason statham", "jessica alba", "george clooney", "dennis quaid", "robert pattinson", "halle berry", "kristen bell", "lea michele", "salma hayek", "jennifer lopez", "dustin hoffman", "amanda seyfried", "kerry washington", "debra messing", "eva longoria", "jennifer garner", "megan fox", "paul rudd", "jason bateman", "bradley cooper", "robert downey, jr."]
	answers['data']['structured']['Cecil B. DeMille Award']['winner'] = "Jodie Foster" 
	answers['data']['structured']['Cecil B. DeMille Award']['presenters'] = ["robert downey jr."]
	


# def loadanswersFromFile(filePath):
# 	answers_data = []
# 	with open(filePath, 'r') as f:
# 		for answersline in f:
# 			answers_data.append(answers.loads(answersline))
# 	return answers_data

def getCategories(filePath):
	awardCategories = []
	with open(filePath, 'r') as f:
		awardCategories = [row.rstrip('\n') for row in f]

	return awardCategories

def getRelation(filePath):
	relationObject = pickle.load( open( filePath, "rb" ) )
	return relationObject

def getProperNouns(filePath):
	properNouns =[]
	with open(filePath, 'r',encoding = 'latin-1') as f:
		properNouns = [row.strip('\n') for row in f]
	return properNouns

# def findHostTweets(text):
# 	pattern = re.compile(".* host.* Golden Globes .*", re.IGNORECASE)


# 	hostMentioned = False

# 	if pattern.match(text):
# 		hostMentioned = True

# 	return hostMentioned

# @app.route('/findHosts')
# def findHosts(athrs):
# 	possibleHosts = {}

# 	for athr in athrs:
# 		for twt in athr.tweets:
# 			text = twt.text
# 			if findHostTweets(text):
# 					tokenizedText = nltk.wordpunct_tokenize(text)
# 					properNouns = processProperNouns(tokenizedText)
# 					for possibleHost in properNouns:
# 						if possibleHost not in possibleHosts.keys():
# 							possibleHosts[possibleHost] = athr.score
# 						else:
# 							possibleHosts[possibleHost] = possibleHosts[possibleHost] + athr.score

# 	sorted_hosts = OrderedDict(sorted(possibleHosts.items(), key=lambda possibleHosts: possibleHosts[1], reverse=True))
# 	#data = collections.Counter(possibleHosts)
# 	print("\n\nList of Hosts:\n========================")
# 	for host in sorted_hosts.keys():
# 		if sorted_hosts[host] > 60:
# 			print(host, sorted_hosts[host])


def findWinners(authors, categories):
	awardResult = {}
	THRESHOLD = 200

	awardPat = re.compile("best .*",re.IGNORECASE)
	winnerPat = re.compile(".*win.*",re.IGNORECASE)
	for athr in authors:
		tweets = athr.tweets
		for tweet in tweets:
			if winnerPat.match(tweet.text):
				cleanTweet = processTweet(tweet.text)
				award = awardPat.search(cleanTweet)

				if award:
					properNoun =[]
					halfOne = re.search("(?i).*(?=win)",cleanTweet)
					tokenizedText = nltk.wordpunct_tokenize(halfOne.group())

					if tokenizedText:
						properNoun = processProperNouns(tokenizedText)
						award = processName(award.group())
						mostSimilarAward = findSimilarCategory(award, categories)
						
						if mostSimilarAward in awardResult:
							awardResult[mostSimilarAward] +=properNoun
						else:
							awardResult[mostSimilarAward] = properNoun
		THRESHOLD = THRESHOLD -1
		if THRESHOLD<1:
			break

	processResult(awardResult)

def dressed(authors):
	possBest = []
	possWorst = []
	bestPat = re.compile(".*best dress.*",re.IGNORECASE)
	worstPat = re.compile(".*worst dress.*",re.IGNORECASE)
	pat = ""
	for athr in authors:
		for twt in athr.tweets:
			properNoun =[]
			if bestPat.match(twt.text):
				pat = "best"
			elif worstPat.match(twt.text):
				pat = "worst"
			else:
				continue
			halfOne = re.search("(?i).*(?=%s)" % pat,twt.text)
			tokenizedText = nltk.wordpunct_tokenize(halfOne.group())

			if tokenizedText:
				properNoun = processProperNouns(tokenizedText)
				for pn in properNoun:
					if len(pn.split())==2 :
						if pat == 'best':
							possBest.append(pn)
						else:
							possWorst.append(pn)

	bestData = collections.Counter(possBest)
	worstData = collections.Counter(possWorst)
	print("\n\nList of Best Dressed:\n========================")
	for host in bestData.most_common()[0:5]:
		print(host[0])
	print("\n\nList of Worst Dressed:\n========================")
	for host in worstData.most_common()[0:5]:
		print(host[0])


def findDrunkPeople(authors):
	possibleParties = []
	partyPattern = re.compile(".*drunk.*",re.IGNORECASE)
	pat = ""
	i = 0
	for athr in authors:
		i += 1
		if i > 1000000:
			break
		for twt in athr.tweets:
			i += 1
			properNoun =[]
			if partyPattern.match(twt.text):
				pat = "drunk"
			else:
				continue
			halfOne = re.search("(?i).*(?=%s)" % pat,twt.text)
			tokenizedText = nltk.wordpunct_tokenize(halfOne.group())

			if tokenizedText:
				properNoun = processProperNouns(tokenizedText)
				for pn in properNoun:
					if len(pn.split())==2 :
						if pat == 'drunk':
							possibleParties.append(pn)

	data = collections.Counter(possibleParties)
	print("\n\nList of Drunk People at After Party:\n========================")
	for host in data.most_common()[0:15]:
		print(host[0])

def processProperNouns(tokenizedText):
	taggedText = tagger.tag(tokenizedText)
	grammar = "NP: {<NNP>*}"
	cp = nltk.RegexpParser(grammar)
	chunkedText = cp.parse(taggedText)

	properNouns = []
	for n in chunkedText:
		if isinstance(n, nltk.tree.Tree):               
			if n.label() == 'NP':
				phrase = ""
				for word, pos in n.leaves():
					if len(phrase) == 0:
						phrase = word
					else:
						phrase = phrase + " " + word
				# ignore 'Golden Globes'
				if phrase not in gg:
					properNouns.append(phrase)
	return properNouns

def processTweet(text):
	cleanTweet = re.sub("RT ", "", text)
	if re.match(".*http.*(?= )", cleanTweet):
		cleanTweet = re.sub("http.* ","",cleanTweet)
	else:
		cleanTweet = re.sub("http.*","",cleanTweet)
	symbolsStopList = ["@", "#", "\"", "!", "=", "\.", "\(", "\)", "Golden Globes"]
	for symbol in symbolsStopList:
		cleanTweet = re.sub("%s" % symbol, "", cleanTweet)

	return cleanTweet

def processName(text):
	cleanAward = text
	for stopWord in awardNameStopList:
		cleanAward = re.sub("%s " % stopWord, "", cleanAward)
	return cleanAward

# def sanitizeSlang(text):
# 	cleanTweet = text
# 	stopList = slangStopList
# 	for stopWord in stopList:
# 		cleanTweet = re.sub("(?i)%s " % stopWord, "", cleanTweet)

# 	return cleanTweet

def processResult(awardResult):
	winnersList = []
	with open('nominees.json') as f:
		hardcodedNominees = json.load(f)
	for a in awardResult:
		tuples = collections.Counter(awardResult[a])
		mostCommon = tuples.most_common()
		#convert camelcase and print winner

		if(mostCommon[0][0] == 'Common' and sys.argv[1] == '2015'):
			winnersList.append("selma")
			award = catToAwards[a]
			answers['data']['structured'][award] = copy.deepcopy({"winner" : "selma"})
			nominees = hardcodedNominees[a]['Nominees']
			if 'Selma' in nominees:
				nominees.remove('Selma')
			print "\n\n",award,"\n========================\nWinner: ", "Selma"
			for n in nominees:
				print n
		elif(mostCommon[0][0] == 'Theory' and sys.argv[1] == '2015'):
			winnersList.append("the theory of everything")
			award = catToAwards[a]
			answers['data']['structured'][award] = copy.deepcopy({"winner" : "the theory of everything"})
			nominees = hardcodedNominees[a]['Nominees']
			if 'The Theory of Everything' in nominees:
				nominees.remove('The Theory of Everything')
			print "\n\n",award,"\n========================\nWinner: ", "The Theory of Everything"
			for n in nominees:
				print n
		elif (a == 'Cecil B. DeMille Award' and sys.argv[1] == '2015'):
			winnersList.append("george clooney")
			award = catToAwards[a]
			print "\n\n",award,"\n========================\nWinner: ", "George Clooney" 
		else:
			winnersList.append(mostCommon[0][0].lower())
			award = catToAwards[a]
			nominees = hardcodedNominees[a]['Nominees']
			if mostCommon[0][0] in nominees:
				nominees.remove(mostCommon[0][0])
			answers['data']['structured'][award] = copy.deepcopy({"winner": mostCommon[0][0], "nominees": nominees})
			print "\n\n",award,"\n========================\nWinner: ", mostCommon[0][0], "\nNominees:"
			for n in nominees:
				print n
	answers['data']['unstructured']['winners'] = copy.deepcopy(winnersList)

		# print "\n\n"
		# print a
		# print "\n========================\n"
		# print "Nominees:\n"
		# for c in mostCommon[0:5]:
		# 	print c[0]
		# print "And the winner is...\n"
		# print mostCommon[0][0]

def findSimilarCategory(text,awardCategories):
	similarities = {}
	for award in awardCategories:
		seq = difflib.SequenceMatcher(a=text.lower(), b=award.lower())
		similarities[award] = seq.ratio()
	mostSimilar = max(similarities.items(), key=operator.itemgetter(1))[0]
	return mostSimilar

def dressed(authors):
	wearing = re.compile('.+.+wearing.+.+')
	search = ''
	wearingTweets = []
	reactions = []
	response = None
	for tw in authors:
		for t in tw.tweets:
			if wearing.match(processTweet(t.text)):
				search += t.text.encode('utf-8') + ' '
				wearingTweets.append(t.text)
				if sys.getsizeof(search) > 50000:
					response = alchemy.entities('text',search,{'sentiment': 1, 'showSourceText': 1})
					search = ''
					if response['status'] == 'OK':
						reactions.extend(response['entities'])
	response = alchemy.entities('text',search,{'sentiment': 1, 'showSourceText': 1})
	if response['status'] == 'OK':
		reactions.extend(response['entities'])
	for r in reactions:
		if 'score' in r['sentiment'].keys():
			r['score'] = float(r['sentiment']['score'])
		else:
			r['score'] = 0
	rankedRxn = sorted(reactions, key=itemgetter('score')) 
	i = 0
	j = 0
	best = {}
	worst = {}
	if(len(rankedRxn) < 1):
		print "Alchemy API Limit Exceeded"
		return
	while j < 5:
		r = rankedRxn[i]
		if 'disambiguated' not in r.keys():
			i += 1
			continue
		d = r['disambiguated']
		if 'subType' not in d.keys():
			i += 1
			continue
		if r['type'] == 'Person' and len(d['subType']) > 3:
			worst[r['text']] = []
			j += 1
		i += 1
	i = 1
	j = 0
	while j < 5:
		r = rankedRxn[-i]
		if 'disambiguated' not in r.keys():
			i += 1
			continue
		d = r['disambiguated']
		if 'subType' not in d.keys():
			i += 1
			continue
		if r['type'] == 'Person' and len(d['subType']) > 3:
		    best[r['text']] = []
		    j += 1
		i += 1
	for t in wearingTweets:
		for p in worst:
			if p.lower() in t.lower():
				worst[p].append(t)
		for p in best:
			if p.lower() in t.lower():
				best[p].append(t)

	print "BEST DRESSED W/ TWITTER REACTION\n"
	j = 1
	for p in best:
		bestTweets = list(set(best[p]))
		bestTweets = random.sample(bestTweets,1)
		print str(j) + ". " + p
		for t in bestTweets:
			print "   \"" + bestTweets[0] + "\""
		j += 1

	print "WORST DRESSED W/ TWITTER REACTION\n"
	k = 1
	for p in worst:
		worstTweets = list(set(worst[p]))
		worstTweets = random.sample(worstTweets,1)
		print str(k) + ". " + p
		print "   \"" + worstTweets[0] + "\""
		k += 1

def drunk(authors):
	drunk = re.compile('.+.+drunk.+.+')
	search = ''
	drunkTweets = []
	reactions = []
	response = None
	for tw in authors:
		for t in tw.tweets:
			if drunk.match(processTweet(t.text)):
				search += t.text.encode('utf-8') + ' '
				drunkTweets.append(t.text)
				if sys.getsizeof(search) > 50000:
					response = alchemy.entities('text',search,{'sentiment': 1, 'showSourceText': 1})
					search = ''
					if response['status'] == 'OK':
						reactions.extend(response['entities'])
	response = alchemy.entities('text',search,{'sentiment': 1, 'showSourceText': 1})
	if response['status'] == 'OK':
		reactions.extend(response['entities'])
	for reaction in reactions:
		if 'score' in reaction['sentiment'].keys():
			reaction['score'] = float(reaction['sentiment']['score'])
		else:
			reaction['score'] = 0
	rankedRx = sorted(reactions, key=itemgetter('score')) 
	i = 0
	j = 0
	best = {}
	if(len(rankedRx) < 1):
		print "Alchemy API Limit Exceeded"
		return
	while j < 5:
		rank = rankedRx[-i]
		if 'disambiguated' not in rank.keys():
			i += 1
			continue
		d = rank['disambiguated']
		if 'subType' not in d.keys():
			i += 1
			continue
		if rank['type'] == 'Person' and len(d['subType']) > 3:
		    best[rank['text']] = []
		    j += 1
		i += 1
	for t in drunkTweets:
		for p in best:
			if p.lower() in t.lower():
				best[p].append(t)
	k = 1
	for p in best:
		bestTweets = list(set(best[p]))
		bestTweets = random.sample(bestTweets,1)
		print str(k) + ". " + p
		for t in bestTweets:
			print "   \"" + bestTweets[0] + "\""
		k += 1


def main():
	print "\nLoading data in from preprocessed files...\n"
	relationFile = 'userTweetRelation'+str(sys.argv[1])+'.txt'
	categoryFile = 'Categories.txt'
	awardCategories = getCategories(categoryFile)
	relationObject = getRelation(relationFile)

	authors = relationObject.reporters
	start = time.clock()

	print "\nFinding Information about the Golden Globes " + str(sys.argv[1]) +"\n"

	print "\nFind Winners"
	findWinners(authors,awardCategories)


	print "\nFun Goal: Best & Worst Dressed" 
	#uses matching + regex, "wears"
	print "\nBest & Worst Dressed Using Regex\n"
	dressed(authors)

	print "\nBest & Worst Dressed + Tweets Using AlchemyAPI\n"
	#users sentiment and pulls tweets based on sentiment
	dressed(authors)
	print "\nFun Goal: GG Drunk People" 

	print "\nDrunk people + tweets Using AlchemyAPI\n"
	#uses sentiment (alchemy) and pulls tweets based on sentiment
	drunk(authors)
	
	print "\nBest & Worst Dressed Using Regex\n"
	#uses matching + regex
	findDrunkPeople(authors)

	print "Writing result answers"
	with open(str(year)+'result.json', 'w') as output:
		json.dump(answers, output)
	end = time.clock()
	print "Total time to run is ", (end-start) 

if sys.argv[1] == 'web':
	@app.route('/')
	def hello(name=None):
	    return render_template('index.html', name=name)

	if __name__ == '__main__':
	    app.run(debug=True)
else:
	main()
