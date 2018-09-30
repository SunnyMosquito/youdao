import os
import re

data = None
baseDir = os.path.dirname(__file__)
fileName = os.path.join(baseDir,'OxfordEnDict.txt')

with open(fileName) as f:
    data = f.readlines()


for i in range(len(data)):
    item = data[i].split()
    if item:
        if re.search('[\u4e00-\u9fa5]+', item[0]):
            data[i-1] = data[i-1][:-1] + data[i]
            data[i] = ''

with open(fileName,'wt') as f:

    for j in data:
        if j.split():
            f.write(j)

# with open(fileName,'wt') as f:
#     for item in data:
#         if not item.endswith('.\n'):
#             f.write(item)
#             print(item.encode('utf-8'))
#         else:
#             print(item)
#             f.write(item[:-2])


# print(len(data))