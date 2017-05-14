#coding=utf-8

import sys
import os

def loadImageList():
    num2image = {}
    with open('image_list.txt', 'r') as f:
        for index, line in enumerate(f):
            num2image[index] = int(line.strip().split('.')[0])
    return num2image
        
def generateResult(image_list, rank_file):
    rank = {}
    with open(rank_file, 'r') as f:
        for line in f:
            line = line.split()
            query = int(line[0].split('.')[0])
            if query % 100 != 0: continue
            rank[query] = []
            rank_list = map(int, line[1:])
            for index, img in enumerate(rank_list):
                if image_list[img] / 100 == query / 100:
                    rank[query].append((index, image_list[img]))
    with open('%s.dat' % rank_file, 'w') as f:
        for query in rank:
            f.write('%d.jpg' % query)
            for r in rank[query]:
                f.write(' %d %d.jpg' % (r[0], r[1]))
            f.write('\n')


if __name__ == "__main__":
    if len(sys.argv) != 2: print 'Please give filename'
    rank_file = sys.argv[1]
    image_list = loadImageList()
    generateResult(image_list, rank_file)
    
    