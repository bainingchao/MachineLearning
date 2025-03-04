# coding:utf8

import numpy as np
from numpy import *
import matplotlib
import matplotlib.pyplot as plt

'''一步步教你轻松学主成分分析PCA降维算法
Blog：https://bainingchao.github.io/
Date：2018年9月29日11:18:08
'''

'''加载数据集'''
def loadDataSet(fileName, delim='\t'):
    fr = open(fileName)
    stringArr = [line.strip().split(delim) for line in fr.readlines()]
    datArr = [list(map(float, line)) for line in stringArr]
    #注意这里和python2的区别，需要在map函数外加一个list（），否则显示结果为 map at 0x3fed1d0
    return mat(datArr)


'''pca算法
    方差：（一维）度量两个随机变量关系的统计量,数据离散程度，方差越小越稳定
    协方差： （二维）度量各个维度偏离其均值的程度
    协方差矩阵：（多维）度量各个维度偏离其均值的程度

    当 cov(X, Y)>0时，表明X与Y正相关(X越大，Y也越大；X越小Y，也越小。)
    当 cov(X, Y)<0时，表明X与Y负相关；
    当 cov(X, Y)=0时，表明X与Y不相关。

    cov协方差=[(x1-x均值)*(y1-y均值)+(x2-x均值)*(y2-y均值)+...+(xn-x均值)*(yn-y均值)]/(n-1)
    Args:
        dataMat   原数据集矩阵
        topNfeat  应用的N个特征
    Returns:
        lowDDataMat  降维后数据集
        reconMat     新的数据集空间
'''
def pca(dataMat, topNfeat=9999999):
    # 计算每一列的均值
    meanVals = mean(dataMat, axis=0)
    # print('meanVals', meanVals)
    # 每个向量同时都减去均值
    meanRemoved = dataMat - meanVals
    # print('meanRemoved=', meanRemoved)
    # rowvar=0，传入的数据一行代表一个样本，若非0，传入的数据一列代表一个样本
    covMat = cov(meanRemoved, rowvar=0)
    # eigVals为特征值， eigVects为特征向量
    eigVals, eigVects = linalg.eig(mat(covMat))
    # print('eigVals=', eigVals)
    # print('eigVects=', eigVects)

    # 对特征值，进行从小到大的排序，返回从小到大的index序号
    # 特征值的逆序就可以得到topNfeat个最大的特征向量
    eigValInd = argsort(eigVals)
    # print('eigValInd1=', eigValInd)
    # -1表示倒序，返回topN的特征值[-1到-(topNfeat+1)不包括-(topNfeat+1)]
    eigValInd = eigValInd[:-(topNfeat+1):-1]
    # print('eigValInd2=', eigValInd)
    # 重组 eigVects 最大到最小
    redEigVects = eigVects[:, eigValInd]
    # print('redEigVects=', redEigVects.T)

    # 将数据转换到新空间
    # print( "---", shape(meanRemoved), shape(redEigVects))
    lowDDataMat = meanRemoved * redEigVects
    reconMat = (lowDDataMat * redEigVects.T) + meanVals
    # print('lowDDataMat=', lowDDataMat)
    # print('reconMat=', reconMat)
    return lowDDataMat, reconMat



'''降维后的数据和原始数据可视化'''
def show_picture(dataMat, reconMat):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(dataMat[:, 0].flatten().A[0], dataMat[:, 1].flatten().A[0], marker='^', s=90,c='green')
    ax.scatter(reconMat[:, 0].flatten().A[0], reconMat[:, 1].flatten().A[0], marker='o', s=50, c='red')
    plt.show()



'''将NaN替换成平均值函数'''
def replaceNanWithMean():
    datMat = loadDataSet('./secom.data', ' ')
    numFeat = shape(datMat)[1]
    # 设置保留小数位
    np.set_printoptions(precision=2)
    for i in range(numFeat):
        # 对value不为NaN的求均值
        # .A 返回矩阵基于的数组
        meanVal = mean(datMat[nonzero(~isnan(datMat[:, i].A))[0], i])
        # 将value为NaN的值赋值为均值
        datMat[nonzero(isnan(datMat[:, i].A))[0],i] = meanVal
    return datMat

'''数值归一化：特征值转化为0-1之间：newValue = (oldValue-min)/(max-min)'''
def norm_dataset(dataset):
    minVals = dataset.min(0)  # 参数0是取得列表中的最小值，而不是行中最小值
    maxVals = dataset.max(0)
    ranges = maxVals - minVals
    normdataset = zeros(shape(dataset)) # 生成原矩阵一样大小的0矩阵

    m = dataset.shape[0]
    # tile:复制同样大小的矩阵
    molecular = dataset - tile(minVals,(m,1))  # 分子： (oldValue-min)
    Denominator = tile(ranges,(m,1))           # 分母：(max-min)
    normdataset = molecular / Denominator     # 归一化结果。

    # print('归一化的数据结果：\n'+str(normdataset))
    return normdataset,ranges,minVals

'''分析数据'''
def analyse_data(dataMat):
    meanVals = mean(dataMat, axis=0)
    meanRemoved = dataMat-meanVals
    covMat = cov(meanRemoved, rowvar=0)
    eigvals, eigVects = linalg.eig(mat(covMat))
    print(eigvals)
    eigValInd = argsort(eigvals)

    topNfeat = 20
    eigValInd = eigValInd[:-(topNfeat+1):-1]
    cov_all_score = float(sum(eigvals))
    sum_cov_score = 0
    for i in range(0, len(eigValInd)):
        line_cov_score = float(eigvals[eigValInd[i]])
        sum_cov_score += line_cov_score
        '''
        我们发现其中有超过20%的特征值都是0。
        这就意味着这些特征都是其他特征的副本，也就是说，它们可以通过其他特征来表示，而本身并没有提供额外的信息。

        最前面15个值的数量级大于10^5，实际上那以后的值都变得非常小。
        这就相当于告诉我们只有部分重要特征，重要特征的数目也很快就会下降。

        最后，我们可能会注意到有一些小的负值，他们主要源自数值误差应该四舍五入成0.
        '''
        print('主成分：%s, 方差占比：%s%%, 累积方差占比：%s%%' % (format(i+1, '2.0f'), format(line_cov_score/cov_all_score*100, '4.2f'), format(sum_cov_score/cov_all_score*100, '4.1f')))





if __name__ == "__main__":
    # 1 加载数据，并转化数据类型为float
    # dataMat = loadDataSet('./testSet.txt')
    # print(dataMat)

    # 2 主成分分析降维特征向量设置
    # lowDmat, reconMat = pca(dataMat, 1)
    # print(shape(lowDmat))
    # 只需要2个特征向量，和原始数据一致，没任何变化
    # lowDmat, reconMat = pca(dataMat, 2)
    # print(shape(lowDmat))

    # 3 将降维后的数据和原始数据一起可视化
    # show_picture(dataMat, reconMat)

    # 4 利用PCA对半导体制造数据降维
    dataMat = replaceNanWithMean()
    normdataset,ranges,minVals = norm_dataset(dataMat)
    print(list(normdataset))
    # 5 分析数据
    # analyse_data(dataMat)
    # lowDmat, reconMat = pca(dataMat, 20)
    # print(shape(lowDmat))
    # show_picture(dataMat, reconMat)
