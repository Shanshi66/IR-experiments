import os
import sys

GROUND_TRUTH = 'GroundTruth'

def loadQuerys():
    querys = {}
    for file_name in os.listdir(GROUND_TRUTH):
        if 'query' not in file_name: continue
        with open(GROUND_TRUTH + '/%s' % file_name, 'r') as f:
            img_name = f.readline().split()[0]
            file_name = file_name.split('_')[:-1]
            file_name = '_'.join(file_name)
            querys[img_name] = file_name
    return querys

def getSingleRanklist(folder, index2name, querys, rank_file):
    with open(rank_file, 'r') as f:
        for line in f:
            line = line.split()
            img_name = line[0]
            rank = line[1:]
            img_name = img_name.split('.')[0]
            if querys.has_key(img_name):
                with open(folder + '/%s_rank_list.txt' % querys[img_name], 'w') as rankf:
                    for r in rank:
                        rankf.write('%s\n' % index2name[int(r)])

def loadImageList(image_list_file):
    index2name = {}
    with open(image_list_file, 'r') as f:
        for index, line in enumerate(f):
            line = line.split('_')
            index2name[index] = '_'.join(line[1:])
            index2name[index] = index2name[index].strip()
    return index2name
            

if __name__ == '__main__':
    rank_file = 'oxford-5k_%s_%s.txt' % (sys.argv[1], sys.argv[2])
    folder = sys.argv[2]
    if not os.path.exists(folder): os.mkdir(folder)
    querys = loadQuerys()
    index2name = loadImageList('image_list.txt')
    getSingleRanklist(folder, index2name, querys, rank_file)
