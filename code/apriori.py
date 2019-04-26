#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging

MIN_SUPPORT = 0.2
MIN_CONFIDENT = 0.6
MIN_LIFT = 3.0

def load_dataset(file_path):
    """Load dataset from preprocess csv file.

    Args:
        file_path: the path of preprocessed .csv file

    Returns:
        data_set: a list contain the transaction, each transaction is also list represent the feature number"""
    data_set = []
    # check if the file exist
    if not os.path.isfile(file_path):
        logging.warning('Dataset file is wrong!\n')
        return data_set
    fp = open(file_path, 'r')
    # ignore the first line, which is a representation of feature number
    fp.readline()
    for line in fp:
        content = line.strip()
        content = '[' + content + ']'
        data_set.append(list(eval(content)))
    fp.close()
    logging.debug('load dataset success!')
    return data_set


def create_c1(data_set):
    """Create the 1-item set.

    Create the 1-item set that each item occurs in data_set.

    Args:
        data_set: a list contains all transactions, which represented by feature number.

    Returns:
        c1: the 1-item set."""
    c1 = []
    for transaction in data_set:
        for item in transaction:
            if [item] not in c1:
                c1.append([item])
    c1.sort()
    logging.debug('finish create c1')
    return map(frozenset, c1)


def create_ck(ffk, k):
    """Create the k-item set.

    Create the k-item set from frequent (k-1)-item set 'ffk'.

    Args:
        ffk: frequent (k-1)-item set
        k: the k-th round indicator

    Returns:
        ck: candidate k-item set"""
    ck = []
    len_ffk = len(ffk)
    for i in range(len_ffk):
        for j in range(i+1, len_ffk):
            # get the first (k-2) items
            set1 = list(ffk[i])[:k-2]
            set1.sort()
            set2 = list(ffk[j])[:k-2]
            set2.sort()
            # if first (k-2) items are the same, do union
            if set1 == set2:
                ck.append(ffk[i] | ffk[j])
    logging.debug('\nfinish create c%s' % k)
    return ck


def calc_support(ck, data_set, min_support = 0.5):
    """Find frequent set.

    Find the frequent k-item set 'fk' from the candidate k-item set 'ck' by calculating support that match min_support.

    Args:
        ck: candidate k-item set
        data_set: a list contains all transactions, which represented by feature number.
        min_support: the threshold of support that frequent item must match

    Returns:
        fk: frequent k-item set
        fk_support: the dictionary stored the support value of each frequent item in 'fk'"""
    num_transaction = float(len(data_set))
    fk = []
    fk_support = {}
    for candidate in ck:
        for transaction in data_set:
            if candidate.issubset(transaction):
                # count the occur times of candidate in all transactions
                if candidate not in fk_support:
                    fk_support[candidate] = 1
                else:
                    fk_support[candidate] += 1
        # calculate the support value of candidate
        fk_support[candidate] = float(fk_support[candidate]) / num_transaction
        # if support value not match, delete it from fk_support
        if fk_support[candidate] < min_support:
            fk_support.pop(candidate)
        # if support value match, put the candidate in the frequent k-item set 'fk'
        else:
            fk.insert(0, candidate)
    logging.debug('finish calculate support value')
    return fk, fk_support


def apriori(data_set, min_support):
    """Apriori algrithm to the get all the frequent item set.

    Find all frequent set whose support value above the 'min_support'.

    Args:
        data_set: a list contains all transactions, which represented by feature number.
        min_support: the threshold of support that frequent item must match.

    Returns:
        f: a set contains all frequent item sets, f[k-1] store the frequent k-item set.
        f_support: a dictionary stored support value of every frequent item.
    """
    # get the candidate set of 1-item
    c1 = create_c1(data_set)
    # get 1-item frequent set and corresponding support value dictionary
    f1, f_support = calc_support(c1, data_set, min_support)
    # build a frequent set to store all k-item frequent set
    f = [f1]
    logging.debug('k: 1')
    logging.debug('f1: %s\n' % f1)
    k = 2
    while(len(f[k-2]) > 0):
        logging.debug('k: %s' % k)
        ck = create_ck(f[k-2], k)
        fk, fk_support = calc_support(ck, data_set, min_support)
        # add new k-item frequent set into 'f'
        f.append(fk)
        # update the dictionay
        f_support.update(fk_support)
        logging.debug('f%s: %s\n' % (k, fk))
        k += 1
    # remove the empty set
    f.pop()
    logging.info('find all frequent set!')
    return f, f_support


def exam_rule(freq_item, posts, f_support, rules, min_confident = 5.0, min_lift = 3.0):
    """Calculate lift value of the rule.

    For each candidate postposition in set 'posts', calculate the lift value and store the rule whose value above 'min_lift'.

    Args:
        freq_item: the original frequent item.
        posts: a set of candidate postposition of the 'freq_item'.
        f_support: a dictionary stored support value of every frequent item.
        rules: a list contains all rules.
        min_lift: the threshold of lift value that rules must match. 

    Returns:
        pruned_posts: the post that is useful."""
    pruned_posts = []
    for post in posts:
        rule = {}
        rule['lhs'] = freq_item - post
        rule['rhs'] = post
        # calculate the support value
        rule['support'] = f_support[freq_item]
        # calculate the confident value
        rule['confident'] = f_support[freq_item] / f_support[rule['lhs']]
        # calculate the lift value
        rule['lift'] = f_support[freq_item] / (f_support[rule['lhs']] * f_support[post])
        # store the rule math lift threshold
        if rule['confident'] >= min_confident:
            logging.debug('%s --> %s, %s, %s, %s' % (rule['lhs'], post, rule['support'], rule['confident'], rule['lift']))
            rules.append(rule)
            pruned_posts.append(post)
    return pruned_posts


def get_rule(freq_item, posts, f_support, rules, min_confident = 5.0, min_lift = 3.0):
    """Get rules of a frequent item.

    Get rule from postposition is generate from privious postposition 'posts'.

    Args:
        freq_item: the original frequent item.
        posts: a set of candidate postposition of the 'freq_item'.
        f_support: a dictionary stored support value of every frequent item.
        rules: a list contains all rules.
        min_lift: the threshold of lift value that rules must match. 

    Returns:
        None"""
    # frequent item cantians only 2 items
    if len(freq_item) == 2:
        # directly exam the candidate rule
        exam_rule(freq_item, posts, f_support, rules, min_confident, min_lift)
    # frequent item cantians more than 2 items
    else:
        m = len(posts[0])
        # post is only 1 item, directly exam the candidate rule
        if m == 1:
            exam_rule(freq_item, posts, f_support, rules, min_confident, min_lift)
        if len(freq_item) > m+1:
            # generate new posts
            posts = create_ck(posts, m+1)
            # exam the rule and get the useful posts
            posts = exam_rule(freq_item, posts, f_support, rules, min_confident, min_lift)
            if(len(posts) > 1):
                get_rule(freq_item, posts, f_support, rules, min_confident, min_lift)


def gen_rules(f, f_support, min_confident = 5.0, min_lift = 3.0):
    """Generate rules from all frequent item.

    For each frequent item, generate its rules that match lift value.

    Args:
        f: a set contains all frequent item sets, f[k-1] store the frequent k-item set.
        f_support: a dictionary stored support value of every frequent item. 
        min_lift: the threshold of lift value that rules must match.

    Returns:
        rules: a list contains all rules
    """
    rules = []
    logging.debug("lhs --> rhs, support, confident, lift")
    for i in range(1, len(f)):
        for freq_item in f[i]:
            # get 1-item postposition
            h1 = [frozenset([item]) for item in freq_item]
            get_rule(freq_item, h1, f_support, rules, min_confident, min_lift)
    return rules


if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)

    data_set = load_dataset('../data/diagnosis.csv')
    logging.debug('first 5 line of data_set:\n%s\n' % data_set[:5])

    f, f_support = apriori(data_set, MIN_SUPPORT)
    logging.debug('\n\n\nf:\n%s' % f )
    logging.debug('\nf_support\n%s' % f_support)

    rules = gen_rules(f, f_support, MIN_CONFIDENT, MIN_LIFT)
    print len(rules)