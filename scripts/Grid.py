#####################################################################################################################

##This Program is used to create a Grid object of desired size and storing latitude and longitude in it accoordingly

#####################################################################################################################
import csv
import pandas as pd
import math
from math import sin, cos, sqrt, atan2, radians
import numpy as np 
import pickle
import networkx as nx
import time

def getDistanceFromline(e1,e2,point):
        m = (e1.y-e2.y)/(e1.x-e2.x)
        b = e1.y - (m*e1.x)
        distance = distancepoint(-1*m,1,-1*b,point)
        return distance
def distancepoint(a,b,c,point):
        num = abs(a*point.x+ b*point.y + c)
        den = math.sqrt(a**2+b**2)
        return num/den
def saveRoad(road,filename):
    with open(filename,'wb') as dbfile:
        pickle.dump(road,dbfile)
def loadRoad(filename):
    road=None
    with open(filename,'rb') as dbfile:
        road=pickle.load(dbfile)
    return road
def onSegment(p,q,r):
    if (p.x<=math.min(p.x,r.x) and q.x>= math.min(p.x,r.x)) and (q.y<=math.min(p.y,r.y) and q.y >= math.min(p.y,r.y)):
        return True
    else:
        return False
def orientation(p,q,r):
    val = ((q.y - p.y) * (r.x - q.x)) - ((q.x-p.x)*(r.y-q.y))
    if val==0:
        return 0
    if val>0:
        return 1
    else:
        return 2
def doIntersect(p1,q1,p2,q2):
    o1 = orientation(p1,q1,p2)
    o2 = orientation(p1,q1,q2)
    o3 = orientation(p2,q2,p1)
    o4 = orientation(p2,q2,q1)
    
    if o1!=o2 and o3!=o4:
        return True
    if o1==0 and onSegment(p1,p2,q1):
        return True
    if o2==0 and onSegment(p1,q2,q1):
        return True
    if o3==0 and onSegment(p2,p1,q2):
        return True
    if o4==0 and onSegment(p2,q1,q2):
        return True
    return False
def getNode(location,grid):
    cell_id = grid.hash(location)
    p1 = Point(location.lat,location.long)
    mini = 88888*(10**9)
    p=-1
    
    for e  in grid.edgeList[cell_id]:
        edge = grid.road.edges[e]
        p2 = Point(edge[0][1],edge[0][0])
        p3 = Point(edge[1][1],edge[1][0])
        dis = getDistanceFromline(p2,p3,p1)
        if dis<mini:
            mini=dis
            p=edge[0]
    return p
        
        
class locat:
    def __init__(self,lat,long):
        self.lat = lat
        self.long = long
    def getLatitude(self):
        return self.lat
    def getLongitude(self):
        return self.long
    def getPrint(self):
        print("Latitde:",self.getLatitude(),", Longitude:",self.getLongitude())

class cell:
    def __init__(self,cell_id):
        self.cell_id = cell_id 
        self.posting = {}
        self.busEntries = {}
        self.averageSpeeds={}
class Point:
    def __init__(self,lat,long):
        self.y = lat
        self.x = long
class Graph:
    def __init__(self,nodes=None,edges=None):
        self.graph=None
        self.edges=None
        self.nodes=None
        if node!=None and edges!=None:
            self.graph=generateGraph(nodes,edges)
    def generateGraph(nodes,edges):
        pass
    def addEdge(point1,point2):
        pass
        
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
        path = nx.single_source_shortest_path(self.graph,node1)
        return path[node2]
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
            self.EdgeDistance[e]=getDistance(point1,point2)
    def getDistanceBetweenTwoNodes(self,node1,node2):
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
            totaldistance+=road.EdgeDistance[e1]
        return totaldistance            
    def getDistance(self,point1,point2):
        radius=6371000 #meters
        dlat = math.radians(point2.y-point1.y)
        dlong = math.radians(point2.x-point1.x)
        a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(point1.y)) * math.cos(math.radians(point2.y)) * math.sin(dlong/2) * math.sin(dlong/2)
        c = 2 * math.atan2(math.sqrt(a),math.sqrt(1-a))
        dist = float(radius * c)
        return dist# distance in meters        
    
class GridMaker:
    def __init__(self,min_latitude,min_longitude,max_latitude,max_longitude,split):
        self.min_lat = min_latitude
        self.min_long = min_longitude
        self.max_lat = max_latitude
        self.max_long = max_longitude
        self.split = split
        self.gridSize = split*split
        self.GRID = None
        
    def loadGrid(self,grid):
        self.GRID=grid
    
    def getMinBoundary(self):
        return [self.min_lat,self.min_long]
    
    def getMaxBoundary(self):
        return [self.max_lat,self.max_long]
    
    def updateSplit(self,new_split):
        self.split=new_split
    
    def getLatStepSize(self):
        diff = self.max_lat-self.min_lat
        return diff/self.split
    
    def getLongStepSize(self):
        diff = self.max_long-self.min_long
        return diff/self.split
    
    def hash(self,point):
        latStep = self.getLatStepSize()
        longStep= self.getLongStepSize()
        latDiff = point.getLatitude()-self.min_lat
        longDiff = point.getLongitude()-self.min_long
        row = math.floor(latDiff/latStep)
        col = math.floor(longDiff/longStep)
        cell_id = row*self.split + col
        return cell_id
    def hashedge(self,point):
        latStep = self.getLatStepSize()
        longStep= self.getLongStepSize()
        latDiff = point.getLatitude()-self.min_lat
        longDiff = point.getLongitude()-self.min_long
        row = math.floor(latDiff/latStep)
        col = math.floor(longDiff/longStep)
        cell_id = row*self.split + col
        return row,col,cell_id
    
    def getAllGridsForEdge(self,row1,col1,row2,col2,line1,line2):
        grids =[]
        if row1==row2:
            if col1>col2:
                while col2!=col1:
                    cell_id = row2*self.split+col2
                    grids.append(cell_id)
                    col2+=1
            elif col1<col2:
                while col1!=col2:
                    cell_id = row2*self.split+col1
                    grids.append(cell_id)
                    col1+=1
            else:
                cell_id = row1*self.split+col1
                grids.append(cell_id)
        elif col1==col2:
            if row1>row2:
                while row1!=row2:
                    cell_id=row2*self.split+col2
                    grids.append(cell_id)
                    row2+=1
            elif row1<row2:
                while row1!=row2:
                    cell_id = row1*self.split + col1
                    grids.append(cell_id)
                    row1+=1
            else:
                cell_id = row1*self.split + col1
                grids.append(cell_id)
        else:
            cell_id1 = row1*self.split+col1
            cell_id2 = row2*self.split+col2
            if cell_id1>cell_id2:
                x = cell_id1
                cell_id1=cell_id2
                cell_id2=x
            for i in range(cell_id1,cell_id2+1):
                l1,l2,l3,l4 = self.getFourCordinatesOfCellEdge(i)
                if (doIntersect(l1,l2,line1,line2) or doIntersect(l1,l3,line1,line2)) or (doIntersect(l3,l4,line1,line2) or doIntersect(l2,l4,line1,line2)):
                    grids.append(i)
        return grids
    def loadEdges(self):
        self.road = loadRoad("Roads.pkl")
        road = self.road
        self.edgeList={}
        for i in range(len(road.edges)):
            edge = road.edges[i]
            edge1 = edge[0]
            edge2 = edge[1]
            l1 = locat(edge1[1],edge1[0])
            l2 = locat(edge2[1],edge2[0])
            row,col,cell_id = self.hashedge(l1)
            row2,col2,cell_id2 = self.hashedge(l2)
            if cell_id<0 or cell_id>=self.gridSize:
                pass
            else:
                if cell_id == cell_id2:
                    if self.edgeList.get(cell_id)==None:
                        self.edgeList[cell_id]=[]
                    self.edgeList[cell_id].append(i)
                else:
                    cell_ids = self.getAllGridsForEdge(row,col,row2,col2,Point(edge1[1],edge1[0]),Point(edge2[1],edge2[0]))
                    for cell_id in cell_ids:
                        if self.edgeList.get(cell_id)==None:
                            self.edgeList[cell_id]=[]
                        self.edgeList[cell_id].append(i)
    
    def getCordinatesOfCell(self,cell_id):
        latStep = self.getLatStepSize()
        longStep= self.getLongStepSize()
        col = cell_id%self.split
        row = (cell_id-col)/self.split
        latitude1 = self.min_lat+ row *latStep
        longitude1= self.min_long + col * longStep
        return latitude1,longitude1
    
    def getFourCordinatesOfCell(self,cell_id):
        lat,long = self.getCordinatesOfCell(cell_id)
        latStep = self.getLatStepSize()
        longStep= self.getLongStepSize()
        loc1 = locat(lat,long)
        loc2 = locat(lat+latStep,long)
        loc3 = locat(lat,long+longStep)
        loc4 = locat(lat+latStep,long+longStep)
        return [loc1,loc2,loc3,loc4]

    def getFourCordinatesOfCellEdge(self,cell_id):
        lat,long = self.getCordinatesOfCell(cell_id)
        latStep = self.getLatStepSize()
        longStep= self.getLongStepSize()
        loc1 = Point(lat,long)
        loc2 = Point(lat+latStep,long)
        loc3 = Point(lat,long+longStep)
        loc4 = Point(lat+latStep,long+longStep)
        return loc1,loc2,loc3,loc4

    def validateLocation(self,loc):
        lat = loc.getLatitude()
        lon = loc.getLongitude()
        if (lat<self.min_lat or lat>self.max_lat) or (lon<self.min_long or lon>self.max_long):
            return False
        return True
        
    def getAddressOfCell(self,cell_id):
        pass
        #body of this fucntion is to return address
        
        
    def create_CSV(self,filename):
        data = {}
        data['cell_id']=[]
        data['latitude']=[]
        data['longitude']=[]
        for i in range(self.gridSize):
            data['cell_id'].append(i)
            lat,long = self.getCordinatesOfCell(i)
            data['latitude'].append(lat)
            data['longitude'].append(long)
        df = pd.DataFrame(data)
        df.to_csv(filename,index=False)
        print('data writed to :',filename)
    
    def createPostingList(self,file): #### with the use of csvreader
        cellList={}
        start = time.time()
        for i in range(self.gridSize):
            cellList[i]=cell(i)
        with open(file,'r') as csvFile:
            reader = csv.reader(csvFile)
            col = next(reader)
            #print(col)
            for row in reader:
                #print(row)
                #print(row[2],row[3])
                loc = locat(float(row[2]),float(row[3]))
                road_id = str(row[1])
                cell_id = self.hash(loc)
                if self.validateLocation(loc)==True:
                    if cellList[cell_id].posting.get(road_id)==None:
                        cellList[cell_id].posting[road_id]=[]
                    cellList[cell_id].posting[road_id].append(loc)
        self.GRID =cellList
        csvFile.close()
        end = time.time()
        print("Done with Postings in ",end-start)
        
    def createPostingListOld(self,file): ### With the use of dataframe reading
        print("creating Postings for Cells")
        dataFrame = pd.read_csv(file)
        cellList={}
        for i in range(self.gridSize):
            cellList[i]=cell(i)
        for i in range(len(dataFrame)):
            lat = dataFrame['Latitude'][i]
            long= dataFrame['Longitude'][i]
            road_id = dataFrame['Road_id'][i]
            loc = locat(lat,long)
            cell_id = self.hash(loc)
            if self.validateLocation(loc)==True:
                if cellList[cell_id].posting.get(road_id)==None:
                    cellList[cell_id].posting[road_id]=[]
                cellList[cell_id].posting[road_id].append(loc)
        self.GRID = cellList
        print("Done with Postings")
        
    def createPostingListForRoad(self,file):
        print("creating Postings for Cells")
        dataFrame = pd.read_csv(file)
        cellList={}
        for i in range(self.gridSize):
            cellList[i]=cell(i)
        for i in range(len(dataFrame)):
            lat = dataFrame['stop_lat'][i]
            long= dataFrame['stop_lon'][i]
            road_id = dataFrame['road_id'][i]
            loc = locat(lat,long)
            cell_id = self.hash(loc)
            if self.validateLocation(loc)==True:
                if cellList[cell_id].posting.get(road_id)==None:
                    cellList[cell_id].posting[road_id]=[]
                cellList[cell_id].posting[road_id].append(loc)
        self.GRID = cellList
        print("Done with Postings")

def createPickle(newGrid):
    with open("SharedMemory/gridWithPosting.pickle", 'wb') as handle:
            pickle.dump(newGrid, handle, protocol=pickle.HIGHEST_PROTOCOL)

if __name__=="__main__":
    t1 =time.time()
    size = 230
    newGrid=GridMaker(28.4011,76.8631,28.8783,77.4481,size)
    list1=newGrid.getFourCordinatesOfCell(21070)
    for coord in list1:
        print(coord.getLatitude())
        print(coord.getLongitude())
    list2=newGrid.getFourCordinatesOfCell(20615)
    for coord in list2:
        print(coord.getLatitude())
        print(coord.getLongitude())

    #newGrid.create_CSV("SharedMemory/grid_"+str(size)+".csv")
    #newGrid.createPostingList('GridReq/combinedRoadInfo.csv')
    #createPickle(newGrid)
    #t2 =time.time()
    #print("Process terminated in :: ",t2-t1)
