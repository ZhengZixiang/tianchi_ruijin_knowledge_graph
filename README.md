# 天池瑞金知识图谱初赛糖尿病相关命名实体识别
这是作为菜鸡的我们在[天池瑞金医院MMC人工智能辅助构建知识图谱大赛](https://tianchi.aliyun.com/competition/introduction.htm?spm=5176.11409106.5678.1.2ba15ecdqJDrOz&raceId=231687)初赛阶段的解决方案，排名只在20多到40多之间徘徊。

我们在初赛A榜阶段使用了传统CRF模型和BiLSTM+CRF模型，但由于没有GPU来改进，最终B榜提交结果用的是CRF模型的结果。B榜结果相对A榜下降了0.017左右，为0.73多。写个README做备忘。

### requirements
Python3

CRF模型：
- beautifulsoup
- codecs
- jieba==0.39
- pandas
- progressbar2==3.38.0
- python-crfsuite==0.9.6
- scikit-learn

BiLSTM+CRF模型
- keras==2.2.4
- git+https://www.github.com/keras-team/keras-contrib.git

### 数据分析与预处理
实体共12类，不同类别实体样本非常不平衡。训练数据人工标注太乱，并且存在同一实体存在不同标注人有不同标注标准的问题。我们并没有花太多的心思去做非常精细的预处理工作，主要完成的内容有：
- 针对ann文件中把跨行实体的多个起始位置，我们只保留开头和结束位置，中间分号全部删去，并另外存为csv文件。
- 再读取上述csv文件，对于词级别，用jieba.posseg进行分词和词性标注，并添加BIO标注，以csv格式存到`word_level_train_set` / `word_level_test_set`
- 对于字级别，包括\n在内都按单字切，添加BIO标注，以csv格式存到`char_level_train_set` / `char_level_test_set`

相关代码在`preprocessing.py`中实现。

### 模型构建
我们最后提交的结果是纯CRF做的。

#### CRF
我们的CRF模型使用了pycrfsuite封装的CRFSuite来训练。需要说明的事，传统CRF模型特别吃内存，对于Linux系统，训练我们这个模型至少要有16G内存。对于Windows系统建议20G以上。

首先对于BIO标注好的训练和测试文件，需要转化成CRFSuite的列表。

对于词级别，我们抽取到了3-gram词本身和词性作为特征模板给CRF训练，这是我们的baseline，只需要500轮迭代，训练四个小时左右，就可以实现0.72的分数。

对于字级别，我们抽取到了更多特征，包括5-gram，单字对应的拼音、笔划、五笔、仓颉码、四角码，以及是否数字、字母、标点和空白符等特征，可以实现接近0.74～0.75的分数。字级别的训练1000次迭代需要花费1天的时间。

上述字的笔划和编码信息，我们参考了[bamtercelboo/corpus_process_script](https://github.com/bamtercelboo/corpus_process_script)的笔划抓取实现，扩展了抓取五笔等编码信息。相关代码在`stroke`文件夹中实现

在初赛过程中，我们训练了多种参数组合的词级别、字级别CRF模型，发现CRF模型主要取决于正则化参数C1、正则化参数C2和迭代次数。不同的正则化参数组合可以显著影响模型训练效果和训练时间，我们发现C2比C1高模型效果更好。而迭代次数更多，虽然结果能更精确，但是由于初赛不是严格F1，所以并不是越高越好。

我们最后采用的参数设置如下：
- C1: 1e-3
- C2: 1
- max_iter: 10000

相关代码在`crfsuite_model.py`中实现。`evaluate.py`参考pycrfsuite的example。直接测试结果使用`submit.py`。由于天池代码审核需要，预处理－训练－测试一条龙放在了`main.ipynb`实现。

#### BiLSTM+CRF
这部分代码的预处理我们采用了类似conll格式，即用句号做断句，而CRF模型是不需要断句的。此外，由于\n和在读取过程中存在问题，而我们希望模型能识别出来\n是多余字符，因此我们的数据文件使用`sp`整体做单字和标签的分隔符，使用`end\n`整体做换行符，这样读取输入数据不会出错。

我们参考了别人的Keras实现，比较容易上手。模型结构主要是：
- Embedding层使用Gensim训练了150维cbow和150维skip-gram字向量做拼接，trainable设为True
- 第一层：Bidreactional CuDNNLSTM
- 第二层：双向CuDNNLSTM
- 第三层：两个卷积两个反卷积+BiGRU
- 最后一层：抽出上述三层的特征做拼接再用CRF输出，CRF使用[Keras Contrib](https://github.com/keras-team/keras-contrib)的实现。loss和accuracy都用默认的。

模型一次迭代要30个小时，只训练了三次迭代……由于很大一部分是参考别人的代码，这里就不放上来献丑了，效果是0.74~0.75。

推荐用Keras的同学利用CuDNNLSTM来加速训练。

#### 其他尝试
我们训练过一个BiLSTM把标注好的BIO文件灌给模型做文本生成，从而实现数据增强，但是……失败了，我们验证集F1效果不如只用原始训练集。而且文本生成特别耗时，就放弃了数据增强。

### 总结
最终有个中流水平已经很满意啦，我们没有GPU，而且实验室不做深度学习，没有能力和资本去做很好的深度学习建模，不过CRF特征选择选得好的话，不但训练时间不长，效果也还凑合，而且还是在语料这么差的情况下，能进复赛就足够了。
做初赛认识很多大佬，看了很多github和博客，让我学到了很多。就算只知道理论，敲一遍别人的代码，这种傻瓜学习方式能让自己很快上手一件工具。
