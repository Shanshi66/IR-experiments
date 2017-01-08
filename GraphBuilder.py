# coding = utf-8

import utility as ut
import numpy as np
import Queue
import pickle
import sys
from progressbar import *
import time

class GraphBuilder:

    def __init__(self, graph_path, total):
        self.graph_path = graph_path
        self.total = total

    # @timer('build jaccard graph', False)
    def buildJaccardGraph(self, rank, neiborsize = 20):
        graph = {}
        for img in rank:
            graph[img] = {}
            for candidate in rank[img]:
                graph[img][candidate] = self.calculateJaccard(set(rank[img][0:neiborsize]), set(rank[candidate][0:neiborsize]))
        return graph

    def buildDoubleTierJaccardGraph(self, rank, neiborsize = 20):
        graph = {}
        for img in rank:
            graph[img] = {}
            for candidate in rank[img]:
                set_a = set()
                for neibor in rank[img][0:neiborsize]:
                    if neibor == candidate: continue
                    set_a.update(rank[neibor][0:neiborsize])
                
                set_b = set()
                for neibor in rank[candidate][0:neiborsize]:
                    if neibor == img: continue
                    set_b.update(rank[neibor][0:neiborsize])
                graph[img][candidate] = self.calculateJaccard(set_a, set_b)
        return graph
    
    def bfs_jaccard(self, rank, img, neiborsize, level = 3, k = 5):
        queue = [(img, 0)]
        visit = set([img])
        while len(queue) > 0:
            node = queue.pop(0)
            edges = {}
            for child in rank[node[0]][0 : neiborsize]:
                edges[child] = self.calculateJaccard(set(rank[child][0:neiborsize]), 
                                                     set(rank[node[0]][0:neiborsize]))

            edges = sorted(edges.iteritems(), key = lambda x: x[1], reverse = True)
            for edge in edges[0 : k]:
                if edge[0] in visit: continue
                if node[1] + 1 <= level: 
                    queue.append((edge[0], node[1] + 1))
                visit.add(edge[0])
        return visit
    
    def bfs_dist(self, rank, img, level = 2, k = 10):
        queue = [(img, 0)]
        visit = set([img])
        knn = []
        while len(queue) > 0:
            node = queue.pop(0)
            knn.append(node[0])
            # for child in rank[node[0]][0 : int(k * (1.1 ** node[1]))]:
            for child in rank[node[0]][0 : k]:
                if child in visit: continue
                if node[1] + 1 <= level: 
                    queue.append((child, node[1] + 1))
                    visit.add(child)
        # print len(visit)
        return knn

    def buildDeepJaccardGraph(self, rank, level = 2, k = 10):
        start_time = time.time()
        pbar = ProgressBar().start()
        graph = {}
        average_set_size = 0
        for img in rank:
            pbar.update(float(img) / self.total * 100)
            graph[img] = {}
            for candidate in rank[img][0:200]:
                set_a = self.bfs_dist(rank, img, level, k)
                set_b = self.bfs_dist(rank, candidate, level, k)
                len_a = len(set_a)
                len_b = len(set_b)
                # print len_a, len_b
                if len_a > min(len_a, len_b):
                    set_a = set_a[0 : min(len_a, len_b)]
                if len_b > min(len_a, len_b):
                    set_b = set_b[0 : min(len_a, len_b)]
                average_set_size += len(set_a)
                # print len(set_a), len(set_b)
                graph[img][candidate] = self.calculateJaccard(set_a, set_b)
                #print len(set_a), len(set_b)
        ut.dumpObj(graph, self.graph_path)
        pbar.finish()
        print average_set_size / len(rank) / 200
        end_time = time.time()
        print 'It takes %ds to build graph' % (end_time - start_time) 
        return graph

    def buildDistGraph(self, rank, dist):
        graph = {}
        for img in rank:
            graph[img] = {}
            for index, candidate in enumerate(rank[img][0:200]):
                graph[img][candidate] = dist[img][index]
            if img == 1: 
                print graph[img]
        return graph

    def calculateJaccard(self, s1, s2):
        s1 = set(s1)
        s2 = set(s2)
        intersection = s1 & s2
        union = s1 | s2
        jaccard = float(len(intersection)) / float(len(union))

        # k = float(len(intersection)) / np.sqrt(len(s1)) / np.sqrt(len(s2))
        
        # jaccard = float(len(intersection)) / max(len(s1), len(s2)) 
        # if jaccard > 0.1: jaccard = 1
        return jaccard
    
