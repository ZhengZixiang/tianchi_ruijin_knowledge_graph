# -*- coding: utf-8 -*-
import os
import codecs
import pandas as pd
import pycrfsuite
from crfsuite_model import sent2features


def write_format(file, id, label, start_end_pairs, entity):
    string = ''
    j = 1
    for pair in start_end_pairs:
        string += str(pair[0]) + ' ' + str(pair[1])
        if j < len(start_end_pairs):
            string += ';'
            j += 1
    file.write('T{0}\t{1} {2}\t{3}\n'.format(id, label, string, entity))


if __name__ == '__main__':
    level = 'char'
    # 预测
    tagger = pycrfsuite.Tagger()
    tagger.open('./model/tianchi_ner_char_level_1000.crfsuite')

    directory = './data/'+level+'_level_test_set/'
    filenames = os.listdir(directory)
    for filename in filenames:
        if filename.endswith('.csv'):
            sent = []
            df = pd.read_csv(directory + filename, skip_blank_lines=False)
            for index, row in df.iterrows():
                if level == 'word':
                    sent.append((row['seq'], row['pos']))
                elif level == 'char':
                    sent.append((row['char']))
            x_test = sent2features(sent, level)
            y_test = tagger.tag(x_test)

            f = codecs.open('./submit/' + filename[:-4] + '.ann', 'w')
            id = 0
            start_end_pairs = [[0, 0]]  # 用列表的形式存储起始字符
            flag = False
            entity = ''  # 用于字符串拼接
            for i in range(0, len(y_test)):
                if y_test[i] != 'O':
                    if y_test[i][:1] == 'B' and flag == False:  # 若满足条件，则代表是实体的开始
                        entity = sent[i][0]
                        flag = True
                        start_end_pairs[-1][0] = start_end_pairs[-1][1]
                        del(start_end_pairs[:-1])  # B重新开始记录起止位置，所以删除前面的元素
                    elif y_test[i][:1] == 'B' and flag == True:  # 代表上一个实体刚结束，新的实体紧接着开始
                        id += 1
                        write_format(f, id, y_test[i-1][2:], start_end_pairs, entity)
                        start_end_pairs[-1][0] = start_end_pairs[-1][1]
                        del (start_end_pairs[:-1])  # B重新开始记录起止位置，所以删除前面的元素
                        # entity = ''
                        entity = sent[i][0]
                    elif y_test[i][:1] == 'I':  # 代表当前token仍然属于同一实体
                        if str(sent[i][0]) == '\n':
                            entity += ' '
                            start_end_pairs.append([start_end_pairs[-1][1]+1, start_end_pairs[-1][1]])
                        else:
                            entity += str(sent[i][0])
                elif flag:
                    flag = False
                    id += 1
                    write_format(f, id, y_test[i - 1][2:], start_end_pairs, entity)
                start_end_pairs[-1][1] += len(str(sent[i][0]))
            f.close()
