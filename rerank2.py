#coding = utf-8

import pickle
import copy
from GraphBuilder import GraphBuilder
import utility as ut
import numpy as np
import os
import sys
from matplotlib import pyplot as plt
import csv

DATASET = 'Data/Image'
FEATURE = 'Data/ImageFeature'

def loadRank(rank_file):
    rank = {}
    num2img = {}
    with open(rank_file, 'r') as f:
        for line in f:
            line = line.split()
            print int(line[1])
            num2img[int(line[1])] = line[0]
            line = map(int, line[1:])
            rank[line[0]] = line

    return rank, num2img

def iterativeRerank(query, graph, K = 1000):
    rank = {}
    for img in query: 
        # print 'rerank %sth image' % img
        rank[img] = query[img]
        query_len = len(query[img])
        nodes = {}
        for j in range(0, query_len):
            for item in graph[query[img][j]]:
                if item == -1: continue
                if (item in query[img]): continue
                if nodes.has_key(item): nodes[item] += graph[query[img][j]][item]
                else: nodes[item] = graph[query[img][j]][item]
                if query[img][j] in graph[item] : nodes[item] += graph[item][query[img][j]]
        nodes = sorted(nodes.iteritems(), key = lambda x: x[1], reverse = True)
        rank[img].extend([x[0] for x in nodes[0 : K - query_len]])
        if len(rank[img]) < K and graph[img].has_key(-1): 
            rank[img].extend(graph[img][-1][0 : K - len(rank[img])])
        # print rank[img]
    return rank

def extendQuery(graph, K = 10):
    cur_knn = {}
    for img in graph:
        children = {}
        for child in graph[img]:
            if child == -1: continue
            children[child] = graph[img][child]
            if graph[child].has_key(img):
                children[child] += graph[child][img]
        edges = sorted(children.items(), key = lambda x: x[1], reverse = True)
        # print edges
        nodes = []
        for edge in edges[0:K]:
            if edge[0] == img: continue
            nodes.append(edge[0])
        cur_knn[img] = [img] + nodes[0: K - 1]
    return cur_knn

def useDashengGraph(graph_path):
    graph = ut.loadObj(graph_path)
    graph = ut.graphTransform(graph)
    return graph

def loadFeature(feature_path):
    feature = readCSV(feature_path)
    return feature

def useDeepJaccardGraph(graph_path, rank, level = 3, k = 6, total = 10000):
    if os.path.exists(graph_path):
        graph = ut.loadObj(graph_path)
    else:
        graph_builder = GraphBuilder(graph_path, total)
        # graph = graph_builder.buildJaccardGraph(rank, neiborsize = 30)
        # graph = graph_builder.buildDoubleTierJaccardGraph(rank, neiborsize = 10)
        graph = graph_builder.buildDeepJaccardGraph(rank, level = level, k = k)

        # dist = loadDist(dist_file)
        # graph = graph_builder.buildDistGraph(rank, dist)
    return graph

def saveRerank(rerank, num2img, rerank_file):
    with open(rerank_file, 'w') as f:
        for img in rerank:
            rerank_list = map(str, rerank[img])            
            f.write(' '.join([num2img[img]] + rerank_list))
            f.write('\n')

def getRerank():
    haveNormalized = 'Unnormalized'
    DATA_FOLDER = 'Oxford-5k'
    DATA_FOLDER = 'Holiday'
    GRAPH_FOLDER = DATA_FOLDER + '/Graph'
    # DASHENG_GRAPH_FOLDER = DATASET + '/%s/Graph_DaSheng/' % haveNormalized

    data_set = 'oxford-5k'
    data_set = 'holiday'
    feature = 'gist'
    # total = 5065
    total = 1491
    level = 2
    k = 4
    
    query_len = 1

    rank_file = DATA_FOLDER + '/%s_rank_%s.txt' % (data_set, feature)

    rank, num2img = loadRank(rank_file)
    
    graph_path = GRAPH_FOLDER + '/%s-%s-graph-%d-%d.pickle' % (data_set, feature, level, k)
    graph = useDeepJaccardGraph(graph_path, rank, level = level, k = k, total = total)

    print '-'*50
    print '%s \t %s'  % (data_set, feature)
    print 'level: %d' % level
    print '    k: %d' % k
    print 'query: %d' % query_len
    print '-' * 50

    query = extendQuery(graph, query_len)
    rerank = iterativeRerank(query, graph)
    rerank_file = DATA_FOLDER + '/%s_rerank_%s.txt' % (data_set, feature)
    saveRerank(rerank, num2img, rerank_file)

if __name__ == '__main__':
    # rerank()
    getRerank()