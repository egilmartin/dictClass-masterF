# -*- coding: utf-8 -*-
# author: Kyusong Lee
from __future__ import unicode_literals  # at top of module

import random
import re

from nltk import tokenize
from pymongo import MongoClient

# redis is a data structure store used in communication with dialcrowd
from database.redis_api import RedisAPI

# Edu is the class for the cloze game which will be connected to dialcrowd
class Edu(object):
    # need to add text for extra divs - grid and scratchpad,
    # add SSML tabs to cut up speech or check if this is already being done using <p> tags (Tony?)
    # Expand game sequence to add scratchpad step
    def __init__(self):
        #intro = "*en-GB* Welcome to Clozer. You're going to hear a story. Close your eyes and listen."
        intro = "*en-GB*Welcome to Clozer.*en-GB*You're going to hear a short passage.*en-GB*So.*en-GB*Close your eyes.*en-GB*Relax and listen carefully."
        #client = MongoClient(host="mongodb://kyusong:ianlee1022@ds251362.mlab.com:51362/dictclass")
        # this sets up access to the mongodb database where stories are kept
        client = MongoClient(host="mongodb://emerg55:emerg55@ds113703.mlab.com:13703/dictstories")


        # initiate list for answered words
        self.answered = []

        # choose a story at random from database
        #sess1 = random.choice(list(client["dictstories"].sessions.find()))
        #sess= sess["text"]
        #self.token_words = tokenize.word_tokenize(sess["text"])

        # choose a story at random from database
        sess = "Je ne peux pas faire beaucoup de phrases sans accents ni apostrophes le matin de bonne heure. Je pourrai en faire davantage plus tard si cela fera ton affaire."
        self.token_words = tokenize.word_tokenize(sess)

        # set up List, which will hold a _______ for each word and the punctuation
        List = []

        # iterate through words in self.token_words. If it's a word, add a ____ to list, if not, keep (e.g. punctuation)
        for w in self.token_words:
            if re.match("^\w+$", w):
                a=len(w)
                myblank = '_'*a

                List.append(myblank)
            else:
                List.append(w)

        # set up a hidden version of utterance - this outputs alternate text to speech bubble while tts speaks sys_utter
        self.hidden = "Right. Now, type one word you remember from the passage."
        self.original = sess

        sess2 = "*fr-FR*Je ne peux pas faire beaucoup de phrases sans accents ni apostrophes le matin de bonne heure.*fr-FR*Je pourrai en faire davantage plus tard si cela fera ton affaire."



        self.sys_utter = intro + "^w^"+ sess2 + "^w^*en-GB*Right.*en-GB*Now, type one word you remember from the passage."
        #self.sys_utter = intro + sess["text"] + " Right. Now, type one word from the story."
        self.extraDiv1 = "  ".join(List)


    def forward(self, text):
        # moves game on after intro
        # check user has only typed one word for guess, reprompt if not, else send to check answer
        if len(text.split(" ")) > 1:
            self.set_utter("Please type one only word.")
        else:
            self.check_answer(text)
        return

    def set_utter(self, text):
        # set system utterance
        self.sys_utter = text

    def check_answer(self, word):
        # generate list for blanks and answered words display
        List = []
        is_answer = False
        is_end = True
        self.set_utter(random.choice(["*en-GB*Sorry, try again. ", "*en-GB*Not there, go again."]))
        for w in self.token_words:
            if re.match("^\w+$", w) and not w.lower() == word.lower() and not w.lower() in self.answered:
                b=len(w)
                myblank2='_'*b
                List.append(myblank2)
                is_end = False
            elif w.lower() == word.lower():
                is_answer = True
                self.set_utter(random.choice(["*en-GB*Good! ", "*en-GB*Great! ", "*en-GB*Correct. ", "*en-GB*Nice one! "]))
                List.append(w)
            else:
                List.append(w)
        # set hidden display to new grid
        self.hidden = self.get_utt()[7:]
        self.answered.append(word.lower())
        self.extraDiv1 = "  ".join(List)
        # ask kyusong what this does
        if is_end:
            self.set_utter("*en-GB*Excellent.*en-GB*You did it! ")

            #self.__init__()
        return is_answer

    def get_utt(self):
        return self.sys_utter

    def get_hint(self):
        return

    def get_sys(self):
        return

    def get_display(self):
        return

    def say_goodbye(self):
        response = {"sessionID": sessionID, "sys": agent.sys_utter, "version": "1.0-xxx", "extraDiv1": agent.extraDiv1,
                    "timeStamp": "yyyy-MM-dd'T'HH-mm-ss.SSS", "display": agent.hidden,
                    "terminal": False}
        return response


class Game(object):
    def __init__(self):
        self.agent_pool = RedisAPI()
        self.edu = Edu()

    def start(self, sessionID):

        self.edu = Edu()
        self.agent_pool.refresh(sessionID)
        self.agent_pool.set(sessionID, self.edu)
        response = {"sessionID": sessionID, "sys": self.edu.sys_utter, "version": "1.0", "extraDiv1": self.edu.extraDiv1,
                    "timeStamp": "yyyy-MM-dd'T'HH-mm-ss.SSS", "terminal": False, "display": self.edu.hidden
                    }
        return response

    def response(self, sessionID, text):
        agent = self.agent_pool.get(sessionID)
        agent.forward(text)
        self.agent_pool.set(sessionID, agent)
        response = {"sessionID": sessionID, "sys": agent.sys_utter, "version": "1.0-xxx", "extraDiv1": agent.extraDiv1,
                    "timeStamp": "yyyy-MM-dd'T'HH-mm-ss.SSS", "display": agent.hidden,
                    "terminal": False}
        return response


if __name__ == "__main__":
    E = Edu()
