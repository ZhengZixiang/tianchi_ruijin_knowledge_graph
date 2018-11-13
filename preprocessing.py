# -*- coding: utf-8 -*-
import os
import codecs
import jieba
import pandas as pd
import jieba.posseg as pseg


def clean_ann():
    directory = './data/train/'
    filenames = os.listdir(directory)
    for filename in filenames:
        entity_list = []
        label_list = []
        start_list = []
        end_list = []
        if filename.endswith('.ann'):
            for line in codecs.open(directory + filename):
                tab_split = line.strip().split('\t')
                space_split = tab_split[1].split()
                entity = tab_split[2].replace(' ', '')  # replace是去除entity不干净的空格
                label = space_split[0]
                start = space_split[1]
                end = space_split[-1]

                entity_list.append(entity)
                label_list.append(label)
                start_list.append(int(start))
                end_list.append(end)

            df = pd.DataFrame({'entity': entity_list, 'label': label_list, 'start': start_list, 'end': end_list})
            df.to_csv('./data/train/' + filename[:-4] + '.csv')


def word_level_tag2(filename):
    f = codecs.open(filename)

    # 分词
    words, flags = [], []
    for word, flag in jieba.posseg.cut(f.read()):
        words.append(word)
        flags.append(flag)
    f.close()

    df = pd.read_csv(filename[:-4] + '.csv')
    df = df.sort_values(by='start', axis=0, ascending=True)

    # 加上词级别标签
    seq, pos, label = [], [], []
    text_length = 0
    i = 0
    j = 0
    tag = 'O'
    while i < len(words) and j < df.shape[0]:
        if text_length < df.iloc[j]['start']:
            seq.append(words[i])
            pos.append(flags[i])
            label.append('O')
        elif text_length == df.iloc[j]['start'] and df.iloc[j]['end'] >= text_length + len(words[i]):
            seq.append(words[i])
            pos.append(flags[i])
            tag = 'B'
            label.append(tag + '-' + df.iloc[j]['label'])
        else:
            seq.append(words[i])
            pos.append(flags[i])
            tag = 'I'
            label.append(tag + '-' + df.iloc[j]['label'])
        text_length += len(words[i])
        i += 1
        if text_length >= df.iloc[j]['end']:
            j += 1

    while i < len(words):
        seq.append(words[i])
        pos.append(flags[i])
        label.append('O')
        i += 1

    return seq, pos, label


def word_level_tag(filename):
    f = codecs.open(filename)

    # 分词
    words, flags = [], []
    for word, flag in jieba.posseg.cut(f.read()):
        words.append(word)
        flags.append(flag)
    f.close()

    df = pd.read_csv(filename[:-4] + '.csv')
    df = df.sort_values(by='start', axis=0, ascending=True)

    # 加上词级别标签
    seq, pos, label = [], [], []
    text_length = 0
    i = 0
    j = 0
    tag = 'O'
    while i < len(words) and j < df.shape[0]:
        if text_length + len(words[i]) <= df.iloc[j]['start']:
            seq.append(words[i])
            pos.append(flags[i])
            label.append('O')
        elif text_length < df.iloc[j]['start'] and df.iloc[j]['start'] >= text_length + len(words[i]):
            prefix = words[i][:df.iloc[j]['start'] - text_length]
            suffix = words[i][df.iloc[j]['start'] - text_length:]
            seq.append(prefix)
            pos.append(flags[i])
            tag = 'O'
            label.append(tag)
            seq.append(suffix)
            pos.append(flags[i])
            tag = 'B'
            label.append(tag + '-' + df.iloc[j]['label'])
        elif text_length == df.iloc[j]['start'] and df.iloc[j]['end'] >= text_length + len(words[i]):
            seq.append(words[i])
            pos.append(flags[i])
            tag = 'B'
            label.append(tag + '-' + df.iloc[j]['label'])
        elif text_length > df.iloc[j]['start'] and df.iloc[j]['end'] >= text_length + len(words[i]):
            seq.append(words[i])
            pos.append(flags[i])
            tag = 'I'
            label.append(tag + '-' + df.iloc[j]['label'])
        elif text_length < df.iloc[j]['end'] and df.iloc[j]['end'] < text_length + len(words[i]):
            prefix = words[i][:df.iloc[j]['end'] - text_length]
            suffix = words[i][df.iloc[j]['end'] - text_length:]
            seq.append(prefix)
            pos.append(flags[i])
            tag = 'I'
            label.append(tag + '-' + df.iloc[j]['label'])
            seq.append(suffix)
            pos.append(flags[i])
            tag = 'O'
            label.append(tag)
        text_length += len(words[i])
        i += 1
        if text_length >= df.iloc[j]['end']:
            j += 1

    while i < len(words):
        seq.append(words[i])
        pos.append(flags[i])
        label.append('O')
        i += 1

    return seq, pos, label


def char_level_tag(filename):
    raw = codecs.open(filename)
    csv = pd.read_csv(filename[:-4] + '.csv').sort_values('start')
    # 字级别不需要分词
    chars = list(raw.read())
    raw.close()
    i = 0
    label = []
    for index, row in csv.iterrows():
        while i < len(chars):
            if i < row['start']:
                label.append('O')
                i += 1
            elif i == row['start']:
                label.append('B-' + row['label'])
                i += 1
            elif row['start'] < i < row['end']:
                label.append('I-' + row['label'])
                i += 1
            elif i >= row['end']:
                break
    while i < len(chars):
        label.append('O')
        i += 1
    return chars, label


def sort():
    filenames = os.listdir('./data/train/')
    for filename in filenames:
        if filename.endswith('.csv'):
            df = pd.read_csv('./data/train/' + filename)
            df = df.sort_values(by='start')
            df.to_csv('./data/sorted_raw_train/' + filename, index=False)


def generate_word_level_train_set():
    directory = './data/train/'
    filenames = os.listdir(directory)

    for filename in filenames:
        if filename.endswith('.txt'):
            seq, pos, label = word_level_tag(directory + filename)
            df = pd.DataFrame(data={'seq': seq, 'pos': pos, 'label': label})
            df.to_csv('./data/word_level_train_set/' + filename[:-4] + '.csv', index=False)


def generate_word_level_test_set():
    directory = './data/test_b/'
    filenames = os.listdir(directory)
    for filename in filenames:
        if filename.endswith('.txt'):
            f = codecs.open(directory + filename, 'r')
            words = []
            flags = []
            for word, flag in jieba.posseg.cut(f.read()):
                words.append(word)
                flags.append(flag)
            df = pd.DataFrame(data={'seq': words, 'pos': flags})
            df.to_csv('./data/word_level_test_set/' + filename[:-4] + '.csv', index=False)
            f.close()


def generate_char_level_train_set():
    directory = './data/train/'
    filenames = os.listdir(directory)
    for filename in filenames:
        if filename.endswith('.txt'):
            chars, label = char_level_tag(directory + filename)
            df = pd.DataFrame(data={'char': chars, 'label': label})
            df.to_csv('./data/char_level_train_set/' + filename[:-4] + '.csv', index=False)


def generate_char_level_test_set():
    directory = './data/test_b/'
    filenames = os.listdir(directory)
    for filename in filenames:
        if filename.endswith('.txt'):
            f = codecs.open(directory + filename, 'r')
            df = pd.DataFrame(data={'char': list(f.read())})
            df.to_csv('./data/char_level_test_set/' + filename[:-4] + '.csv', index=False)
            f.close()


def conll_format():
    directory = './data/train/'
    filenames = os.listdir(directory)
    conll_file = codecs.open('./data/char.conll', 'w')
    for filename in filenames:
        if filename.endswith('.txt'):
            chars, label = char_level_tag(directory + filename)
            for i in range(len(chars)):
                conll_file.write(str(chars[i]) + 'sp' + label[i] + 'end\n')
                if chars[i] == '。' or chars[i] == ';' or chars[i] == '，':
                    conll_file.write('end\n')
    conll_file.close()


if __name__ == '__main__':
    print('Cleaning annotation files and saving as csv files ...')
    # clean_ann()
    print('Sorting csv file by column start ...')
    # sort()
    print('Adding word level B/O/I tag for named entity recognition ...')
    # generate_word_level_train_set()
    # generate_word_level_test_set()
    print('Adding char level B/O/I tag for named entity recognition ...')
    # generate_char_level_train_set()
    generate_char_level_test_set()
    print('Merging train files ...')
    # conll_format()
