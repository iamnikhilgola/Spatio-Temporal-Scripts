#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 12:00:59 2020

@author: nikhil gola
"""
import datetime

from heremaps_data_downloader import *
import networkx as nx

ROADID_PATH= './data_cache/heremaps_road_id.pkl'
HEREMAPS_GRAPHPATH='./data_cache/heremaps_graph.pkl'

class HereMaps:
    def  __init__(self,Edges,Graph,Nodes,Node_id):
        self.Edges = Edges
        self.Graph = Graph
        self.Nodes = Nodes
        self.Node_id = Node_id
        
def getCurrTime():
   return datetime.now().strftime('%H:%M:%S')

def load_here_maps_road():
    return load_pickle(ROADID_PATH)

def create_networkX_graph(d):
    Edges={}
    Node=set()
    Node_id = {}
    for key in d.keys():
        for ele in d[key]:
            ele=ele.strip()
            splitted = ele.split(' ')
            #print(splitted)
            for i in range(len(splitted)-1):
                p = splitted[i].split(',')
                n1 = (p[1],p[0])
                p = splitted[i+1].split(',')
                n2 = (p[1],p[0])
                
                Node.add(n1)
                Node.add(n2)
                if Node_id.get(n1)==None:
                    Node_id[n1]=[]
                if Node_id.get(n2)==None:
                    Node_id[n2]=[]
                Node_id[n1].append(key)
                Node_id[n2].append(key)
                e = (n1,n2)
                #print(e)
                if Edges.get(e)==None:
                    Edges[e]=key
    G=nx.Graph()
    for e in Edges.keys():
        G.add_edge(*e)
    heremaps = HereMaps(Edges,G,Node,Node_id)
    return heremaps

def saveGraph(data,filename):
    save_pickle(data,filename)

def main():
      update_flag=False
      while True:
          tim = getCurrentTime()
          if (tim>10 and tim<17000) and update_flag==False:
              update_flag=True
              roadIDs = load_here_maps_road()
              heremaps=create_networkX_graph(roadIDs)
              saveGraph(heremaps,HEREMAPS_GRAPHPATH)
              print('Updated here Maps Graph..... ',getCurrTime())
              #break
              time.sleep(1000)
              
          else:
              print('Sleeping... ZZzzzzzz')
              if tim>17000:
                 
                  update_flag=False
              time.sleep(5000)
              
if __name__=='__main__':
    main()

        
    
        
        
        
        
        
    