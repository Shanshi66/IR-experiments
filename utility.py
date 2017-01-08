#coding = utf8

import csv
import time
import cPickle


def graphTransform(graph):
    new_graph = {}
    for index, g in enumerate(graph):
        all_keys = g.keys()
        weight_sum = {}
        for cur_key in all_keys:
            if cur_key == -1: continue
            cur_weights = g[cur_key]
            for weight in cur_weights:
                if cur_key not in weight_sum.keys():
                    weight_sum[cur_key] = weight[1] 
                else:
                    weight_sum[cur_key] += weight[1]
        if g.has_key(-1):
            for i in g[-1]:
                if not weight_sum.has_key(i): weight_sum[i] = 0
        new_graph[index] = weight_sum
    return new_graph

def readCSV(file_name):
    data = []
    with open(file_name, 'r') as f:
        reader = csv.reader(f)
        for line in reader:
            line = map(float, line)
            data.append(line)
    return data

def writeCSV(file_name, data):
    with open(file_name, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(data)

def caculateDistance(vector_a, vector_b):
    vector = map(lambda x: x[0] - x[1], zip(vector_a, vector_b))
    vector = map(lambda x: x * x, vector)
    return sum(vector)

# decorator
def timer(time_what, have_return):
    def _timer(func):
        def __timer(*args, **kwargs):
            begin_time = time()
            if have_return: 
                ret = func(*args, **kwargs)
            else :
                func(*args, **kwargs)
            end_time = time()

            print "It take %d to %s" % (end_time - begin_time, time_what)

            if have_return :
                return ret
    return _timer

def dumpObj(obj, file_path):
    with open(file_path, 'wb') as f:
        cPickle.dump(obj, f, 2)

def loadObj(file_path):
    with open(file_path, 'rb') as f:
        obj = cPickle.load(f)
    return obj