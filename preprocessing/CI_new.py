#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 18:37:46 2022

@author: cengxiaoxiao
"""

# coding: utf-8
"""
This script computes confidence interval in each window of vader timelines and null-model. 10 minute window moves from -6 hours to +6 hours.
This script has 2 parameters:
The first one is the specified mood. 1 for positive, -1 for negative
The second one is the gender. You can set it to "all", "male" or "female".
examples:
python CI.py 1 all && python CI.py 1 male && python CI.py 1 female
python CI.py -1 all && python CI.py -1 male && python CI.py -1 female
"""

import random
import sys
import numpy as np
import util
import json

def get_CI(scores):
    """
    CI is short for confidence interval
    :param scores:
    :return: the resampling means
    """
    sample_size = int(len(scores))
    sample_cnt = 10000
    mean_vals = []
    for i in range(sample_cnt):
        sample_list = np.random.choice(scores, sample_size, replace=True)
        mean = np.mean(sample_list)
        mean_vals.append(mean)
    mean_vals.sort()
    return mean_vals

def get_null_CI(minutes_cnt_dict, minutes_tweets):
    """
    get null-model confidence intervals
    :param minutes_cnt_dict: the number of tweets that posted in specific week minute
    :param minutes_tweets: null-model tweets
    :return:
    """
    sample_cnt = 10000
    mean_vals = []
    for i in range(sample_cnt):
        sample_list = []
        for minute in minutes_cnt_dict:
            # get the tweets of each minute 
            minutes_scores = minutes_tweets[minute]
            #repeat for j times, j is the number of tweets for each week_minute
            for j in range(minutes_cnt_dict[minute]):
                sample_score = random.choice(minutes_scores)
                sample_list.append(sample_score)
        mean = np.mean(sample_list)
        mean_vals.append(mean)
    mean_vals.sort()
    return mean_vals

def slide_CI(timelines, specified_mood, minutes_tweets,reply_status):
    """
    slide window by 10 minute and compute null-model confidence interval in that window
    :param timelines: user timelines
    """
    window_size = 600 # window_size is 600 seconds / 10 minutes
    step = window_size # step is equal with the size of window
    start, end = -6 * 3600, 6 * 3600 - window_size + 1 # the window slides from -6 hours to +6 hours

    # the results store in the intermediary folder
    intermediary_path = '../data/intermediary_data/new_data'
    mood_name_map = {1: 'pos', -1: 'neg'}
    foutpath = '%s/%s_reply_status=%s.txt' % (intermediary_path, mood_name_map[specified_mood],
                                               str(reply_status))
    

    with open(foutpath, 'w') as fout:
        fout.write('window\tvader_2.5p\tvader_50p\tvader_97.5p\tnull_2.5p\tnull_50p\tnull_97.5p\tlengths\n')
        for start_t in range(start, end, step):
            end_t = start_t + window_size # define the start and end of the window
            scores = []
            minutes_cnt_dict = {}
            for timeline in timelines:
                if timeline['mood'] == specified_mood:
                    for tweet in timeline['tweets']:
                        # if the tweet post in the window, then we collect it's valence
                        if start_t <= tweet['stamp'] - timeline['stamp'] < end_t:
                            scores.append(tweet['mood'])
                            # count the number of tweets in each week-minute.
                            # It is useful in null-model sampling
                            week_minute = tweet['week_minutes']
                            minutes_cnt_dict.setdefault(week_minute, 0)
                            minutes_cnt_dict[week_minute] += 1
            CI = get_CI(scores)
            null_CI = get_null_CI(minutes_cnt_dict, minutes_tweets)
            mid_window = start_t + window_size // 2 # write the middle of window in the result file
            vader_low, vader_median, vader_high = CI[int(0.025*len(CI))], \
                                                  CI[int(0.5*len(CI))], CI[int(0.975*len(CI))]
            null_low, null_median, null_high = null_CI[int(0.025*len(null_CI))], \
                                               null_CI[int(0.5*len(null_CI))], \
                                               null_CI[int(0.975*len(null_CI))]
            fout.write("%d\t%f\t%f\t%f\t%f\t%f\t%f\t%d\n" % (mid_window,
                                                             vader_low, vader_median, vader_high,
                                                             null_low, null_median, null_high, len(scores)))
moodmap = {"pos":1,"neg":-1}
path = '../data/intermediary_data/new_data/'
for i in ["pos","neg"]:
    for j in ["before","after","none","all","before_after","before_noafter"]:
        filename = i+"_"+j+".txt"
        filepath = "%s%s" % (path,filename)
        print(filepath)
        with open(filepath) as f:
            for line in f:
                timelines = json.loads(line.strip())
        minutes_tweets = {}
        for timeline in timelines:
            seed_stamp = timeline['stamp']
            for tweet in timeline['tweets']:
                minutes = tweet['week_minutes']
                minutes_tweets.setdefault(minutes, [])
                minutes_tweets[minutes].append(tweet['mood'])
        slide_CI(timelines,moodmap[i],minutes_tweets,j)        
            
    
