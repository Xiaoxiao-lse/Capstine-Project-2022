#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 17:27:24 2022

@author: cengxiaoxiao
"""

import numpy as np
import json

def slide_means(timelines, specified_mood, reply_status):
    """
    slide window by 1 minute and compute the mean emotion score in that window
    :param timelines: user timelines
    """
    window_size = 60 # window_size is 60 seconds / 1 minute
    step = window_size # step is equal with the size of window
    start, end = -6 * 3600, 6 * 3600 - window_size + 1 # the window slides from -6 hours to +6 hours

    # the results store in the intermediary folder
    intermediary_path = '../data/intermediary_data/new_data'
    foutpath = '%s/mean_mood=%d_reply_status=%s.txt' % (intermediary_path,
                                                             specified_mood,
                                                             str(reply_status),)
    count = []
    with open(foutpath, 'w') as fout:
        fout.write('start\tmean\n')
        # the window slides minute by minute
        for start_t in range(start, end, step):
            end_t = start_t + window_size
            scores = []
            for timeline in timelines:
                if timeline['mood'] == specified_mood:
                    for tweet in timeline['tweets']:
                        # if the tweet post in the 1 minute window, we collect it's valence
                        if start_t <= tweet['stamp'] - timeline['stamp'] < end_t:
                            scores.append(tweet['mood'])
            mean = np.mean(scores)
            fout.write('%d\t%f\n' % (start_t, mean))
    return(count)

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
        slide_means(timelines, moodmap[i],  j)
                
                