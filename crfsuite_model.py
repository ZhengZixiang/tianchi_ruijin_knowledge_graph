# -*- coding: utf-8 -*-
import os
import pycrfsuite
import pandas as pd
import progressbar
import string
import sys

from stroke.character_stroke_handian import Stroke
from cnradical import Radical, RunOption
from pypinyin import lazy_pinyin


def get_radical(word):
    radical = Radical(RunOption.Radical)
    rs = [radical.trans_ch(ele) for ele in word]
    str = ''
    for r in rs:
        if r is not None:
            str += r
    return str


def word2features(sent, i):
    word = str(sent[i][0])
    pos = sent[i][1]
    features = ['bias',
                'word=' + word,
                'word_tag=' + pos,
                'word_len=' + str(len(word))
                ]
    if i > 0:
        word1 = str(sent[i-1][0])
        pos1 = sent[i-1][1]
        features.extend(['-1:word=' + word1,
                         '-1:word_tag=' + pos1,
                         '-0,1:word=' + word1 + word,
                         '-0,1:pos=' + pos1 + pos])
        if i > 1:
            word2 = str(sent[i-2][0])
            pos2 = sent[i-2][1]
            features.extend(['-2:word=' + word2,
                             '-2:word_tag=' + pos2,
                             '-1,2:word=' + word2 + word1,
                             '-1,2:pos=' + pos2 + pos1,
                             '-0,1,2:word=' + word2 + word1 + word,
                             '-0,1,2:pos=' + pos2 + pos1 + pos])
        if i < len(sent)-1:
            features.extend(['101:word=' + word1 + word + str(sent[i+1][0])])
    if i < len(sent) - 1:
        word1 = str(sent[i+1][0])
        pos1 = sent[i+1][1]
        features.extend(['+1:word=' + word1,
                         '+1:word_tag=' + pos1,
                         '+0,1:word=' + word + word1,
                         '+0,1:pos=' + pos + pos1])
        if i < len(sent) - 2:
            word2 = str(sent[i+2][0])
            pos2 = sent[i+2][1]
            features.extend(['+2:word=' + word2,
                             '+2:word_tag=' + pos2,
                             '+1,2:word=' + word1 + word2,
                             '+1,2:pos=' + pos1 + pos2,
                            '-0,1,2:word=' + word + word1 + word2,
                            '-0,1,2:pos=' + pos + pos1 + pos2])
    return features


global stroke
stroke = Stroke()


def char2features(sent, i):
    char = str(sent[i][0])
    zh_punctuation = ['，', '。', '！', '？', '“', '”', '‘', '’']
    features = ['bias',
                'char=' + char,
                'pinyin=' + ''.join(lazy_pinyin(char, errors='ignore')),
                'isalpha=' + str(char.isalpha()),
                'isdigit=' + str(char.isdigit()),
                'ispunct=' + str(char in string.punctuation or char in zh_punctuation),
                'isspace=' + str(char.isspace())]
    if '\u4e00' <= char <= '\u9fff':
        features.extend(['stroke=' + ''.join(stroke.get_info(char, 'stroke')),
                         'wubi=' + ''.join(stroke.get_info(char, 'wubi')),
                         'cangjie=' + ''.join(stroke.get_info(char, 'cangjie')),
                         'sijiao=' + ''.join(stroke.get_info(char, 'sijiao'))])
    if i > 0:
        char1 = str(sent[i-1][0])
        features.extend(['-1:char=' + char1,
                         '-0,1:char=' + char1 + char])
        if i > 1:
            char2 = str(sent[i-2][0])
            features.extend(['-2:char=' + char2,
                             '-1,2:char=' + char2 + char1,
                             '-0,1,2:char=' + char2 + char1 + char])
            if i < len(sent) - 1:
                features.extend(['2101:char=' + char2 + char1 + char + str(sent[i + 1][0])])
            if i < len(sent) - 2:
                features.extend(['21012:char=' + char2 + char1 + char + str(sent[i+1][0]) + str(sent[i+2][0])])
        if i < len(sent) - 1:
            features.extend(['101:char=' + char1 + char + str(sent[i+1][0])])
    if i < len(sent) - 1:
        char1 = str(sent[i+1][0])
        features.extend(['+1:char=' + char1,str(sent[i + 1][0]),
                         '+0,1:char=' + char + char1])
        if i < len(sent) - 2:
            char2 = str(sent[i+2][0])
            features.extend(['+2:char=' + char2,
                             '+1,2:char=' + char1 + char2,
                             '+0,1,2:char=' + char + char1 + char2])
            if i > 0:
                features.extend(['1012:char=' + str(sent[i - 1][0]) + char + char1 + char2])
    return features


def sent2features(sent, level):
    if level == 'word':
        return [word2features(sent, i) for i in range(len(sent))]
    if level == 'char':
        return [char2features(sent, i) for i in range(len(sent))]


def sent2labels(sent, level):
    if level == 'word':
        return [label for token, postag, label in sent]
    if level == 'char':
        return [label for char, label in sent]


def load_data(directory, level):
    sents = []
    filenames = os.listdir(directory)
    for filename in filenames:
        df = pd.read_csv(directory + filename)
        sent = []
        for index, row in df.iterrows():
            if level == 'word':
                sent.append((row['seq'], row['pos'], row['label']))
            elif level == 'char':
                sent.append((row['char'], row['label']))
        sents.append(sent)
    return sents


if __name__ == '__main__':
    level = 'char'

    print('Preparing train data ...')
    train_sents = load_data('./data/'+level+'_level_simplified_train_set/', level)
    x_train = [sent2features(s, level) for s in progressbar.progressbar(train_sents)]
    y_train = [sent2labels(s, level) for s in train_sents]

    del train_sents

    # 模型训练
    print('Training CRF model ...')
    model = pycrfsuite.Trainer(verbose=True)
    for xseq, yseq in zip(x_train, y_train):
        model.append(xseq, yseq)
    model.set_params({'c1': 1e-3,  # coefficient for L1 penalty
                      'c2': 1,  # coefficient for L2 penalty
                      'max_iterations': 500,  # stop earlier
                      # include transitions that are possible, but not observed
                      'feature.possible_transitions': True})
                      #'feature.minfreq': 3})
    model.train('./model/tianchi_ner_'+level+'_level.crfsuite')

    del x_train
    del y_train
