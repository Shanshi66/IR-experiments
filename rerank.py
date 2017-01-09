#coding = utf-8

import pickle
import copy
from GraphBuilder import GraphBuilder
import utility as ut
import numpy as np
import os
import sys

DATASET = 'Data/Image'
FEATURE = 'Data/ImageFeature'

def loadRank(rank_file):
    rank = {}
    with open(rank_file, 'r') as f:
        for line in f:
            line = line.split()[1 : ]
            line = map(int, line)
            rank[line[0]] = line
    return rank

def loadDist(dist_file):
    dist = {}
    with open(dist_file, 'r') as f:
        for line in f:
            line = line.split()
            img = int(line[0].split('.')[0])
            line = map(float, line[1 : ])
            dist[img - 1] = line
    return dist

def computeAccuracy(rank, k, class_num):
    accuracy = []
    for img in rank:
        count = 0
        for i in range(k):
            if img / class_num == rank[img][i] / class_num: count += 1
        accuracy.append(float(count) / k)
    return sum(accuracy) / len(accuracy)

def evaluate(rank, rerank, K, class_num, data_set, first_k):
    if not first_k:
        print '%10s %10s %10s %10s' % ('id', 'before', 'after', 'improvement')
    result = []
    for i in range(1, K + 1):
        rerank_accuracy = computeAccuracy(rerank, i, class_num)
        rank_accuracy = computeAccuracy(rank, i, class_num)
        
        if data_set == 'UK': 
            rerank_accuracy = rerank_accuracy * 4
            rank_accuracy = rank_accuracy * 4
        else:
            rerank_accuracy = rerank_accuracy * 100
            rank_accuracy = rank_accuracy * 100

        improvement = rerank_accuracy - rank_accuracy

        rerank_accuracy = round(rerank_accuracy, 2)
        rank_accuracy = round(rank_accuracy, 2)
        improvement = round(improvement, 2)
        if i in first_k: 
            result.append(rerank_accuracy)
        if not first_k:
            print '%10d %10.2f %10.2f %10.2f' % (i, rank_accuracy, rerank_accuracy, improvement)
    return result

def iterativeRerank(query, graph, K = 20):
    rank = {}
    for img in query: 
        # print 'rerank %sth image' % img
        rank[img] = query[img]
        query_len = len(query[img])
        if query_len >= K: continue
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

feature_types = ['CDH', 'HSV', 'LBP', 'MSD', 'TCD1', 'TCD2']

def extendQuery(graph, K = 10):
    cur_knn = {}
    for img in graph:
        cur_knn[img] = [img]
        if len(cur_knn[img]) >= K: continue
        candidate_set = set()
        for item in cur_knn[img]:
            for candidate in graph[item]:
                if candidate == -1: continue
                if candidate in cur_knn[img]: continue
                candidate_set.add(candidate)
        while len(cur_knn[img]) <= K:
            maxNode = -1; maxWeight = -1;
            for candidate in candidate_set:
                if candidate == -1: continue
                if candidate in cur_knn[img]: continue
                weight_sum = 0
                for haveSelect in cur_knn[img]:
                    if graph[haveSelect].has_key(candidate):
                        weight_sum += graph[haveSelect][candidate]
                    if graph[candidate].has_key(haveSelect):
                        weight_sum += graph[candidate][haveSelect]
                if weight_sum > maxWeight:
                    maxWeight = weight_sum
                    maxNode = candidate
            if maxNode == -1: break
            cur_knn[img].append(maxNode)
            for candidate in graph[maxNode]:
                candidate_set.add(candidate)
    return cur_knn

def extendQuery_2(graph, K = 10):
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

def useDeepJaccardGraph(graph_folder, feature, rank, level = 3, k = 6, total = 10000):
    graph_path = GRAPH_FOLDER + '%s-%s-graph-%d-%d.pickle' % (data_set, feature, level, k)
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

if __name__ == '__main__':

    data_set = sys.argv[1]
    each_class = int(sys.argv[2])
    total = int(sys.argv[3])
    feature = sys.argv[4]
    level = int(sys.argv[5])
    k = int(sys.argv[6])


    haveNormalized = 'Unnormalized'
    norm = 'L1'
    # data_set = 'Coil100'
    # data_set = 'Corel1k'
    # data_set = 'UK'
    DATA_FOLDER = DATASET + '/%s/%s/%s/' % (haveNormalized, norm, data_set)
    GRAPH_FOLDER = DATASET + '/%s/%s/GraphDeepJaccard/' % (haveNormalized, norm)
    DASHENG_GRAPH_FOLDER = DATASET + '/%s/Graph_DaSheng/' % haveNormalized
    
    # each_class = 100
    # each_class = 72
    # each_class = 4
    # total = 10000
    # total = 7200
    # total = 10200

    # feature = 'msd'
    # method = 'TTNG'
    method = 'LSSM'
    # level = 2
    # k = 9
    query_len = 1

    
    rank_file = DATA_FOLDER + 'rank_%s.txt' % feature
    dist_file = DATA_FOLDER + 'rank_%s.dist' % feature
    rank = loadRank(rank_file)
    
    if method == 'LSSM':
        graph = useDeepJaccardGraph(GRAPH_FOLDER, feature, rank, level = level, k = k, total = total)
    else:
        graph_path = DASHENG_GRAPH_FOLDER + '%s-%s.pickle' % (data_set, feature)
        graph = useDashengGraph(graph_path)
    
    K = 30

    print '-'*50
    print '%s %s \t %s \t %s \t %s' % (haveNormalized, norm, data_set, feature, method)
    if method == 'LSSM':
        print 'level: %d' % level
        print '    k: %d' % k
    print 'query: %d' % query_len
    print '-'*50

    # query = extendQuery(graph, query_len)
    # query = extendQuery_2(graph, query_len)
    # rerank = iterativeRerank(query, graph, K = K)
    # evaluate(rank, rerank, K, each_class, data_set)

    firstKs = [12, 20, 30]
    # firstKs = [4]
    print '\t'.join([str(x) for x in firstKs])
    origin = []
    for i in firstKs:
        accuracy = computeAccuracy(rank, i, each_class)
        if data_set == 'UK': 
            accuracy *= 4
        else:
            accuracy *= 100
        origin.append(round(accuracy, 2))
    print '\t'.join([ str(x) for x in origin ])
    print
    for i in range(1, query_len + 1):
        query = extendQuery_2(graph, i)
        # query = extendQuery(graph, i)
        rerank = iterativeRerank(query, graph, K = K)
        # result = evaluate(rank, rerank, K, each_class, data_set, [])
        result = evaluate(rank, rerank, K, each_class, data_set, firstKs)
        result = '\t'.join([ str(x) for x in result ])
        print result


