import csv
import math

import matplotlib.pyplot as plt
import networkx as nx
import mplleaflet



from RoadUtils import getDistanceFromline,saveRoad,loadRoad
from heremaps_data_downloader import load_pickle
from RoadDFS import get_annotated_Graph


path_to_road_data = './data/Roads.pkl'   
ROADNODE_PATH= './data_cache/Node_road_id.pkl'
     

class RoadReader:
    def __init__(self,file=None):
        self.file=file
        self.hasFile=False
        if file!=None:
            self.hasFile=True
        self.geopandasFile=None
        self.networkGraph=None
        self.EdgeDistance={}
    def readFile(self,file=None):
        if file==None and self.hasFile==True:
            self.geopandasFile = gp.read_file(self.file)
        elif file!=None:
            self.geopandasFile=gp.read_file(file)
        else:
            print("File not found!!")
    def loadGraph(self,file=None):
        print('Graph: loading....')
        if file==None and self.hasFile==True:
                file = self.file
        elif file==None:
            print('File required: Need a file to load')
        geoms =[shape(feature['geometry']) for feature in fiona.open(file)] 
        res = unary_union(geoms)
        G = nx.Graph()
        for line in res:
            for seg_start, seg_end in zip(list(line.coords),list(line.coords)[1:]):
                G.add_edge(seg_start, seg_end) 
        self.graph=G
        self.edges = list(G.edges())
        self.nodes = list(G.nodes())
        self.calculateEdgeDistance()
        print("Graph: Loaded with edges=",str(len(self.edges))," and vertices=",str(len(self.nodes)))
    def loadShortestPath(self,node1,node2):
        #print(node1)
        #print(node2)
        path = nx.shortest_path(self.graph,node1,node2)
        #path = nx.single_source_shortest_path(self.graph,node1,node2)
        return path
    def showPathGraph(self,path):
        x,y=[],[]
        for p in path:
            x.append(p[0])
            y.append(p[1])
        fig = plt.figure()
        plt.plot(x,y)
        mplleaflet.show(fig=fig)
    def calculateEdgeDistance(self):
        for e in self.edges:
            p1 = e[0]
            p2 = e[1]
            point1 = Point(p1[1],p1[0])
            point2 = Point(p2[1],p2[0])
            self.EdgeDistance[e]=self.getDistance(point1,point2)
    def getDistanceBetweenTwoNodes1(self,node1,node2):
        p =self.loadShortestPath(node1,node2)
        dis = self.getTotalDistance(p)
        return dis
    def getTotalDistance(self,path):
        totaldistance=0
        for i in range(len(path)-1):
            e1 = (path[i],path[i+1])
            e2 = (path[i+1],path[i])
            if self.EdgeDistance.get(e1)==None:
                e1 = e2
            totaldistance+=self.EdgeDistance[e1]
        return totaldistance            
    def getDistance(self,point1,point2):
        radius=6371000 #meters
        dlat = math.radians(point2.y-point1.y)
        dlong = math.radians(point2.x-point1.x)
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(point1.y)) * math.cos(math.radians(point2.y)) * math.sin(dlong/2) * math.sin(dlong/2)
        c = 2 * math.atan2(math.sqrt(a),math.sqrt(1-a))
        dist = float(radius * c)
        return dist# distance in meters        

class Stop:
    def __init__(self,stop_id,stop_detail,point):
        self.stop_id = stop_id
        self.stop_detail = stop_detail
        self.location = point
        self.nearest_node=None
        self.nearest_node_dist=None
    def define_nearest_node(self,node,dist):
        self.nearest_node=node
        self.nearest_node_dist = dist
    def display_info(self):
        print("stop_id:",self.stop_id,
              " stop_name:",self.stop_detail,
              " NearestNode:",self.nearest_node,
              " Distance from node:",self.nearest_node_dist)

#Latitude is the y-axis whereas the longitude is the x-axis

class BoundingBox:
    # This Bounding box is used to hold the four coordinates. 
    def __init__(self,min_y,min_x,max_y,max_x):
        self.min_x=min_x
        self.min_y=min_y
        self.max_x=max_x
        self.max_y=max_y
class Cell:
    def __init__(self):
        edges={}
        
class Point:
    def __init__(self,x,y):
        self.x=x
        self.y=y
class Grid:
    def __init__(self,box=None,split_size=0):
        self.min_lat=box.min_y
        self.min_long=box.min_x
        self.max_lat=box.max_y
        self.max_long=box.max_x
        self.split =split_size
        self.size= self.split**2
        self.Nodes = None
        roads=None
    def latitude_step_size(self):
        return (self.max_lat - self.min_lat)/self.split
    def longitude_step_size(self):
        return (self.max_long - self.min_long)/self.split
    def hash(self,point):
        latstep = self.latitude_step_size()
        longstep = self.longitude_step_size()
        latdiff = point.y-self.min_lat
        longdiff = point.x-self.min_long
        row = math.floor(latdiff/latstep)
        #print(row)
        col = math.floor(longdiff/longstep)
        cell_id = row * self.split + col
        return row,col,cell_id
    def get_cell_cordinates(self,cell_id):
        latStep = self.latitude_step_size()
        longStep= self.longitude_step_size()
        col = cell_id%self.split
        row = (cell_id-col)/self.split
        latitude1 = self.min_lat+ row *latStep
        longitude1= self.min_long + col * longStep
        return latitude1,longitude1
    def plot_cell(self,cell_id):
        latstep = self.latitude_step_size()
        longstep= self.longitude_step_size()
        lat,long = self.get_cell_cordinates(cell_id)
        x=[]
        y=[]
        x.append(lat)
        y.append(long)
        x.append(lat+latstep)
        y.append(long)
        x.append(lat+latstep)
        y.append(long+longstep)
        x.append(lat)
        y.append(long+longstep)
        x.append(lat)
        y.append(long)
        plt.plot(x,y)
    def validate_location(self,point):
        lat= point.y
        lon = point.x
        if (lat<self.min_lat or lat>self.max_lat) or (lon<self.min_long or lon>self.max_long):
            return False
        return True
    def defineGrid(self):
        x = self.road.getDistance(Point(self.min_long, self.min_lat),Point(self.min_long+self.longitude_step_size(), self.min_lat))
        y = self.road.getDistance(Point(self.min_long, self.min_lat),Point(self.min_long, self.min_lat+self.longitude_step_size()))
        print("================================================================================")
        print("Cell Dimensions:")
        print(x,"meters","X",y,"meters")
        print("Area of the cell: ",x*y,"meter sq")
        totalArea = x*y*self.size/(1000*1000)
        print("Total Area(in sq Km):",totalArea)
        print("Total Number of cells:",self.size)
        print("================================================================================")
    def plot_path(self,path):
        #This plot the path on OSM.
        x=[]
        y=[]
        for p in path:
            x.append(p[0])
            y.append(p[1])
        fig = plt.figure()
        plt.plot(x,y)
        mplleaflet.show(fig=fig)
    def loadNodes(self):
        #This function loads the road network graph in the main grid.
        self.road=loadRoad("RoadsNew.pkl")
        roadNodes={}
        for node in self.road.nodes:
            point = Point(node[0],node[1])
            _,_,cell_id=self.hash(point)
            if roadNodes.get(cell_id)==None:
                roadNodes[cell_id]=[]
            roadNodes[cell_id].append(node)
        self.Nodes=roadNodes
        self.Edges={}
        for e in self.road.edges:
            if self.Edges.get(e[0])==None:
                self.Edges[e[0]]=[]
            if self.Edges.get(e[1])==None:
                self.Edges[e[1]]=[]
            self.Edges[e[0]].append(e)
            self.Edges[e[1]].append(e)
        self.node_road = load_pickle(ROADNODE_PATH)
        print('loading road annotated graph ... ')
        self.EDGE_LIST,self.NODE_LIST = get_annotated_Graph(self.road.graph)
        
        
    def getShortestpath(self,source,target):
        graph = self.road.graph
        path = nx.shortest_path(graph,source,target)
        return path
    def getTotalDistance(self,path):
        totaldistance=0
        for i in range(len(path)-1):
            e1 = (path[i],path[i+1])
            e2 = (path[i+1],path[i])
            if self.road.EdgeDistance.get(e1)==None:
                e1 = e2
            totaldistance+=self.road.EdgeDistance[e1]
        return totaldistance
    def getDistanceNodes(self,node1,node2):
        path = self.getShortestpath(node1,node2)
        #print(len(path))
        return self.getTotalDistance(path)    
    def getShortestpath(self,source,target):
        graph = self.road.graph
        path = nx.shortest_path(graph,source,target)
        return path
    def getNeighbourNodes(self,cell_id):
        #this function returns the neighbour nodes if there is no node in the hashed cell.
        nodes = []
        new_cell_id=0
        offsets = [1,-1,self.split,-1*self.split]#,-1*self.split+1,-1*self.split-1,self.split+1,self.split-1]
        for offset in offsets:
                new_cell_id = cell_id+offset
                if (new_cell_id<0 or new_cell_id>=self.size) or ((cell_id%self.size!=0 and new_cell_id%self.size==0) or(cell_id%self.size==0 and new_cell_id%self.size!=0)):
                    pass
                elif self.Nodes.get(new_cell_id)!=None:
                    nodes +=self.Nodes[new_cell_id]
        return nodes
    def map_to_node(self,point):
        # Function returns the node where the point is mapped to nearest node.
        _,_,cell_id = self.hash(point)
        #print(cell_id)
        if self.Nodes.get(cell_id)==None:
            nodes = self.getNeighbourNodes(cell_id)
        else:
            nodes = self.Nodes[cell_id]+self.getNeighbourNodes(cell_id)
        if len(nodes)<=0:
            return None
        mindistance=99999999
        minEdge=None
        minNode=None
        #if nodes==None:
            #print("Yess")
        for node in nodes:
            edges = self.Edges[node]
            for edge in edges:
                e1 = Point(edge[0][0],edge[0][1])
                e2 = Point(edge[1][0],edge[1][1])
                dist = getDistanceFromline(e1,e2,point)
                #print(dist)
                if dist<mindistance:
                    
                    mindistance = dist
                    minEdge=edge
        
        e1 = Point(minEdge[0][0],minEdge[0][1])
        e2 = Point(minEdge[1][0],minEdge[1][1])

        dis1 = self.road.getDistance(e1,point)
        dis2 = self.road.getDistance(e2,point)
        if dis1>dis2:
            minNode=minEdge[1]
        else:
            minNode=minEdge[0]
        return minNode
    
    def load_stops(self,path_to_stops):
        path = path_to_stops
        data=[]
        self.stops={}
        with open(path,'rt') as f:
            da = csv.reader(f)
            for row in da:
                data.append(row)
        data=data[1:]
        for row in data:
            #print(row)
            stop_id = row[0]
            detail=row[2]
            latitude = float(row[3])
            longitude= float(row[4])
            point=Point(longitude,latitude)
            stop=Stop(stop_id,detail,point)
            _,_,cell_id=self.hash(point)
            #print("Cell_id:",cell_id)
        
            node=self.map_to_node(point)
            if node==None:
                stop.define_nearest_node(None,None)
            else:
                distance=self.road.getDistance(point,Point(node[0],node[1]))
                stop.define_nearest_node(node,distance)
            self.stops[cell_id]=stop
            
    def map_to_road(self,node,here=False):
        result =None
        result = self.node_road[node]
            
        if here ==True:
            result = result[0][1]
        else:
            result = result[0][0]
        return result

# size = 230
        
# newGrid=Grid(BoundingBox(28.4011,76.8631,28.8783,77.4481),size)


# newGrid.loadNodes()


# newGrid.defineGrid

# path=newGrid.getShortestpath(node1,node2)

