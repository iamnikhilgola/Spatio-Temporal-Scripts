#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 21:37:19 2020

@author: nikhil
"""

import requests
import time
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import date
import pickle 

from datetime import datetime
import os.path


def  file_exist(file):
    if os.path.isfile(file):
        return True
    else:
        return False
def getCSVFilename(suffix,path):
    
    name=suffix
    prefix='.csv'
    today=date.today()
    today=str(today)
    name=suffix+today+prefix
    return path+name
    
def getCurrentTime():    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    tim=0
    lstC = current_time.split(':')
    mul=3600
    
    for num in lstC:
        tim+=int(num)*mul
        mul/=60
    return tim
    
def save_pickle(data,filename):
    with open(filename,'wb') as dbfile:
        pickle.dump(data,dbfile)
    print('Successfully saved data to pickle file ',filename)
def load_pickle(filename):
    data=None
    with open(filename,'rb') as dbfile:
        data=pickle.load(dbfile)
    print('data loaded....')
    return data
def main():
    roadIDs = load_pickle('./data_cache/heremaps_road_id.pkl')
    csvfilename=None
    while True:
        tim = getCurrentTime()
        if tim>00 and tim<17000:
            if csvfilename!=None:
                
                df = pd.read_csv(csvfilename)
                df = df.drop_duplicates()
                save_csv(df,csvfilename)
                csvfilename=None
            print('sleeping.... Zzzzzz')
            time.sleep(1800)
        else:
            
            csvpath='./heremaps_data/'
            csvfilename=getCSVFilename('heremaps',csvpath)
            
            
            conges,roadid = readingHereCongestion(roadIDs)
            df= getCongestionDF(conges)
            if roadIDs!=roadid:
                roadIDs=roadid
                save_pickle(roadid,'./data_cache/heremaps_road_id.pkl')
            if file_exist(csvfilename):
                append_csv(df,csvfilename)
            else:
                save_csv(df,csvfilename)
            time.sleep(10)
            
    
def save_csv(df,name):
    df.to_csv(name, mode='w')    
    print("Succesfully saved data to CSV: ",datetime.now().strftime('%H:%M:%S'))
    
def append_csv(df,name):
    df.to_csv(name, mode='a', header=False)    
    print("Succesfully appended data to CSV: ",datetime.now().strftime('%H:%M:%S'))
    
def load_csv():
    pass

def getCongestionDF(congDict):
    i=0
    data_loc =[]
    for key in congDict.keys():
        for data in congDict[key]:
            data_loc.append(data)
        
    df = pd.DataFrame(data_loc,columns=['Road_id','Time','Confidence','Jam_factor','Avg_speed'])
    return df.drop_duplicates()

def readingHereCongestion(roadIDs):
    apiurl = "https://traffic.api.here.com/traffic/6.2/flow.xml?app_id=745ZKEzlXnLFfUKRcoNN&app_code=zaWAZogV6yQYQsApKAwizQ&bbox=28.4011,76.8631;28.8783,77.4481&responseattributes=sh,fc"
    #apiurl = "https://traffic.api.here.com/traffic/6.2/flow.xml?app_id=745ZKEzlXnLFfUKRcoNN&app_code=zaWAZogV6yQYQsApKAwizQ&bbox=28.589905217391305,77.22173043478261;28.587830434782607,77.23190434782609&responseattributes=sh,fc"
    congestionParameters={}
    try:
        print('waiting for data')
        response = requests.get(apiurl)
    except:
        print('Caught in exception....')
        time.sleep(10)
        
        return readingHereCongestion(roadIDs)
    
    content =response.content
    root=ET.fromstring(content)
    tag = "{http://traffic.nokia.com/trafficml-flow-3.2}"
    df = pd.DataFrame(columns=['Road_Code','Latitude','Longitude','Road_Name'])
    for rw in root.iter(tag+"RW"):
        tim  = rw.attrib['PBT']
        for fis in rw.getchildren():
            for fi in fis.getchildren():
                attriblen = len(fi)
                roadid = fi[0].attrib['PC']
                di=fi[0].attrib['QD']
                
                if roadIDs.get(roadid+di)==None:
                    roadIDs[roadid+di]=[]
                    for i in range(1,attriblen-1):
                        roadIDs[roadid+di].append(str(fi[i].text))
                cn = float(fi[attriblen-1].attrib['CN'])
                jf = float(fi[attriblen-1].attrib['JF'])
                avgSpeed  =float(fi[attriblen-1].attrib['SP'])
                if congestionParameters.get(roadid+di)==None:
                    congestionParameters[roadid+di]=[]
                congestionParameters[roadid+di].append([roadid+di,tim,cn,jf,avgSpeed])
    return congestionParameters,roadIDs         
                
if __name__=='__main__':
    main()                
            
           
