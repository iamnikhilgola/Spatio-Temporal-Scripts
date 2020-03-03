# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 20:53:07 2020

@author: nikhi
"""
import pandas as pd
import pickle
from RoadMapper import BoundingBox,Grid,Point,RoadReader,Stop
from Create_heremaps_graph import * 

ROAD_INFO_PATH='updatedRoadInfo.csv'

ROADNODE_PATH= './data_cache/Node_road_id.pkl'

def savepickle(filename,data):
    print('saving.. :',filename)
    with open(filename,'wb') as dbfile:
        pickle.dump(data,dbfile)
    print('successfully saved: ',filename)
def load_bus_dict(df,grid):
    print('loading bus info....')
    df  = df.drop_duplicates()
    df=df.sort_values(by=["vehicle_id",'timestamp'])
    bus_dict={}
    i=0
    for _,row in df.iterrows():
        if i%100000==0:
            print(i,"/",len(df))
        i+=1
        key = row['vehicle_id']+str(row['trip_id'])+str(row['route_id'])
        if bus_dict.get(key)==None:
            bus_dict[key]={}
            bus_dict[key][0]=[]
        
        point = Point(row['longitude'],row['latitude'])
        node = grid.map_to_node(point)
        if node==None:
            pass
        else:
            k = list(bus_dict[key].keys())[-1]
            if len(bus_dict[key][k])==0:
                bus_dict[key][k].append([node,0,row['timestamp'],point,0.0])
            else:
                if row['timestamp']-bus_dict[key][k][-1][2]>3600:
                    k=k+1
                    bus_dict[key][k]=[]
                    bus_dict[key][k].append([node,0,row['timestamp'],point,0.0])
                else:
                    dist=0
                    #dist = grid.road.getDistance(bus_dict[key][k][-1][0],node)
                    n = bus_dict[key][k][-1][3]
                    #print(n[1].x)
                    n2 = (point.x,point.y)
                    n1=(n.x,n.y)
                    #print(i," n1:",n1,"  n2:",n2)

                    dist = getNodeDistance(grid,n1,n2)

                    timdiff = row['timestamp']-bus_dict[key][k][-1][2]    
                    speed =0.0
                    try:
                        speed = (dist/timdiff) *(18/5)
                    except:
                        speed = 0.0
                    if timdiff!=0:
                        bus_dict[key][k].append([node,dist,row['timestamp'],point,speed])
    return bus_dict
                
def load_road_id(grid):
    road_details = {}
    road = pd.read_csv(ROAD_INFO_PATH)
    for _,row in road.iterrows():
        point = Point(row['Longitude'],row['Latitude'])
        _,_,cell_id=grid.hash(point)
        if road_details.get(cell_id)==None:
            road_details[cell_id]=[]
        road_details[cell_id].append([(row['Longitude'],row['Latitude']),row['Road_id']])
    return road_details
def load_here_maps_id(grid):
    here_maps_road={}
    d = load_here_maps_road()
    for key in d.keys():
        for ele in d[key]:
            ele=ele.strip()
            splitted = ele.split(' ')
            #print(splitted)
            for i in range(len(splitted)):
                p = splitted[i].split(',')
                node=[float(p[1]),float(p[0])]
                _,_,cell_id = grid.hash(Point(node[0],node[1]))
                if here_maps_road.get(cell_id)==None:
                    here_maps_road[cell_id]=[]
                here_maps_road[cell_id].append([node,key])
    return here_maps_road           
    
def map_road_to_node(nodes,road_dict,here,grid):
    node_road_id = {}
    for node in nodes:
        if node_road_id.get(node)==None:
            node_road_id[node]=[]
        #print(node)
        _,_,cell_id = grid.hash(Point(node[0],node[1]))
        mindis = 99999999999
        road_id=None
        if road_dict.get(cell_id)!=None:
            for rd in road_dict[cell_id]:
                #print(rd)
                dis=getNodeDistance(grid,node,(float(rd[0][0]),float(rd[0][1])))
                if dis<mindis:
                    dis=mindis
                    road_id = int(rd[1])
        else:
            road_id='None'
        mindis = 9999999999
        h_id=None
        if here.get(cell_id)==None:
            h_id= "None"
        else:
            for hd in here[cell_id]:
                dis=getNodeDistance(grid,node,hd[0])
                if dis<mindis:
                    dis=mindis
                    h_id = hd[1]
        node_road_id[node].append([road_id,h_id])
    return node_road_id
                
            
def getNodeDistance(grid,node1,node2):
     point1 = Point(node1[0],node1[1])
     point2 = Point(node2[0],node2[1])
     return grid.road.getDistance(point1,point2)
def update_road_node(grid):
    print('loading... road_id')

    road_details= load_road_id(grid)
    
    print('success: loaded... roadid')
    here = load_here_maps_id(grid)
    
    print('success: loaded... heremapid')
    
    roadids_node = map_road_to_node(grid.road.nodes,road_details,here,grid)
    
    
    print('saving')
    save_pickle(roadids_node,ROADNODE_PATH)
    print("Thank You")


def load_Grid():
    size = 230
    grid=Grid(BoundingBox(28.4011,76.8631,28.8783,77.4481),size)
    grid.loadNodes()
    grid.defineGrid()
    #print(grid.Nodes)
    print('loading... stops')
    grid.load_stops('GTFS/stops.txt')
    print('success: loaded... stops')
    return grid

            
            
            
            
