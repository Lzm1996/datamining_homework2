#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import os
from chardet import detect

DATA_FILE = '../data/diagnosis.data'
OUTPUT_FILE = '../data/diagnosis.csv'
# build up the number presentation of each feature
HEAD = '1:temp,2:nausea,3:lumbar,4:urine,5:micturition,6:urethra,7:inflammation,8:nephritis\n'

def preprocess(source_path, target_path):
    fp_read = open(source_path, 'r')
    fp_write = open(target_path, 'w')
    fp_write.write(HEAD)
    for line in fp_read:
        content = line.strip().split()
        output = []
        # get the tempreture
        temp = float(content[0].replace(',', '.'))
        if temp >= 38.0:
            output.append('1')
        # for each feature besides tempreture, mark feature number if identifier is 'yes'
        for i in range(1,8):
            if content[i] == 'yes':
                output.append(str(i+1))
        fp_write.write(','.join(output)+'\n')
    fp_read.close()
    fp_write.close()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        while not os.path.exists(file_path):
            file_path = raw_input('File not exist! Please enter the data file path:')
    else:
        file_path = DATA_FILE
    preprocess(file_path, OUTPUT_FILE)