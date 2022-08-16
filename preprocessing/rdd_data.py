#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 19:09:43 2022

@author: cengxiaoxiao
"""

import sys
import numpy as np
import util
import matplotlib
from matplotlib import pyplot as plt
import pandas as pd


import glob
import numpy as np
import scipy as sp

import matplotlib
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
import pandas as pd

from scipy import stats
from scipy.optimize import curve_fit

import statsmodels.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from lmfit.models import *
from sklearn.mixture import GaussianMixture

from rdd import rdd

import json
import random


path = '../data/intermediary_data/new_data/'
overallpath = "%soverall_reply_dict.txt" % (path)
affectpath = "%saffect_reply_dict.txt" % (path)
user_info= pd.read_csv("../data/raw_dataset/user.csv")

window_size = 60 # window_size is 60 seconds / 1 minute
step = window_size # step is equal with the size of window
start, end = -6 * 3600, 6 * 3600 - window_size + 1 # the window slides from -6 hours to +6 hours
rdd_t = {"pos":[],"neg":[]}
threshold = {"pos":2340,"neg":300}
with open(affectpath) as f:
    for line in f:
        affect = json.loads(line.strip())
for j in ["pos","neg"]:
    current_t = affect[j]["replied"]
    
   
    tweets = []
    index = 0

    for timeline in  current_t["all"]["timeline"]:
        uid = timeline["uid"]
        reply_time_ls = []
        affect_reply_mood = []
        for reply in timeline["reply_ls"]:
            if reply["affect"] == True:
                
                reply_time = reply["stamp"] - timeline['stamp']
                reply_time_ls.append(reply_time)
                affect_reply_mood.append(reply["mood"])        
        reply_time = min(reply_time_ls)
        mood = [affect_reply_mood[i[0]] for i in enumerate(reply_time_ls) if i[1] == reply_time]
        mood = sum(mood) / len(mood)
        if (reply_time >= 0) and (reply_time <= threshold[j]):
            flag = False
            for start_t in range(start, end, step):
                end_t = start_t + window_size
            
                for tweet in timeline['tweets']:
                    # if the tweet post in the 1 minute window, we collect it's valence
                    if start_t <= tweet['stamp'] - timeline['stamp'] < end_t:
                        tweets.append([tweet['stamp'] - timeline['stamp'],tweet["mood"], index,mood,uid,reply_time])
                        flag = True
            if flag :
                index+=1
        else:
            continue
            
    
    tweets_df = pd.DataFrame(tweets,columns = ["start_t","mean","id","mood","uid","reply_time"])
    
    result = pd.merge(tweets_df,
                     user_info[['uid', 'followers_count']],
                     on='uid', 
                 how='left')
    filename = "../data/rdd/new/rdd_%s.csv" % j
    result.to_csv(filename)
                    
rdd_pos = pd.read_csv("../data/rdd/new/rdd_pos.csv")  
n_pos = len(rdd_pos["id"].unique() )  

rdd_neg = pd.read_csv("../data/rdd/new/rdd_neg.csv")  
n_neg = len(rdd_neg["id"].unique())  

random.seed(10)
rdd_pos_unreply = []
rdd_neg_unreply = []
rdd_unreply ={"pos":rdd_pos_unreply,"neg":rdd_neg_unreply}

for i in ["neg","pos"]:
    for timeline in affect[i]["unreplied"]["timeline"]:
        reply_time_ls = []
        if timeline["reply_ls"] == []:
            continue
        else:
            for reply in timeline["reply_ls"]:
                reply_time = reply["stamp"] - timeline['stamp']
                if reply_time >= 0:
                    reply_time_ls.append(reply_time)
            # no replies after t0
            if reply_time_ls == []:
                continue
            # the first reply after t0 should within 300s
            else:
                reply_time = min(reply_time_ls)
            
            if reply_time <= threshold[i]:
                rdd_unreply[i].append(timeline)




for i in ["neg","pos"]:
    
    tweets =[]  
    index = 0      
    for timeline in  rdd_unreply[i]:
        
        uid = timeline["uid"]
        reply_time_ls = []
        reply_mood_dict = {}
        # gather replies within 300s 
        for reply in timeline["reply_ls"]:
            
            reply_time = reply["stamp"] - timeline['stamp']
            
            if reply_time >=0 and reply_time <= threshold[i]:
                reply_mood_dict.setdefault(reply_time,[])
                reply_mood_dict[reply_time].append(reply["mood"])
                reply_time_ls.append(reply_time)
                
        # calculate reply time and reply mood        
        reply_time = min(reply_time_ls)
        reply_mood_ls = reply_mood_dict[reply_time]
        reply_mood = sum(reply_mood_ls) / len(reply_mood_ls)
        # append tweets within 12 hours
        flag = False
        for start_t in range(start, end, step):
            end_t = start_t + window_size
            for tweet in timeline['tweets']:
                # if the tweet post in the 1 minute window, we collect it's valence
                if start_t <= tweet['stamp'] - timeline['stamp'] < end_t:
                    tweets.append([tweet['stamp'] - timeline['stamp'],tweet["mood"], index,reply_mood,uid,reply_time])
                    flag = True
        
        if flag:
            index+=1
                

    tweets_df = pd.DataFrame(tweets,columns = ["start_t","mean","id","mood","uid","reply_time"])
    
    
    result = pd.merge(tweets_df,
                     user_info[['uid', 'followers_count']],
                     on='uid', 
                 how='left')
    filename = "../data/rdd/new/rdd_%s_unreply.csv" % i
    result.to_csv(filename)
rdd_pos_unreply_df = pd.read_csv("../data/rdd/new/rdd_pos_unreply.csv") 
rdd_neg_unreply_df = pd.read_csv("../data/rdd/new/rdd_neg_unreply.csv")


with open(overallpath) as f:
    for line in f:
        overall = json.loads(line.strip())
        
random.seed(10)
        
overall_pos_unreply = random.sample(
    [i for i in affect["pos"]["unreplied"]["timeline"] if i["reply_ls"] == []]\
                                     ,round(n_pos*2))
                                     
overall_neg_unreply = random.sample(
    [i for i in affect["neg"]["unreplied"]["timeline"] if i["reply_ls"] == []] , round(n_neg*1.5))


overall_unreply = {"pos":overall_pos_unreply , "neg":overall_neg_unreply}


for i in ["neg","pos"]:
    index = 0
    tweets =[]
    
    for timeline in  overall_unreply[i]:
        uid = timeline["uid"]
        reply_time = 0
        flag = False
        for start_t in range(start, end, step):
            end_t = start_t + window_size
            for tweet in timeline['tweets']:
                # if the tweet post in the 1 minute window, we collect it's valence
                if start_t <= tweet['stamp'] - timeline['stamp'] < end_t:
                
                    tweets.append([tweet['stamp'] - timeline['stamp'],tweet["mood"], index,uid,reply_time])
                    flag = True
        if flag:
            index+=1    
            
    tweets_df = pd.DataFrame(tweets,columns = ["start_t","mean","id","uid","reply_time"])
    
    result = pd.merge(tweets_df,
                     user_info[['uid', 'followers_count']],
                     on='uid', 
                 how='left')
    filename = "../data/rdd/new/rdd_%s_overall_unreply.csv" % i
    result.to_csv(filename)

overall_pos_unreply_df = pd.read_csv("../data/rdd/new/rdd_pos_overall_unreply.csv") 
overall_neg_unreply_df = pd.read_csv("../data/rdd/new/rdd_neg_overall_unreply.csv")


for j in ["pos","neg"]:
    
    tweets = []
    
    index = 0
    
    for q in ["replied","unreplied"]:
        current_t = overall[j][q]
    
        for timeline in  current_t["timeline"]:
            uid = timeline["uid"]
            for start_t in range(start, end, step):
                end_t = start_t + window_size
            
                for tweet in timeline['tweets']:
                    # if the tweet post in the 1 minute window, we collect it's valence
                    if start_t <= tweet['stamp'] - timeline['stamp'] < end_t:
                        tweets.append([tweet['stamp'] - timeline['stamp'],tweet["mood"], index,uid])
            index += 1
     
            
    
    tweets_df = pd.DataFrame(tweets,columns = ["start_t","mean","id","uid"])
    
    result = pd.merge(tweets_df,
                     user_info[['uid', 'followers_count']],
                     on='uid', 
                 how='left')
    filename = "../data/rdd/new/rdd_all_%s.csv" % j
    result.to_csv(filename)  
    
overall_pos_df = pd.read_csv("../data/rdd/new/rdd_all_pos.csv") 
overall_neg_df = pd.read_csv("../data/rdd/new/rdd_all_neg.csv")
