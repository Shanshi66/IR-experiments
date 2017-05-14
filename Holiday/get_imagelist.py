

def getImageList(rank_file):
    image_list = []
    with open(rank_file, 'r') as f:
        for line in f:
            image_list.append(line.split()[0].strip())
    with open('image_list.txt', 'w') as f:
        for img in image_list:
            f.write('%s\n' % img)

if __name__ == "__main__":
    getImageList('holiday_rank_cnn.txt')