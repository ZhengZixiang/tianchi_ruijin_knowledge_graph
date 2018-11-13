# -*- coding: utf-8 -*-
import os
import codecs
import progressbar
from stroke.character_stroke_handian import Stroke


def analysis_stoke_corpus(directory):
    filenames = os.listdir(directory)
    stroke = Stroke()
    for filename in progressbar.progressbar(filenames):
        if filename.endswith('.txt'):
            f = codecs.open(directory + filename, 'r')
            text = f.read()
            f.close()
            for c in text:
                if '\u4e00' <= c <= '\u9fff':
                    stroke.get_info(c, 'stroke')
                    stroke.get_info(c, 'wubi')
                    stroke.get_info(c, 'cangjie')
                    stroke.get_info(c, 'zheng')
                    stroke.get_info(c, 'sijiao')
