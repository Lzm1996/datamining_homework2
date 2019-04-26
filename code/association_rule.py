#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib
matplotlib.style.use('ggplot')

import apriori
import preprocess

DATA_FILE = '../data/diagnosis.data'
OUTPUT_FILE = '../data/diagnosis.csv'
MIN_SUPPORT = 0.2
MIN_CONFIDENT = 0.6
MIN_LIFT = 3.0

# prepocess the original data file
preprocess.preprocess(DATA_FILE, OUTPUT_FILE)

# get the data_set from .csv file
data_set = apriori.load_dataset(OUTPUT_FILE)

# get frequent items and their support value
f, f_support = apriori.apriori(data_set, MIN_SUPPORT)

# generate the rules
rules = apriori.gen_rules(f, f_support, MIN_CONFIDENT, MIN_LIFT)

# discard duplicate rules
# if rule A's lhs and rhs is the subset of rule B's
# and rule A's lift is less than B's
discard_rules = []
for i in range(len(rules)):
    rule_a = rules[i]
    for j in range(len(rules)):
        if i == j or i in discard_rules or j in discard_rules:
            continue
        rule_b = rules[j]
        if(rule_a['lhs'].issubset(rule_b['lhs']) and rule_a['rhs'].issubset(rule_b['rhs']) and rule_a['lift'] <= rule_b['lift']):
            # print rule_a, '\n', rule_b, '\n\n'
            discard_rules.append(i)
# remove the duplicate rules and stroe the rest rules into 'strong_rules'
strong_rules = []
for i in range(len(rules)):
    if i not in discard_rules:
        strong_rules.append(rules[i])

# build up the DataFrame of strong rules
df_strong_rules = pd.DataFrame(strong_rules)

# plot the scatter figure
plot = df_strong_rules.plot.scatter(x = 'support', y = 'confident', c = 'lift', s = 100)
fig = plot.get_figure()
fig.savefig('../image/rules_scatter.jpg')

df_strong_rules = df_strong_rules.sort_values(by = 'lift', ascending = False)
df_strong_rules = df_strong_rules.reset_index(drop = True)
names = {1:'发烧', 2:'恶心', 3:'腰疼', 4:'连续排尿', 5:'排尿疼痛', 6:'尿道肿胀', 7:'膀胱炎症', 8:'肾炎'}

# filter by lift
counter = 0
for i in range(len(df_strong_rules)):
    rule = df_strong_rules.iloc[i]
    if rule['lift'] > 2.0:
        lhs_index = []
        for item in rule['lhs']:
            lhs_index.append(names[item])
        lhs = ', '.join(lhs_index)
        
        rhs_index = []
        for item in rule['rhs']:
            rhs_index.append(names[item])
        rhs = ', '.join(rhs_index)
        lift = round(rule['lift'], 2)
        support = round(rule['support'], 2)
        confident = round(rule['confident'], 2)
        print '%s \t %s \t %s \t %s' % (lhs+' --> '+rhs, lift, support, confident)
        counter += 1
print 'num of strong rules: ', counter, '\n\n'

# filted by the same lift value
counter = 0
disease = []
for i in range(len(df_strong_rules)):
    rule = df_strong_rules.iloc[i]
    if rule['lift'] > 2.0:
        lift = round(rule['lift'], 2)
        support = round(rule['support'], 2)
        confident = round(rule['confident'], 2)
        
        symptom = []
        for item in (rule['rhs'] | rule['lhs']):
            symptom.append(names[item])
        symptom = ', '.join(symptom)
        if symptom not in disease:
            disease.append(symptom)
            print '%s \t %s \t %s \t %s' % (symptom, lift, support, confident)
            counter += 1

print 'num of rules: ', counter
