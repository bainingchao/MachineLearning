# -*- coding:utf-8 -*-

from numpy import *
import feedparser

"""
p(xy)=p(x|y)p(y)=p(y|x)p(x)
p(x|y)=p(y|x)p(x)/p(y)
"""

'''-----------项目案例1: 屏蔽社区留言板的侮辱性言论----------------'''

'''创建数据集：单词列表postingList, 所属类别classVec'''
def loadDataSet():
    postingList = [['my', 'dog', 'has', 'flea', 'problems', 'help', 'please'],
                   ['maybe', 'not', 'take', 'him', 'to', 'dog', 'park', 'stupid'],
                   ['my', 'dalmation', 'is', 'so', 'cute', 'I', 'love', 'him'],
                   ['stop', 'posting', 'stupid', 'worthless', 'garbage'],
                   ['mr', 'licks', 'ate', 'my', 'steak', 'how', 'to', 'stop', 'him'],
                   ['quit', 'buying', 'worthless', 'dog', 'food', 'stupid']]
    classVec = [0, 1, 0, 1, 0, 1]  # 1代表侮辱性文字,0代表非侮辱文字
    return postingList, classVec



'''获取所有单词的集合:返回不含重复元素的单词列表'''
def createVocabList(dataSet):
    vocabSet = set([])
    for document in dataSet:
        vocabSet = vocabSet | set(document)  # 操作符 | 用于求两个集合的并集
    # print(vocabSet)
    return list(vocabSet)



'''词集模型构建数据矩阵'''
def setOfWords2Vec(vocabList, inputSet):
    # 创建一个和词汇表等长的向量，并将其元素都设置为0
    returnVec = [0] * len(vocabList)
    # 遍历文档中的所有单词，如果出现了词汇表中的单词，则将输出的文档向量中的对应值设为1
    for word in inputSet:
        if word in vocabList:
            returnVec[vocabList.index(word)] = 1
        else:
            print("单词: %s 不在词汇表之中!" % word)
    # print(returnVec)
    return returnVec



'''文档词袋模型构建数据矩阵'''
def bagOfWords2VecMN(vocabList, inputSet):
    returnVec = [0] * len(vocabList)
    for word in inputSet:
        if word in vocabList:
            returnVec[vocabList.index(word)] += 1
    # print(returnVec)
    return returnVec



'''朴素贝叶斯分类器训练函数'''
def _trainNB0(trainMatrix, trainCategory):
    numTrainDocs = len(trainMatrix) # 文件数
    numWords = len(trainMatrix[0]) # 单词数
    # 侮辱性文件的出现概率，即trainCategory中所有的1的个数，
    # 代表的就是多少个侮辱性文件，与文件的总数相除就得到了侮辱性文件的出现概率
    pAbusive = sum(trainCategory) / float(numTrainDocs)

    # 构造单词出现次数列表
    p0Num = zeros(numWords) # [0,0,0,.....]
    p1Num = zeros(numWords) # [0,0,0,.....]
    p0Denom = 0.0;p1Denom = 0.0 # 整个数据集单词出现总数
    for i in range(numTrainDocs):
        # 遍历所有的文件，如果是侮辱性文件，就计算此侮辱性文件中出现的侮辱性单词的个数
        if trainCategory[i] == 1:
            p1Num += trainMatrix[i] #[0,1,1,....]->[0,1,1,...]
            p1Denom += sum(trainMatrix[i])
        else:
            # 如果不是侮辱性文件，则计算非侮辱性文件中出现的侮辱性单词的个数
            p0Num += trainMatrix[i]
            p0Denom += sum(trainMatrix[i])
    # 类别1，即侮辱性文档的[P(F1|C1),P(F2|C1),P(F3|C1),P(F4|C1),P(F5|C1)....]列表
    # 即 在1类别下，每个单词出现次数的占比
    p1Vect = p1Num / p1Denom# [1,2,3,5]/90->[1/90,...]
    # 类别0，即正常文档的[P(F1|C0),P(F2|C0),P(F3|C0),P(F4|C0),P(F5|C0)....]列表
    # 即 在0类别下，每个单词出现次数的占比
    p0Vect = p0Num / p0Denom
    return p0Vect, p1Vect, pAbusive



'''训练数据优化版本'''
def trainNB0(trainMatrix, trainCategory):
    numTrainDocs = len(trainMatrix) # 总文件数
    numWords = len(trainMatrix[0]) # 总单词数
    pAbusive = sum(trainCategory) / float(numTrainDocs) # 侮辱性文件的出现概率
    # 构造单词出现次数列表,p0Num 正常的统计,p1Num 侮辱的统计
    # 避免单词列表中的任何一个单词为0，而导致最后的乘积为0，所以将每个单词的出现次数初始化为 1
    p0Num = ones(numWords)#[0,0......]->[1,1,1,1,1.....],ones初始化1的矩阵
    p1Num = ones(numWords)

    # 整个数据集单词出现总数，2.0根据样本实际调查结果调整分母的值（2主要是避免分母为0，当然值可以调整）
    # p0Denom 正常的统计
    # p1Denom 侮辱的统计
    p0Denom = 2.0
    p1Denom = 2.0
    for i in range(numTrainDocs):
        if trainCategory[i] == 1:
            p1Num += trainMatrix[i]  # 累加辱骂词的频次
            p1Denom += sum(trainMatrix[i]) # 对每篇文章的辱骂的频次 进行统计汇总
        else:
            p0Num += trainMatrix[i]
            p0Denom += sum(trainMatrix[i])
    # 类别1，即侮辱性文档的[log(P(F1|C1)),log(P(F2|C1)),log(P(F3|C1)),log(P(F4|C1)),log(P(F5|C1))....]列表,取对数避免下溢出或浮点舍入出错
    p1Vect = log(p1Num / p1Denom)
    # 类别0，即正常文档的[log(P(F1|C0)),log(P(F2|C0)),log(P(F3|C0)),log(P(F4|C0)),log(P(F5|C0))....]列表
    p0Vect = log(p0Num / p0Denom)
    return p0Vect, p1Vect, pAbusive



'''
朴素贝叶斯分类函数

将乘法转换为加法
乘法：P(C|F1F2...Fn) = P(F1F2...Fn|C)P(C)/P(F1F2...Fn)
加法：P(F1|C)*P(F2|C)....P(Fn|C)P(C) -> log(P(F1|C))+log(P(F2|C))+....+log(P(Fn|C))+log(P(C))

vec2Classify: 待测数据[0,1,1,1,1...]，即要分类的向量
p0Vec: 类别0，即正常文档的[log(P(F1|C0)),log(P(F2|C0)),log(P(F3|C0)),log(P(
        F4|C0)),log(P(F5|C0))....]列表
p1Vec: 类别1，即侮辱性文档的[log(P(F1|C1)),log(P(F2|C1)),log(P(F3|C1)),log(P(
        F4|C1)),log(P(F5|C1))....]列表
pClass1: 类别1，侮辱性文件的出现概率
返回：类别1 or 0
'''
def classifyNB(vec2Classify, p0Vec, p1Vec, pClass1):
    # 计算公式  log(P(F1|C))+log(P(F2|C))+....+log(P(Fn|C))+log(P(C))
    # 使用 NumPy 数组来计算两个向量相乘的结果，这里的相乘是指对应元素相乘，即先将两个向量中的第一个元素相乘，然后将第2个元素相乘，以此类推。这里的 vec2Classify * p1Vec 的意思就是将每个词与其对应的概率相关联起来
    p1 = sum(vec2Classify * p1Vec) + log(pClass1)
    p0 = sum(vec2Classify * p0Vec) + log(1.0 - pClass1)
    if p1 > p0:
        return 1
    else:
        return 0



'''朴素贝叶斯算法屏蔽社区留言板的侮辱性言论的应用'''
def testingNB():
    # 1. 加载数据集
    dataSet, Classlabels = loadDataSet()
    # 2. 创建单词集合
    myVocabList = createVocabList(dataSet)
    # 3. 计算单词是否出现并创建数据矩阵
    trainMat = []
    for postinDoc in dataSet:
        # 返回m*len(myVocabList)的矩阵， 记录的都是0，1信息
        trainMat.append(setOfWords2Vec(myVocabList, postinDoc))
    # print('test',len(array(trainMat)[0]))
    # 4. 训练数据
    p0V, p1V, pAb = trainNB0(array(trainMat), array(Classlabels))
    # 5. 测试数据
    testEntry = ['love', 'my', 'dalmation']
    thisDoc = array(setOfWords2Vec(myVocabList, testEntry))
    print(testEntry, '分类结果是: ', classifyNB(thisDoc, p0V, p1V, pAb))
    testEntry = ['stupid', 'garbage']
    thisDoc = array(setOfWords2Vec(myVocabList, testEntry))
    print(testEntry, '分类结果是: ', classifyNB(thisDoc, p0V, p1V, pAb))




'''---------------项目案例2: 使用朴素贝叶斯过滤垃圾邮件----------------'''

'''接收一个大字符串并将其解析为字符串列表'''
def textParse(bigString):
    import re
    # 使用正则表达式来切分句子，其中分隔符是除单词、数字外的任意字符串
    listOfTokens = re.split(r'\W*', bigString)
    return [tok.lower() for tok in listOfTokens if len(tok) > 2]



'''读取文本'''
def testParseTest():
    print(textParse(open('./email/ham/1.txt').read()))



'''对贝叶斯垃圾邮件分类器进行自动化处理。'''
def spamTest():
    docList = [];classList = [];fullText = [] # 文档列表、类别列表、文本特征
    for i in range(1, 26): # 总共25个文档
        # 切分，解析数据，并归类为 1 类别
        wordList = textParse(open('./email/spam/%d.txt' % i).read())
        docList.append(wordList)
        classList.append(1)
        # 切分，解析数据，并归类为 0 类别
        wordList = textParse(open('./email/ham/%d.txt' % i,encoding='UTF-8').read())
        docList.append(wordList)
        classList.append(0)
        fullText.extend(wordList)
    # 创建词汇表
    vocabList = createVocabList(docList)
    trainingSet = list(range(50)) # 词汇表文档索引
    testSet = []
    # 随机取 10 个邮件用来测试
    for i in range(10):
        # random.uniform(x, y) 随机生成一个范围为 x - y 的实数
        randIndex = int(random.uniform(0, len(trainingSet)))
        testSet.append(trainingSet[randIndex]) # 随机抽取测试样本
        del(trainingSet[randIndex]) # 训练集中删除选择为测试集的文档

    trainMat = [];trainClasses = [] # 训练集合训练标签
    for docIndex in trainingSet:
        trainMat.append(setOfWords2Vec(vocabList, docList[docIndex]))
        trainClasses.append(classList[docIndex])

    p0V, p1V, pSpam = trainNB0(array(trainMat), array(trainClasses))
    errorCount = 0
    for docIndex in testSet:
        wordVector = setOfWords2Vec(vocabList, docList[docIndex])
        if classifyNB(array(wordVector), p0V, p1V, pSpam) != classList[docIndex]:
            errorCount += 1
    print('the errorCount is: ', errorCount)
    print('the testSet length is :', len(testSet))
    print('the error rate is :', float(errorCount)/len(testSet))




# -----------项目案例3: 使用朴素贝叶斯从个人广告中获取区域倾向------------

'''正则切词'''
def textParse(bigString):
    import re
    # 匹配字母或数字或下划线或汉字 等价于
    listOfTokens=re.split(r'\W*',bigString)
    return [tok.lower() for tok in listOfTokens if len(tok)>2]


'''RSS源分类器及高频词去除函数'''
def calcMostFreq(vocabList,fullText):
    import operator
    freqDict={}
    for token in vocabList:  #遍历词汇表中的每个词
        freqDict[token]=fullText.count(token)  #统计每个词在文本中出现的次数
    sortedFreq=sorted(freqDict.items(),key=operator.itemgetter(1),reverse=True)  #根据每个词出现的次数从高到底对字典进行排序
    return sortedFreq[:30]   #返回出现次数最高的30个单词



def localWords(feed1,feed0):
    # import feedparser # feedparser是python中最常用的RSS程序库
    docList=[];classList=[];fullText=[]
    minLen=min(len(feed1['entries']),len(feed0['entries'])) # entries内容无法抓取，网站涉及反爬虫技术
    print(len(feed1['entries']),len(feed0['entries']))
    for i in range(minLen):
        wordList=textParse(feed1['entries'][i]['summary'])   #每次访问一条RSS源
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(1)
        wordList=textParse(feed0['entries'][i]['summary'])
        docList.append(wordList)
        fullText.extend(wordList)
        classList.append(0)
    vocabList=createVocabList(docList)
    top30Words=calcMostFreq(vocabList,fullText)
    for pairW in top30Words:
        if pairW[0] in vocabList:vocabList.remove(pairW[0])    #去掉出现次数最高的那些词
    trainingSet=range(2*minLen);testSet=[]
    for i in range(20):
        randIndex=int(random.uniform(0,len(trainingSet)))
        testSet.append(trainingSet[randIndex])
        del(trainingSet[randIndex])
    trainMat=[];trainClasses=[]
    for docIndex in trainingSet:
        trainMat.append(bagOfWords2VecMN(vocabList,docList[docIndex]))
        trainClasses.append(classList[docIndex])
    p0V,p1V,pSpam=trainNB0(array(trainMat),array(trainClasses))
    errorCount=0
    for docIndex in testSet:
        wordVector=bagOfWords2VecMN(vocabList,docList[docIndex])
        if classifyNB(array(wordVector),p0V,p1V,pSpam)!=classList[docIndex]:
            errorCount+=1
    print('the error rate is:',float(errorCount)/len(testSet))
    return vocabList,p0V,p1V


# 最具表征性的词汇显示函数
def getTopWords(ny,sf):
    import operator
    vocabList,p0V,p1V=localWords(ny,sf)
    topNY=[];topSF=[]
    for i in range(len(p0V)):
        if p0V[i]>-6.0:topSF.append((vocabList[i],p0V[i]))
        if p1V[i]>-6.0:topNY.append((vocabList[i],p1V[i]))
    sortedSF=sorted(topSF,key=lambda pair:pair[1],reverse=True)
    print("SF**SF**SF**SF**SF**SF**SF**SF**SF**SF**SF**SF**SF**SF**")
    for item in sortedSF:
        print(item[0])
    sortedNY=sorted(topNY,key=lambda pair:pair[1],reverse=True)
    print("NY**NY**NY**NY**NY**NY**NY**NY**NY**NY**NY**NY**NY**NY**")
    for item in sortedNY:
        print(item[0])






if __name__ == "__main__":
    # 1 打印数据集和标签
    # dataSet,Classlabels = loadDataSet()
    # print(dataSet,'\n',Classlabels)

    # 2 获取所有单词的集合
    # vocabList=createVocabList(dataSet)
    # print(vocabList)

    # 3 文本转化为向量
    # setOfWords2Vec(vocabList, dataSet[0]) # 单句文本向量转化
    # bagOfWords2VecMN(vocabList, dataSet[0])
    # 文本向量转化
    # trainMatrix = []
    # for postinDoc in dataSet:
    #     trainMatrix.append(setOfWords2Vec(vocabList,postinDoc))
    # print(trainMatrix,'\n',Classlabels)

    # 4.1 朴素贝叶斯分类器训练函数
    # p0V,p1V,pAb=_trainNB0(trainMatrix,Classlabels)
    # print(p0V,'\n',p1V,'\n',pAb)

    # 4.2训练数据优化版本
    # p0V,p1V,pAb=trainNB0(trainMatrix, Classlabels)
    # print(p0V,'\n',p1V,'\n',pAb)

    # 5 测试朴素贝叶斯算法
    # testingNB()

    # 6 正则切词
    # bigString = 'This book is the best book on python or M.L. I have ever laid eyes upon.'
    # textParse(bigString)
    # testParseTest()

    # 7 对贝叶斯垃圾邮件分类器进行自动化处理。
    spamTest()

    # 8 使用朴素贝叶斯从个人广告中获取区域倾向
    ny = feedparser.parse('http://newyork.craigslist.org/stp/index.rss')
    sf = feedparser.parse('http://sfbay.craigslist.org/stp/index.rss')
    # print(ny)
    vocabList,pSF,pNY=localWords(ny,sf)
