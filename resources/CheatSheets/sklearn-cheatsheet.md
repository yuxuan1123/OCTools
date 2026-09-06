---
title: Scikit-learn 速查表
description: 这里列出了 scikit-learn 最重要且最实用的方法和函数。
created: 2022-10-31
---

<a id="table-of-contents"></a>
## 目录

- [面向开发者的 Scikit-learn 速查表](#scikit-learn-cheatsheet-for-developers)
  - [训练集、验证集与测试集](#training-validation-and-test-sets)
  - [预处理](#preprocessing)
  - [建模](#modeling)
    - [监督学习](#supervised-learning)
      - [`线性回归`](#linear-regression)
      - [`逻辑回归`](#logistic-regression)
      - [`支持向量机`](#support-vector-machines)
      - [`朴素贝叶斯`](#naive-bayes)
      - [`KNN`](#knn)
      - [`决策树`](#decision-tree)
      - [`梯度提升`](#gradient-boosting)
      - [`随机森林`（袋装决策树）](#random-forest-bagged-decision-trees)
    - [无监督学习](#unsupervised-learning)
      - [`PCA`](#pca)
      - [`k-Means 聚类`](#k-means-clustering)
  - [补充说明](#additional-notes)
    - [决策树提升](#decision-tree-boosting)
    - [交叉验证与网格搜索](#cross-validation-and-grid-search)

<a id="scikit-learn-cheatsheet-for-developers"></a>
# 面向开发者的 Scikit-learn 速查表

<a id="training-validation-and-test-sets"></a>
## 训练集、验证集与测试集

> [train_test_split](http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html) - [scikit-learn.org](https://scikit-learn.org/stable/)

```python
from sklearn.model_selection import train_test_split
x_trn, x_other, y_trn, y_other = train_test_split(x, y, train_size=0.7, random_state=0)
x_val, x_tst, y_val, y_tst = train_test_split(x_other, y_other, test_size=0.33, random_state=1)
```

**[🔼Back to Top](#table-of-contents)**

<a id="preprocessing"></a>
## 预处理

> 对于许多机器学习模型，各种预处理技术不仅有助于提高效率，往往对确保获得有意义的结果也很重要。

- [StandardScaler](http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html)（即 Z-score）
- [Normalizer](http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.Normalizer.html)（向量归一化）
- [Binarizer](http://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.Binarizer.html)
典型流程如下：
  1. 选择合适的预处理方法并导入它
  2. 仅通过对训练集拟合所选方法来构造缩放对象！
  3. 使用构造好的缩放对象对训练集、验证集和测试集进行变换。

```python
# Example:  Standarization / Z Scoring
#   -- the procedure is the same for Normalizer and Binarizer
from sklearn.preprocessing import StandardScaler
rescale = StandardScalar.fit(x_trn)
xx_trn = rescale.transform(x_trn)
xx_val = rescale.transform(x_val)
xx_tst = rescale.transform(x_tst)
```

**[🔼Back to Top](#table-of-contents)**

<a id="modeling"></a>
## 建模

> Scikit-Learn 让建模变得非常简单。其步骤如下：

1. 构造
2. 拟合
3. 预测
4. 评估

在接下来的小节中，我们介绍前 3 个步骤。模型评估将在下一节介绍。

**[🔼Back to Top](#table-of-contents)**

<a id="supervised-learning"></a>
### 监督学习

<a id="linear-regression"></a>
#### `线性回归`

> [函数文档](http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)

```python
from skearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(xx_trn, y_tr)
y_pred = model.predict(xx_val)
```

**[🔼Back to Top](#table-of-contents)**

<a id="logistic-regression"></a>
#### `逻辑回归`

> [函数文档](http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)

```python
from skearn.linear_model import LogisticRegression
model = LogisticRegression()
model.fit(xx_trn, y_tr)
y_pred = model.predict(xx_val)
```

**[🔼Back to Top](#table-of-contents)**

<a id="support-vector-machines"></a>
#### `支持向量机`

> [文档](http://scikit-learn.org/stable/modules/svm.html)

```python
from skearn.svm import SVC
model = SVC(kernel='linear') # other kernels: polynomial, rbf, sigmoid
model.fit(xx_trn, y_tr)
y_pred = model.predict(xx_val)
```

**[🔼Back to Top](#table-of-contents)**

<a id="naive-bayes"></a>
#### `朴素贝叶斯`

```python
from skearn.naive_bayes import GaussianNB
model = GaussianNB()
model.fit(xx_trn, y_tr)
y_pred = model.predict(xx_val)
```

**[🔼Back to Top](#table-of-contents)**

<a id="knn"></a>
#### `KNN`

```python
from skearn.neighbors import KNeighborsClassifier
model = KNeighborsClassifier(n_neighbors=3)
model.fit(xx_trn, y_tr)
y_pred = model.predict(xx_val)
```

**[🔼Back to Top](#table-of-contents)**

<a id="decision-tree"></a>
#### `决策树`

```python
from skearn.tree import DecisionTreeClassifier
model = DecisionTreeClassifier(criterion='entropy', max_depth=10, random_state=0)
model.fit(x_trn, y_tr)  # Vars do not have to be normalized/standardized for DTs!
y_pred = model.predict(x_val)
```

**[🔼Back to Top](#table-of-contents)**

<a id="gradient-boosting"></a>
#### `梯度提升`

```python
from skearn.ensemble import GradientBoostinClassifier
model = GradientBoostinClassifier(max_depth=5, n_estimators=1000, 
  subsample=0.5, random_state=0, learning_rate=0.001)
model.fit(x_trn, y_tr)  # Vars do not have to be normalized/standardized for DTs!
y_pred = model.predict(x_val)
```

**[🔼Back to Top](#table-of-contents)**

<a id="random-forest-bagged-decision-trees"></a>
#### `随机森林`（袋装决策树）

```python
from skearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=1000, criterion='entropy', 
   n_jobs=4, max_depth=10)
model.fit(x_trn, y_tr)  # Vars do not have to be normalized/standardized for DTs!
y_pred = model.predict(x_val)
```

**[🔼Back to Top](#table-of-contents)**

<a id="unsupervised-learning"></a>
### 无监督学习

<a id="pca"></a>
#### `PCA`

```python
from skearn.decomposition import PCA
model = PCA(n_components=0.95)
model.fit(xx_trn, y_tr)
#y_pred = model.predict(xx_val)
```

**[🔼Back to Top](#table-of-contents)**

<a id="k-means-clustering"></a>
#### `k-Means 聚类`

```python
from skearn.cluster import KMeans
model = KMeans(n_clusters=3, random_state=1)
model.fit(xx_trn, y_tr)
#y_pred = model.predict(xx_val)
```

**[🔼Back to Top](#table-of-contents)**

---------------------------------------------

<a id="additional-notes"></a>
## 补充说明

<a id="decision-tree-boosting"></a>
### 决策树提升

> 这基本上就是正在发生的事情……

```python
from skearn.tree import DecisionTreeClassifier
model = DecisionTreeClassifier(max_depth=2, random_state=0)
N_estimators = 3
for i in range(N_estimators):
  model.fit(x_trn, y_trn)  
  y_res = y_trn - model.predict(x_trn)
y_pred = y_res
```

**[🔼Back to Top](#table-of-contents)**

<a id="cross-validation-and-grid-search"></a>
### 交叉验证与网格搜索

- [StratifiedKFold](http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html)
- [GridSearchCV](http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html)

```python
#from sklearn.cross_validation import StratifiedKFold
from sklearn.grid_search import GridSearchCV
###
#skf = StratifiedKFold(n_splits=2)
model_type = GradientBoostingClassifier(n_estimators=500, learning_rate=.01)
params = {"max_depth": [3, 5, 7]}
###
model = GridSearchCV(model_type, param_grid=params, verbose=2)
model.fit(x_trn, y_trn)
```

**[🔼Back to Top](#table-of-contents)**
