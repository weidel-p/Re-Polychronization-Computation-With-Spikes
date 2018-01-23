import json
import numpy as np
import sys
import copy

groups_izh_fn = sys.argv[1]
groups_nest_fn = sys.argv[2]


with open(groups_nest_fn, "r+") as f:
    groups_nest = json.load(f)

with open(groups_izh_fn, "r+") as f:
    groups_izh = json.load(f)



def compare(g0, g1):

#    if not g0["L_max"] == g1["L_max"]:
#        return False
#
#    if not g0["N_fired"] == g1["N_fired"]:
#        return False

    if not all([f in g1['fired'] for f in g0['fired']]):
        return False

#    if not all([f in g0['fired'] for f in g1['fired']]):
#        return False
#    
#    if not all([l in g1['links'] for l in g0['links']]):
#        return False
#
#    if not all([l in g0['links'] for l in g1['links']]):
#        return False

    return True


def contains_group(g, groups, i):
    for g0 in groups[i:]:
        if compare(g, g0):
            return i 
        i += 1 

    
    j = 0
    for g0 in groups[:i]:
        if compare(g, g0):
            return j 
        j += 1 

    return False


result_izh = []
i = 0
for g_izh in groups_izh:
    i = contains_group(g_izh, groups_nest, i)
    result_izh.append(i)
    print len(result_izh) / float(len(groups_izh))

result_nest = []
i = 0
for g_nest in groups_nest:
    i = contains_group(g_nest, groups_izh, i)
    result_nest.append(i)
    print len(result_nest) / float(len(groups_nest))





