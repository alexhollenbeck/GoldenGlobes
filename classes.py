class tweet:
    def __init__(self):
        self.text = ''
        self.score = 1
        self.tweetId = 0

class author:
    def __init__(self):
        self.score = 1
        self.tweets = []
        self.userName = ''
        self.userId = 0

class relation:
    def __init__(self):
        self.name = ''
        self.id = 0
        self.reporters = []     
        self.tags = {}          
        self.tagwords = {}      
        self.words_dict = {}    