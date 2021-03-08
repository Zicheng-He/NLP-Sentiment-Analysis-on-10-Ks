

# Not used in Project
def negated(word,negate):
    """
    Determine if preceding word is a negation word
    """
    if word.lower() in negate:
        return True
    else:
        return False

# Not used in Project
def update_set(documents, neg_hv, neg_lm, pos_hv, pos_lm):
    import re
    for docu in documents:
        input_words = re.findall(r'\b([a-zA-Z]+n\'t|[a-zA-Z]+\'s|[a-zA-Z]+)\b', docu.lower())
        for i in range(len(input_words)):
            if input_words[i] in (pos_hv - pos_lm):
                if i >= 3:
                    if negated(input_words[i - 1]) or negated(input_words[i - 2]) or negated(input_words[i - 3]):
                        neg_hv.add(input_words[i] + ' (with negation)')
                elif i == 2:
                    if negated(input_words[i - 1]) or negated(input_words[i - 2]):
                        neg_hv.add(input_words[i] + ' (with negation)')
                elif i == 1:
                    if negated(input_words[i - 1]):
                        neg_hv.add(input_words[i] + ' (with negation)')
            if input_words[i] in (pos_lm - pos_hv):
                if i >= 3:
                    if negated(input_words[i - 1]) or negated(input_words[i - 2]) or negated(input_words[i - 3]):
                        neg_lm.add(input_words[i] + ' (with negation)')
                elif i == 2:
                    if negated(input_words[i - 1]) or negated(input_words[i - 2]):
                        neg_lm.add(input_words[i] + ' (with negation)')
                elif i == 1:
                    if negated(input_words[i - 1]):
                        neg_lm.add(input_words[i] + ' (with negation)')
            else:
                if i >= 3:
                    if negated(input_words[i - 1]) or negated(input_words[i - 2]) or negated(input_words[i - 3]):
                        neg_hv.add(input_words[i] + ' (with negation)')
                        neg_lm.add(input_words[i] + ' (with negation)')
                elif i == 2:
                    if negated(input_words[i - 1]) or negated(input_words[i - 2]):
                        neg_hv.add(input_words[i] + ' (with negation)')
                        neg_lm.add(input_words[i] + ' (with negation)')
                elif i == 1:
                    if negated(input_words[i - 1]):
                        neg_hv.add(input_words[i] + ' (with negation)')
                        neg_lm.add(input_words[i] + ' (with negation)')

# The function returns weight matrix for word i in jth 10-K
def problem2(documents, set_hv, set_lm):
    import re
    import numpy as np
    "documents is a list of 10-Ks text, set_hv is a set of harvard negative words"
    N = len(documents)
    total_words = [0] * N
    "The initial dictionary format is key(nagative word) : [0]*N "
    "Each element in list [0]*N stands for the total counts of that word in j th 10-K "
    dic_hv = {key: [0] * N for key in set_hv}
    dic_lm = {key: [0] * N for key in set_lm}
    for j in range(N):
        input_words = re.findall(r'\b([a-zA-Z]+n\'t|[a-zA-Z]+\'s|[a-zA-Z]+)\b', documents[j].lower())
        'aj : total words count in jth 10-K'
        total_words[j] = len(input_words)
        for i in range(len(input_words)):
            if input_words[i] in dic_hv:
                dic_hv[input_words[i]][j] += 1
            if input_words[i] in dic_lm:
                dic_lm[input_words[i]][j] += 1
    count_hv = {key:sum(np.array(dic_hv[key])>0) for key in dic_hv}
    count_lm = {key:sum(np.array(dic_lm[key])>0) for key in dic_lm}


    c_hv = np.zeros((len(dic_hv),N))
    c_lm = np.zeros((len(dic_lm),N))
    term_hv = np.zeros((len(dic_hv),N))
    term_lm = np.zeros((len(dic_lm),N))
    prop_hv = np.zeros((len(dic_hv),N))
    prop_lm = np.zeros((len(dic_lm),N))

    for i, p in enumerate(count_hv):
        for j in range(N):
            tfij = dic_hv[p][j]
            if tfij >=1 :
                c_hv[i][j] = tfij
                term_hv[i][j] = (1 + np.log(tfij)) / (1 + np.log(total_words[j])) * np.log(N / count_hv[p])
                prop_hv[i][j] = tfij / total_words[j]
            else:
                c_hv[i][j] = 0
                term_hv[i][j] = 0
                prop_hv[i][j] = 0
    for i, p in enumerate(count_lm):
        for j in range(N):
            tfij = dic_lm[p][j]
            if tfij >=1 :
                c_lm[i][j] = tfij
                term_lm[i][j] = (1 + np.log(tfij)) / (1 + np.log(total_words[j])) * np.log(N / count_lm[p])
                prop_lm[i][j] = tfij / total_words[j]
            else:
                c_lm[i][j] = 0
                term_lm[i][j] = 0
                prop_lm[i][j] = 0

    return term_hv, term_lm, prop_hv, prop_lm, c_hv, c_lm







