#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 09:52:09 2020

@author: iiitd
"""

import networkx as nx

current_MAX=0


def get_nodes_from_adjacent_edges(G,node):
    edges=  list(G.edges(node))
    nodes = set()
    for edge in edges:
        nodes.add(edge[1])
    return list(nodes)
def get_nodes_dict(G):
    nodes_Dict={}
    nodes = list(G.nodes())
    for node in nodes:
        nodes_Dict[node]=[False,[]]
    return nodes_Dict
def get_edges_dict(G):
    edges_Dict={} 
    edges = list(G.edges())
    for edge in edges:
        edges_Dict[edge]=[]
    return edges_Dict
def get_edge(node1,node2,EDGE_LIST):
    if EDGE_LIST.get((node1,node2))!=None:
        return (node1,node2)
    elif EDGE_LIST.get((node2,node1))!=None:
        return (node2,node1)
def get_edge_nodes(edge):
    node1 = edge[0]
    node2 = edge[1]
    return node1,node2
def isJunction_node(G,node):
    edges=list(G.edges(node))
    if len(edges)>2:
        return True
    else:
        return False
def DFS_UTIL(G,node,NODE_LIST,EDGE_LIST):
         Stack=[]
         Stack.append(node)
         
         while len(Stack)>0:
            node=Stack[-1]
            Stack.pop()
            global current_MAX
            NODE_LIST[node][0]=True
            debug=False
            #print(node)
            nodes=get_nodes_from_adjacent_edges(G,node)
            if isJunction_node(G,node)==True:

                for nn in nodes:
                    if  len(NODE_LIST[nn][1])>0 and isJunction_node(G,nn)==False:
                        edge = get_edge(node,nn,EDGE_LIST)
                        if len(EDGE_LIST[edge])==0:
                            NODE_LIST[node][1].append(NODE_LIST[nn][1][0])

                            EDGE_LIST[edge]=[NODE_LIST[nn][1][0]]
                            if debug:
                                print(1)
                                print("Edge :",edge,"  Node:",nn,"  Value:",NODE_LIST[nn][1][0])
                                print(NODE_LIST[node])

                    elif len(NODE_LIST[nn][1])>0 and isJunction_node(G,nn)==True:
                        edge = get_edge(node,nn,EDGE_LIST)
                        if len(EDGE_LIST[edge])==0:    
                            current_MAX+=1
                            NODE_LIST[node][1].append(current_MAX)
                            NODE_LIST[nn][1].append(current_MAX)

                            EDGE_LIST[edge]=[current_MAX]
                            if debug:
                                print(2)
                                print("Edge :",edge,"  Node:",nn,"  Value:",NODE_LIST[nn][1][0])
                                print(NODE_LIST[node])

                        
                    else:
                        current_MAX+=1
                        NODE_LIST[node][1].append(current_MAX)
                        NODE_LIST[nn][1].append(current_MAX)
                        edge = get_edge(node,nn,EDGE_LIST)
                        EDGE_LIST[edge]=[current_MAX]
                        if debug:
                            print(3)
                            print("Edge :",edge,"  Node:",nn,"  Value:",NODE_LIST[nn][1][0])
                            print(NODE_LIST[node])
                 
            else:
                if  len(NODE_LIST[node][1])==0:
                    if len(nodes)==2:
                        if len(NODE_LIST[nodes[0]][1])>0 or len(NODE_LIST[nodes[1]][1])>0:
                            rid=-1
                            if len(NODE_LIST[nodes[0]][1])>0:
                                rid = NODE_LIST[nodes[0]][1][0]
                                edge = get_edge(nodes[0],node,EDGE_LIST)
                                #print(edge)
                                EDGE_LIST[edge]=[rid]
                                
                            else:
                                rid = NODE_LIST[nodes[1]][1][0]
                                #print(edge)
                                edge = get_edge(nodes[1],node,EDGE_LIST)
                                EDGE_LIST[edge]=[rid]
                        else:
                            rid = current_MAX
                        NODE_LIST[node][1].append(rid)
                    elif len(nodes)==1:
                        rid=-1
                        #print(node)
                        if len(NODE_LIST[nodes[0]][1])>0:
                            rid = NODE_LIST[nodes[0]][1][0]
                            edge = get_edge(nodes[0],node,EDGE_LIST)
                           # print(nodes[0],node)
                            EDGE_LIST[edge]=[rid]

                        else:
                            rid =current_MAX
                            edge = get_edge(nodes[0],node,EDGE_LIST)
                            EDGE_LIST[edge]=[rid]
                        NODE_LIST[node][1].append(rid)
                    else:
                        print('Not Found !!!!')
                elif len(NODE_LIST[node][1])>0:
                    pass
            for n in nodes:
                    if NODE_LIST[n][0]==False:
                        Stack.append(n)

def DFS(G,NODE_LIST,EDGE_LIST):
    global current_MAX
    
    for node in NODE_LIST.keys():
        if NODE_LIST[node][0]==False:
            DFS_UTIL(G,node,NODE_LIST,EDGE_LIST)
    for edge in EDGE_LIST.keys():
        if len(EDGE_LIST[edge])==0:
             n1,n2 = get_edge_nodes(edge)
            # print(isJunction_node(G,n1),isJunction_node(G,n2))
             if isJunction_node(G,n1)==True and isJunction_node(G,n2)==False:
                 rid = NODE_LIST[n1][1][0]
                 EDGE_LIST[edge]=[rid]
             elif isJunction_node(G,n2)==True and isJunction_node(G,n1)==False:
                 rid = NODE_LIST[n2][1][0]
                 EDGE_LIST[edge]=[rid]
             else:
                 rid = NODE_LIST[n1][1][0]
                 EDGE_LIST[edge]=[rid]
def get_annotated_Graph(G):
    global current_MAX
    current_MAX=0
    NODE_LIST=get_nodes_dict(G)
    EDGE_LIST=get_edges_dict(G)
    
    DFS(G,NODE_LIST,EDGE_LIST)
    #print(NODE_LIST)
    return EDGE_LIST,NODE_LIST