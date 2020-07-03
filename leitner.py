import os
import json
import time
import argparse
import numpy as np
import pandas as pd
import pickle as pkl
from tqdm import tqdm
from datetime import datetime


class LeitnerBox():
    
    @classmethod
    def empty(C):
        pairs = {}
        return(C(pairs))
    
    @staticmethod
    def load(fn):
        with open(fn, "rb") as ih:
            return(pkl.load(ih))
        
    def save(self, fn):
        with open(fn, "wb") as oh:
            pkl.dump(self, oh)
    
    @staticmethod
    def schedule(level):
        return(2**level)
    
    def __init__(self, pairs):
        self.pairs = pairs
        
    @staticmethod
    def get_questions(file_contents):
        cs = [a.strip().lower() for a in file_contents.split("\n")]
        try:
            if "## questions" in cs:
                qna = cs.index("## questions")
                cs = cs[qna+1:]
                ai = cs.index("## answers")
                q_s = list(filter(lambda x: len(x) > 0, cs[:ai]))
                a_s = list(filter(lambda x: len(x) > 0, cs[ai+1:]))
            else:
                return({})
        except Exception as e:
            return({})
        else:
            return({q:a for q,a in zip(q_s, a_s)})
                
    def index(self, files):
        for file in files:
            with open(file, "r") as ih:
                qa = LeitnerBox.get_questions(ih.read())
                qa = {a: (qa[a], 0, datetime.now()) for a in qa}
                intersecting_keys = set(self.pairs.keys()) & set(qa.keys())
                noint_qa = {}
                for a in qa:
                    if a not in intersecting_keys:
                        noint_qa[a] = qa[a]
                self.pairs.update(noint_qa)
                
    def study_one(self, question):
        _ = input(question+"\n")
        answer = self.pairs[question][0]
        print(answer+"\n")
        level = self.pairs[question][1]
        tm = datetime.now()
        while True:
            correct = input("Is the answer correct? (Y,n)\n").lower()
            if correct in ["y", "n"]:
                if correct == "y":
                    level += 1
                else:
                    level = 0
                print("Your current level is "+str(level))
                break
        return(answer, level, tm)
    
    def today(self):
        t = datetime.now()
        suitable = {}
        for question in self.pairs:
            answer, lv, qt = self.pairs[question]
            td = t-qt
            # print(td.seconds//3600, lv, times)
            if lv == 0:
                suitable[question] = (answer, lv, qt)
            else:
                # print(td.days % 2**lv, 2**lv, td.days+1, qt)
                if td.seconds//3600 > 10 and (td.days + 1) % 2**lv == 0:
             #       print(td.days % 2**lv)
                    suitable[question] = (answer, lv, qt)
        return(suitable)
    
    def study(self, catch_up=False):
        suitable = self.today()
        keys = np.random.permutation(list(suitable.keys()))
        if catch_up:
            keys = keys[0:25]
        print(str(len(keys))+" questions to study today.")
        for i,k in enumerate(keys):
            print("Question#"+str(i+1))
            self.pairs[k] = self.study_one(k)
