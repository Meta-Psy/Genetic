import string
import random
from itertools import islice, product
from math import prod




def random_parent_for_filio():
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    number = random.randint(6, 10)
    parent_1 = list()
    parent_pairs_1 = list()
    for lc, uc in islice(zip(lowercase, uppercase), number):
        pair = random.choice([lc + lc, uc + lc, uc + uc])
        parent_1.append(pair)
        parent_pairs_1.append(pair)
    parent_str_1 = ''.join(parent_1)
    parent_2 = list()
    parent_pairs_2 = list()
    for lc, uc in islice(zip(lowercase, uppercase), number):
        pair = random.choice([lc + lc, uc + lc, uc + uc])
        parent_2.append(pair)
        parent_pairs_2.append(pair)
    parent_str_2 = ''.join(parent_2)
    return parent_str_1, parent_pairs_1, parent_str_2, parent_pairs_2


def split_into_pairs(s):
    return [s[i:i+2] for i in range(0, len(s), 2)]


def random_filio():
    parent_str_1, parent_pairs_1, parent_str_2, parent_pairs_2 = random_parent_for_filio()
    filio_1 = list()
    filio_2 = list()
    for pair in parent_pairs_1:
        if pair == pair.upper():
            filio_1.append(pair[0])
        elif pair == pair.lower():
            filio_1.append(pair[0])
        else:
            filio_1.append(random.choice([pair[0].lower(), pair[0].upper()]))
    for pair in parent_pairs_2:
        if pair == pair.upper():
            filio_2.append(pair[0])
        elif pair == pair.lower():
            filio_2.append(pair[0])
        else:
            filio_2.append(random.choice([pair[0].lower(), pair[0].upper()]))
    result = list()
    hetero_filio = list()
    for ch1, ch2 in zip(filio_1, filio_2):
        if ch2 == ch2.upper():
            result.append(ch2)
            result.append(ch1)
        else:
            result.append(ch1)
            result.append(ch2)
        if ch1 == ch1.upper() and ch2 == ch2.lower():
            pair = [ch1+ch2]
            hetero_filio.append(pair)
    print(parent_str_1, parent_str_2)
    print(hetero_filio, ''.join(result))
    return ''.join(result), hetero_filio, parent_str_1, parent_str_2


def filio_nums():
    filio, hetero_filio, parent_1, parent_2 = random_filio()
    count = 1
    for pair in hetero_filio:
        if str(pair[0]) in parent_1 and str(pair[0]) in parent_2:
            count += 1
        else:
            pass
    answer = 2**count
    return answer, filio, parent_1, parent_2


def random_parents(n, m):
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    number = random.randint(n, m)
    parent_1 = list()
    hetero_1 = 0
    for lc, uc in islice(zip(lowercase, uppercase), number):
        pair = random.choice([lc + lc, uc + lc, uc + uc])
        parent_1.append(pair)
        if pair[0] != pair[1]:
            hetero_1 += 1
    parent_str_1 = ''.join(parent_1)
    parent_2 = list()
    hetero_2 = 0
    for lc, uc in islice(zip(lowercase, uppercase), number):
        pair = random.choice([lc + lc, uc + lc, uc + uc])
        parent_2.append(pair)
        if pair[0] != pair[1]:
            hetero_2 += 1
    parent_str_2 = ''.join(parent_2)
    return parent_str_1, hetero_1, parent_str_2, hetero_2, number



def create_pre_fen():
    parent_str_1, hetero_1, parent_str_2, hetero_2, number = random_parents(2, 3)
    parent_1_pairs = split_into_pairs(parent_str_1)
    parent_2_pairs = split_into_pairs(parent_str_2)
    pre_answer = list()
    for pair_parent_1, pair_parent_2 in islice(zip(parent_1_pairs, parent_2_pairs), number):
        # Гетерозигота с гетерозиготой (Аа х Аа)
        if pair_parent_1 == pair_parent_2 and pair_parent_1[0] != pair_parent_1[1]:
            pre_answer.append([3, 1])
        # Гомозиготы с гомозиготами (АА х АА или АА х аа или аа х АА или аа х аа)
        elif pair_parent_1[0] == pair_parent_1[1] and pair_parent_2[0] == pair_parent_2[1]:
            pre_answer.append([1])
        # Гомозиготы с гетерозиготами (АА х Аа или аа х Аа или Аа х АА или Аа х аа)
        else:
            pre_answer.append([1, 1])
    return parent_str_1, parent_str_2, pre_answer


def create_pre_gen():
    parent_str_1, hetero_1, parent_str_2, hetero_2, number = random_parents(2, 3)
    parent_1_pairs = split_into_pairs(parent_str_1)
    parent_2_pairs = split_into_pairs(parent_str_2)
    pre_answer = list()
    for pair_parent_1, pair_parent_2 in islice(zip(parent_1_pairs, parent_2_pairs), number):
        # Гетерозигота с гетерозиготой (Аа х Аа)
        if pair_parent_1 == pair_parent_2 and pair_parent_1[0] != pair_parent_1[1]:
            pre_answer.append([1, 2, 1])
        # Гомозиготы с гомозиготами (АА х АА или АА х аа или аа х АА или аа х аа)
        elif pair_parent_1[0] == pair_parent_1[1] and pair_parent_2[0] == pair_parent_2[1]:
            pre_answer.append([1])
        # Гомозиготы с гетерозиготами (АА х Аа или аа х Аа или Аа х АА или Аа х аа)
        else:
            pre_answer.append([1, 1])
    return parent_str_1, parent_str_2, pre_answer


def segregation_fen():
    parent_str_1, parent_str_2, pre_answer = create_pre_fen()
    combinations = product(*pre_answer)
    results = [prod(comb) for comb in combinations]
    result = ':'.join(map(str, results))
    print(result)
    return parent_str_1, parent_str_2, result


def segregation_gen():
    parent_str_1, parent_str_2, pre_answer = create_pre_gen()
    combinations = product(*pre_answer)
    results = [prod(comb) for comb in combinations]
    result = ':'.join(map(str, results))
    print(parent_str_1, parent_str_2)
    print(pre_answer)
    print(result)
    return parent_str_1, parent_str_2, result


