# -*- coding: utf-8 -*-
import os
import pandas as pd
import pycrfsuite

from crfsuite_model import sent2features

from itertools import chain
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelBinarizer


def ner_report(y_true, y_pred):
    lb = LabelBinarizer()
    y_true_combined = lb.fit_transform(list(chain.from_iterable(y_true)))
    y_pred_combined = lb.fit_transform(list(chain.from_iterable(y_pred)))

    tagset = set(lb.classes_) - {'O'}
    tagset = sorted(tagset, key=lambda tag: tag.split('-', 1)[::-1])
    class_indices = {cls: idx for idx, cls in enumerate(lb.classes_)}

    return classification_report(y_true_combined, y_pred_combined,
                                 labels=[class_indices[cls] for cls in tagset],
                                 target_names=tagset)


if __name__ == '__main__':
    level = 'char'
    tagger = pycrfsuite.Tagger()
    tagger.open('./model/tianchi_ner_char_level_stroke.crfsuite')

    filenames = os.listdir('./dataset/'+level+'_level_val_set/')
    y_pred = []
    y_true = []
    for filename in filenames:
        sent_pred = []
        sent_true = []
        df_pred = pd.read_csv('./dataset/'+level+'_level_val_set/' + filename)
        df_true = pd.read_csv('./dataset/'+level+'_level_train_set/' + filename)
        for index, row in df_pred.iterrows():
            if level == 'word':
                sent_pred.append((row['seq'], row['pos']))
            elif level == 'char':
                sent_pred.append((row['char']))
        x_pred = sent2features(sent_pred, level)
        y_pred.append(tagger.tag(x_pred))
        sent_true.append(row['label'])
        y_true.append(sent_true)

    print(ner_report(y_true, y_pred))
