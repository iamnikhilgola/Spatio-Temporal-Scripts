#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 13:13:36 2020

@author: iiitd
"""

from main import * 
import numpy as np

from os import listdir
from os.path import isfile, join

def create_avg_speed_vector(bus_vectors,slots): #required : complete vector 
    bus_avg_vec = {}
    bus_vectors=calculate_avg_road(bus_vectors)
    for key in bus_vectors.keys():
        if bus_avg_vec.get(key)==None:
            bus_avg_vec[key]=get_complete_dict(bus_vectors[key],slots)
    return bus_avg_vec

def complete_value_1D(key1,key2,value1,value2):
    temp_dict={}
    start_value = value1
    interpolateValue = (value2-value1)/(key2-key1)
    for i in range(key1+1,key2):
            temp_dict[i]= start_value+interpolateValue
            start_value+=interpolateValue
    return temp_dict

def get_complete_dict(bus_vector,last_index):
    #required average calculated vector
    avg_vector={}
    
    for i in range(last_index):
        if bus_vector.get(i)==None:
            if i==0:
                avg_vector[i]= 25.0#get_complete_avg(bus_vector)[1]
            else:
                key1 = i-1
                #print(avg_vector,' ',key1)
                key2 = get_next_key(key1,last_index,bus_vector)
                if key2==-1:
                    bus_vector[last_index-1]=[25.0,25.0,1.0] #get_complete_avg(bus_vector)[1]
                key2 = get_next_key(key1,last_index,bus_vector)
                value1 = avg_vector[key1]
                #print(bus_vector[key2])
                value2 = bus_vector[key2][1]
                di = complete_value_1D(key1,key2,value1,value2)
                for ke in di.keys():
                    avg_vector[ke]=di[ke]
        else:
            #print(bus_vector[i])
            avg_vector[i]=bus_vector[i][1]
    return avg_vector
          


def get_first_nz():
    pass
def get_next_key(start,last_index,bus_vec):
    for i in range(start+1,last_index):
        if bus_vec.get(i)==None:
            pass
        else:
            if bus_vec[i][1]==0:
                pass
            else:
                return i
    return -1
def get_confidence_of_speed(vector):
    countnz=0
    for i in range(len(vector)):
        if vector[i]>4:
            countnz+=1
    return countnz/len(vector)

def get_avg(vector):
    return np.mean(np.array(vector))

def get_nonZero_avg(vector):
    countnz = 0
    su=0.0
    for i in range(len(vector)):        
	    if vector[i]>3.0 and vector[i]<90.0:
                countnz+=1
                su+=vector[i]
                #su = np.sum(np.array(vector))
    if countnz==0:
        return 0.0
    avg = su/countnz
    
    return avg

def calculate_avg_road(bus_vector):
    road_avg={}
    for road in bus_vector.keys():
        if road_avg.get(road)==None:
            road_avg[road]={}
        for timeslot in bus_vector[road].keys():
            #print(timeslot)
            if road_avg[road].get(timeslot)==None:
                    road_avg[road][timeslot]={}
                    road_avg[road][timeslot]=[get_avg(bus_vector[road][timeslot]),get_nonZero_avg(bus_vector[road][timeslot]),get_confidence_of_speed(bus_vector[road][timeslot])]
    return road_avg
def get_complete_avg(bus_vect):
    bus_avg = []
    for i in bus_vect.keys():
        bus_avg.append(np.array(bus_vect[i]))
    av = bus_avg
    av=np.array(av)
    print(av)
    avg = np.mean(av,axis=0)
    #print(list(avg))
    return list(avg)
def getAllfiles(path):
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    return onlyfiles
def main():
    allfiles = getAllfiles('./bus_vectors/')
    for fi in allfiles:
            
        file ='./bus_vectors/'+fi
        f = file.split('.')
        f = f[1].split('/')[2]
        outfile='./feature_vectors/avg_vector_'+f+'.pkl'
        vector =load_pickle(file)
        feature = create_avg_speed_vector(vector,int((60/15)*24))
        save_pickle(feature,outfile)


#main()
    
