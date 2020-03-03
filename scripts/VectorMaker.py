#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 21:43:13 2020

@author: iiitd
"""
import pandas as pd
import pickle 
from RoadMapper import *
import datetime
import math
from main import savepickle, getNodeDistance, load_bus_dict,load_Grid
from heremaps_data_downloader import *
from feature_extractor import create_avg_speed_vector
from Create_heremaps_graph import getCurrTime


from os import listdir
from os.path import isfile, join
from dateutil import tz

PATH_BUS_DICT='./bus_dict/'
PATH_BUS_VECTORS='./bus_vectors/'
PATH_TO_DONE_CACHE='./data_cache/done.pkl'
PATH_TO_LIVE='./live_data/'

def getTimeSlot(ts,minpslot):
        
    mtim = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    tim = datetime.utcfromtimestamp(ts).strptime(mtim,'%Y-%m-%d %H:%M:%S')
    
    #print(tim)
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    
    tim =tim.replace(tzinfo=from_zone)
    tim = tim.astimezone(to_zone)
    tim=tim.strftime('%Y-%m-%d %H:%M:%S')
    tim = tim.split(" ")[1]
    s= tim.split(':')
    hr = int(s[0])
    mn = int(s[1])
    sec = int(s[2])
    divs = math.floor(mn/minpslot)
    timslot = hr*(60/minpslot)+divs
    return int(timslot)
    
def create_vector(df,grid,mnslot):
    print('Creating vectors...')
    bus_dict = load_bus_dict(df,grid)
    print('Bus data loaded successfully...')
    rv,bd=create_day_vector(grid,bus_dict,mnslot)
    return rv,bd   	
def create_day_vector(grid,bus_dict,mnslot):
    road_vector={}
    for key in bus_dict.keys():
        for k in bus_dict[key].keys():
            for ele in bus_dict[key][k]:
                road_id = grid.map_to_road(ele[0],here=True) # here maps road id  if here ==True else normal road id
                if road_vector.get(road_id)==None:
                    road_vector[road_id]={}
                timeslot = getTimeSlot(int(ele[2]),mnslot)
    
                if road_vector[road_id].get(timeslot)==None:
                    road_vector[road_id][timeslot]=[]
                road_vector[road_id][timeslot].append(ele[4])
    print('done creating vectors...')
    return road_vector,bus_dict

def getAllfiles(path):
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    return onlyfiles
	
def load_all_vectors(grid,mnslot):
    done = []
    if file_exist(PATH_TO_DONE_CACHE):
        done = load_pickle(PATH_TO_DONE_CACHE)
    files = getAllfiles(PATH_TO_LIVE)
    for file in files:
        if file not in done:
            filenamedict = PATH_BUS_DICT+file.split('.')[0]+'_bus_dict.pkl'
            filenamevector =PATH_BUS_VECTORS+file.split('.')[0]+'_bus_vectors.pkl'
            filename = PATH_TO_LIVE+file
            #print(filename,' ',filenamedict,' ',filenamevector)
            print('Reading CSV :',filename)
            df = pd.read_csv(filename)
            print('success:',getCurrTime())
            rv,bd = create_vector(df,grid,mnslot)
            print("Vectors created successfully: ",getCurrTime())
            save_pickle(rv,filenamevector)
            save_pickle(bd,filenamedict)
            done.append(file)
            save_pickle(done,PATH_TO_DONE_CACHE)
            
        else: 
            pass
def save_data(rv,bd,filenamevector,filenamedict):
    if rv!=None:
        save_pickle(rv,filenamevector)
        print('Saved: ',filenamevector)
    if bd!=None:
        save_pickle(bd,filenamedict)
        print('Saved: ',filenamedict)
def updateVectors(grid,filename,outputfile):
    busdict = load_pickle(filename)
    rv,bd=create_day_vector(grid,busdict,15)
    save_data(rv,bd,outputfile,filename)
    print('updated successfully')
def save_file(filename,data):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as dbfile:
        pickle.dump(data,dbfile)
    print("File Saved Successfully: ",filename)
def second_main():
    grid = load_Grid()
    allfiles = getAllfiles('./bus_dict/')
    ts = [5,10,15,20,30,60]
    remark='here/'
    tss='/'
    for fi in allfiles:
        print('Loading file: ',fi)
        for timeslot in ts:
            print('loading for timeslot ',str(timeslot))
            file ='./bus_dict/'+fi
            f = file.split('.')
            f = f[1].split('/')[2]
            bus_dict = load_pickle(file)
            rv,bd=create_day_vector(grid,bus_dict,timeslot)
            outfile='./bus_vectors/'+remark+str(timeslot)+tss+f+'bus_vector.pkl'
            outfilefeature = './bus_feature/'+remark+str(timeslot)+tss+f+'bus_feature.pkl'
            feature=create_avg_speed_vector(rv,int((60/timeslot)*24))
            save_file(outfile,rv)
            save_file(outfilefeature,feature)
            
   	
def main():
    grid = load_Grid()
   # updateVectors(grid,'bus_dict/30_01_bus_dict.pkl','./bus_vectors/30_01_bus_vectors.pkl')
   # updateVectors(grid,'bus_dict/29_01_bus_dict.pkl','./bus_vectors/29_01_bus_vectors.pkl')
    #updateVectors(grid,'bus_dict/31_01_bus_dict.pkl','./bus_vectors/31_01_bus_vectors.pkl')
   
    load_all_vectors(grid,15)
    
if __name__=='__main__':
    second_main()