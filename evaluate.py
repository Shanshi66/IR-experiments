#coding=utf8

OXFORD5K = 'Oxford-5k'
GROUND_TRUTH = OXFORD5K + '/GroundTruth'
import os

def loadQuerys(folder):
    querys = {}
    GROUND_TRUTH = folder + '/GroundTruth'
    for file_name in os.listdir(GROUND_TRUTH):
        if 'query' not in file_name: continue
        with open(GROUND_TRUTH + '/%s' % file_name, 'r') as f:
            img_name = f.readline().split()[0]
            file_name = file_name.split('_')[:-1]
            file_name = '_'.join(file_name)
            querys[img_name] = file_name
    return querys

def loadImageList(image_list_file):
    index2name = {}
    with open(image_list_file, 'r') as f:
        for index, line in enumerate(f):
            line = line.split('_')
            index2name[index] = '_'.join(line[1:])
            index2name[index] = index2name[index].strip()
    return index2name

def getRankList(rank_file, folder):
    querys = loadQuerys(folder)
    index2name = loadImageList(folder + '/image_list.txt')
    rank_list = {}
    with open(rank_file, 'r') as f:
        for line in f:
            line = line.split()
            img_name = line[0]
            rank = line[1:]
            img_name = img_name.split('.')[0]
            if querys.has_key(img_name):
                rank_list[querys[img_name]] = []
                for r in rank:
                    rank_list[querys[img_name]].append(index2name[int(r)])
    return rank_list

def computeAP(good_set, junk_set, rank):
    old_recall = 0.0
    old_precison = 1.0
    ap = 0.0
    intersect_size = 0
    for index, img in enumerate(rank):
        # if index == 4: break
        if img in junk_set: continue
        if img in good_set: intersect_size += 1

        recall = float(intersect_size) / float(len(good_set))
        precision = float(intersect_size) / (index + 1.0)

        ap += (recall - old_recall) * (old_precison + precision) / 2.0

        old_recall = recall
        old_precison = precision
    return ap

def loadStdResult(file_name):
    result = set()
    with open(file_name, 'r') as f:
        for line in f:
            result.add(line.strip())
    return result

def evaluateSingleOxford5K(query, rank):
    good_set = loadStdResult(GROUND_TRUTH + '/%s_good.txt' % query)
    ok_set = loadStdResult(GROUND_TRUTH + '/%s_ok.txt' % query)
    junk_set = loadStdResult(GROUND_TRUTH + '/%s_junk.txt' % query)

    good_set = good_set.union(ok_set)
    print query
    ap = computeAP(good_set, junk_set, rank)
    return ap

def evaluateOxford5K(rank_file):
    rank_list = getRankList(rank_file, OXFORD5K)
    precision = 0
    pset = []
    for query in rank_list:
        p = evaluateSingleOxford5K(query, rank_list[query])
        precision += p
        pset.append((query, p))
    pset.sort()
    for p in pset:
        print p[0], p[1]
    precision = precision / len(rank_list)
    print precision
    

if __name__ == '__main__':
    evaluateOxford5K(OXFORD5K + '/oxford-5k_rank_cnn.txt')