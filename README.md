# winemage-data数据集关联规则挖掘报告

姓名：刘张敏

学号：3220180832

## 一、数据预处理&格式转换

预处理部分代码：[preprocess.py](https://github.com/amazingcosmos/DM-course-AssociationRule/blob/master/code/preprocess.py)

原始数据格式如下图所示：

![图1 原始数据](./image/original_data.png)

数据由10列特征组成，分别代表country、description、designation、points、price
、province、region_1、region_2、variety、winery。除了points和price为数值属性，其他属性都是标称属性，所以考虑将points和price转换为同为标称属性的范围。在实验中选取points=90、80为临界点，高于90为high，低于90高于80为low；选取price=100、200为临界点，低于100为cheap，高于200为expensive，之间为normal。

对这10个属性标号为1-10，以country、points、price、province为关联属性得到处理后的适合关联规则挖掘的数据形式，如下图所示，其中每行代表一条transaction。

![图2 处理后数据](./image/preprocessed_data.png)

## 二、频繁项集挖掘

使用Apriori算法寻找频繁项集。

首先定义支持度S和置信度C的计算公式如下，其中sigma代表计数值，N为transaction总数。

![图3 支持度公式](./image/fomular_support.png)

![图4 置信度公式](./image/fomular_confident.png)

根据先验(apriori)原理：如果一个项集是频繁的，则的所有子集一定是频繁的。若某项集是非频繁的，则其所有的超级也一定是非频繁的。根据给定的置信度0.2，依次找出1-频繁项集、2-频繁项集等等。Apriori算法代码：[apriori.py](https://github.com/amazingcosmos/DM-course-AssociationRule/blob/master/code/apriori.py)中包含数据加载函数load_dataset、生成候选k-频繁项集函数create_c1和create_ck、计算支持度函数calc_surpport、Apriori算法函数apriori等。算法流程图如下：

![图5 Apriori算法生成频繁项集](./image/apriori_frequent_set.jpg)

## 三、导出关联规则，计算支持度和置信度

导出关联规则部分也是使用apriori算法，如果一条规则是低置信度的，则它的子代都是低置信度的。利用这个原则可以进行剪枝，快速生成规则。实现了规则生成算法gen_rules、置信度及支持度计算函数exam_rule等。算法流程图如下：

![图6 Apriori算法生成关联规则](./image/apriori_gen_rules.jpg)

最终生成规则列表rules，其中每项都是一个字典，包含五项内容。代表一条满足给定置信度0.6的规则及其对应的支持度、置信度、提升度。

| 属性名称 | 类型 | 解释 |
| -------- | ---- | ---- |
| lhs | list | 规则的前件 |
| rhs | list | 规则的后件 |
| support | float | 支持度值 |
| confident | float | 置信度值 |
| lift | float | 提升度值 |

其中提升度lift的计算公式为：

![图7 提升度公式](./image/fomular_lift.png)

## 四、去除冗余规则

满足置信度和支持度的规则一共有**66300**条，但是其中有很多冗余，定义冗余是：如果rule_a的lhs和rhs是包含于rule_b的，而且rule_a的lift小于或者等于rule_b，则称rule_a是rule_b的冗余规则。随后执行对冗余规则的删除操作，生成强规则strong_rules。

[association_rule.py](https://github.com/amazingcosmos/DM-course-AssociationRule/blob/master/code/association_rule.py)实现了调用Apriori算法，生成频繁项集，生成规则并去除冗余规则的操作。执行完成后，还剩余**55**条规则。

## 五、可视化

采用散点图的方式，对去除冗余后的55条规则进行可视化。

[association_rule.py](https://github.com/amazingcosmos/DM-course-AssociationRule/blob/master/code/association_rule.py)调用的pandas库中的预设绘图函数，将规则字典转换为DataFrame数据，然后使用DataFrame.plot.scatter()方法绘制散点图如下所示。图中横坐标为规则的支持度，纵轴为规则的置信度，圆点颜色的深浅代表提升度。其中颜色越深表示提升度越大。

![图8 散点图](./image/rules_scatter.jpg)

## 六、结果分析

如果选择支持度大于2作为筛选条件，在去除冗余后的规则中，共有**12090**条规则属于强规则。

部分规则如下：

| 规则 | 提升度lift | 支持度support | 置信度confident |
| ---- | :--------: | :-----------: | :-------------: |
| US --> high, normal, California | 4.14 | 0.24 | 1.0 |
| US, California --> high, normal | 4.14 | 0.24 | 1.0 |
| US, Oregon --> high, normal | 4.14 | 0.24 | 1.0 |
| US, Washington --> high, normal | 4.14 | 0.24 | 1.0 |
| US, Oregon, normal --> high | 4.14 | 0.24 | 1.0 |
| US, California, high --> normal | 4.14 | 0.24 | 1.0 |
| Italy, Northeastern Italy, high --> cheap | 4.14 | 0.24 | 1.0 |
| Italy, Tuscany --> high, cheap | 4.14 | 0.24 | 1.0 |
| Italy, Tuscany, cheap --> high | 4.14 | 0.24 | 1.0 |
| Italy, Rhône Valley --> high, cheap | 4.14 | 0.24 | 1.0 |
| Spain, Levante --> high, cheap | 3.0 | 0.25 | 1.0 |
| Spain, Levante --> high, normao | 3.0 | 0.25 | 1.0 |
| Spain, Northern Spain --> low, cheap | 3.0 | 0.25 | 0.75 |

可以看到，当提升度相同时，有很多规则仍然是重复的，表示这个国家某些地区同时产酒的概率很大。


