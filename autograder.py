import json
import sys
import difflib
from nltk.metrics import edit_distance
from collections import Counter
from pprint import pprint

decision_to_methods = {'1': 'hardcoded', '2': 'scraped', '3': 'detected'}
methods_to_decision = {'hardcoded': 1, 'scraped': 2, 'detected': 3}

def acceptable_distance(resultlen,matchlen):
    minlen = float(min(resultlen,matchlen))
    return (minlen/2.0 + float(max(resultlen,matchlen)-minlen))

def prep(word):
    return word.replace('tv','television').replace('/',' or ').replace('movie','motion picture').replace('film','motion picture').replace('show','series').strip().lower()

def norm_text(textlist):
    """Takes a list of text and returns a string of normalized text."""
    textlist = [' '.join(line.lower().split()) for line in textlist]
    textlist = ["".join([c for c in line if c.isalnum() or c.isspace()]) for line in textlist]
    text = '\n'.join(textlist)

    return text

def text(result,answer):
    """Accepts two normalized texts, as output by the norm_text function, and returns a score based on the match length relative to the longest text length."""
    len_result = len(result)
    len_answer = len(answer)

    if (result in answer) or (answer in result):
        textscore = min(len_result,len_answer)/float(max(len_result,len_answer))
    else:
        s = difflib.SequenceMatcher(None, result, answer)

    # matchlen = len('\n'.join([newtext[m[0]:m[0]+m[2]].strip() for m in s.get_matching_blocks() if m[2] > 1]).strip().split())
    # textscore = float(matchlen)/min([len(oldtext.strip().split()),len(newtext.strip().split())])
        longest = s.find_longest_match(0,len_result,0,len_answer)
        longest = longest.size/float(max(len_result,len_answer))
        if longest > 0.3:
            matchlen = sum([m[2] for m in s.get_matching_blocks() if m[2] > 1])
            textscore = float(matchlen)/max(len_result,len_answer)
        else:
            textscore = longest

    return textscore

def calc_awards(result,answer):
    problems = []
    intersection = result.intersection(answer)
    translation = dict(zip(intersection,intersection))
    for r in (result-intersection):
        prepped = prep(r)
        rlist = set(prepped.split())
        if 'animated' in rlist:
            translation[r] = 'best animated feature film'
        elif 'foreign' in rlist:
            translation[r] = 'best foreign language film'
        elif 'director' in rlist:
            translation[r] = 'best director - motion picture'
        elif rlist.intersection(('screenplay', 'script')):
            translation[r] = 'best screenplay - motion picture'
        elif 'score' in rlist:
            translation[r] = 'best original score - motion picture'
        elif 'song' in rlist:
            translation[r] = 'best original song - motion picture'
        elif rlist.intersection(('cecil','demille')):
            translation[r] = 'cecil b. demille award'
        else:
            if rlist.intersection(('comedy','musical')):
                qualifier = 'comedy or musical'
            elif 'drama' in rlist:
                qualifier = 'drama'
            else:
                qualifier = None

            if rlist.intersection(('performance','actor','actress','supporting')):
                if 'actor' in rlist:
                    actor = 'actor'
                elif 'actress' in rlist:
                    actor = 'actress'
                else:
                    actor = None

                if rlist.intersection(('miniseries','mini-series')) or (True in [phrase in prepped for phrase in ['mini series', 'made for television', 'television motion picture']]):
                    if qualifier:
                        problems.append(r)
                    elif 'supporting' in rlist:
                        if actor:
                            translation[r] = 'best performance by an %s in a supporting role in a series, mini-series or motion picture made for television'%actor
                        else:
                            problems.append(r)
                    elif actor:
                        translation[r] = 'best performance by an %s in a mini-series or motion picture made for television'%actor
                    else:
                        problems.append(r)
                elif 'television' in rlist:
                    if not qualifier:
                        problems.append(r)
                    elif actor:
                        translation[r] = 'best performance by an %s in a television series - %s'%(actor,qualifier)
                    else:
                        problems.append(r)
                elif rlist.intersection(('motion','picture')):
                    if not actor:
                        problems.append(r)
                    elif 'supporting' in rlist:
                        if qualifier:
                            problems.append(r)
                        else:
                            translation[r] = 'best performance by an %s in a supporting role in a motion picture'%actor
                    elif qualifier:
                        translation[r] = 'best performance by an %s in a motion picture - %s'%(actor,qualifier)
                    else:
                        problems.append(r)
                else:
                    problems.append(r)
            elif rlist.intersection(('miniseries','mini-series')) or (True in [phrase in prepped for phrase in ['mini series', 'made for television', 'television motion picture']]):
                if qualifier:
                    problems.append(r)
                else:
                    translation[r] = 'best mini-series or motion picture made for television'
            elif 'television series' in prepped:
                if qualifier:
                    translation[r] = 'best television series - %s'%qualifier
                else:
                    problems.append(r)
            elif 'motion picture' in prepped:
                if qualifier:
                    translation[r] = 'best motion picture - %s'%qualifier
                else:
                    problems.append(r)
            else:
                problems.append(r)
    if len(problems) > 0:
        print "Could not find a match for the following results:"
    for p in problems:
        print p

    problems = answer-intersection - set(translation.values())
    if len(problems) > 0:
        print "Could not find a match for the following answers:"
    for p in problems:
        print p

    # sum([edit_distance(t,translation[t])/float(max(len(t),len(translation[t]))) for t in translation])
    score = calc_score(set([translation[a] if a in translation else a for a in result]),answer)*len(answer)

    return score,translation

def calc_translation(result,answer):
    intersection = result.intersection(answer)
    translation = dict(zip(intersection,intersection))
    scores = dict(zip(intersection, [1]*len(intersection)))
    score_by_results = {}
    score_by_answers = {}
    for r in (result-intersection):
        score_by_results[r] = Counter()
        for a in answer:
            if a not in score_by_answers:
                score_by_answers[a] = Counter()
            score_by_results[r][a] = text(norm_text([a]),norm_text([r]))
            score_by_answers[a][r] = score_by_results[r][a]
    for r in score_by_results:
        cnt = 0
        ranking = score_by_results[r].most_common()
        flag = True
        while flag:
            answer_match = ranking[cnt][0]
            max_result = score_by_answers[answer_match].most_common()[0]
            # print "result: %s\tbest answer: %s, %.1f\tbest result for answer: %s, %.2f"%(r,answer_match,score_by_results[r][answer_match],max_result[0], max_result[1])
            # max_length = acceptable_distance(len(answer_match),len(r))
            # print "result: %s\tmatch: %s\tdistance: %f\tdistance to alt: %f\tmax distance: %f"%(r,answer_match,score_by_results[r][answer_match],min_result[1],max_length)

            if score_by_results[r][answer_match] < 0.45:
                # print "No result found."
                flag = False
            elif (max_result[0] == r) or (score_by_results[r][answer_match] > score_by_answers[answer_match][max_result[0]]):
                translation[r] = answer_match
                change = 1-(edit_distance(r,answer_match)/float(max(len(r),len(answer_match))))
                if answer_match in scores:
                    scores[answer_match] = (scores[answer_match] + change)/2.0
                else:
                    scores[answer_match] = change
                
                # print "%s\t->\t%s:\t%f\n"%(r,answer_match,change)
                flag = False

            cnt += 1
            if cnt == len(ranking):
                # print "No result found.\n"
                flag = False
            
    return sum(scores.values()),translation

def calc_score(result, answer):
    intersection = result.intersection(answer)
    len_intersection = len(intersection)
    len_union = len(result.union(answer))
    len_result = len(result)
    len_answer = len(answer)

    if len_union == 0:
        return 0
    elif len_result == len_answer and len_intersection == len_answer:
        m = 1.0
    elif len_intersection == len_result:
        # all results correspond to a correct answer, but some 
        # answers are missing
        m = 0.95
    elif len_intersection == len_answer:
        # all answers correspond to a result, but there are
        # some extra results as well
        m = 0.9
    elif len_intersection > 0:
        # there is some post-translation intersection between
        # results and answers.
        m = 0.85
    else:
        return 0

    return (len_intersection / float(len_union)) * m

def check_metadata(item,metadata):
    if metadata['method'] == 'hardcoded':
        print "The %s were hard coded.\n"%item
        return 1
    else:
        print item
        print metadata['method']
        print metadata['method_description']
        print "\n1. Treat as hardcoded.\n2. Treat as scraped.\n3. Treat as detected."

    return int(raw_input())            

def lowercase(item):
    for i in item['unstructured']:
        item['unstructured'][i] = [a.lower() for a in item['unstructured'][i]]
    structured = {}
    for award in item['structured']:
        new_award = {}
        for info_type in item['structured'][award]:
            new_info_type = info_type.lower()
            if new_info_type=='winner':
                new_award[new_info_type] = item['structured'][award][info_type].lower()
            else:
                new_award[new_info_type] = [i.lower() for i in item['structured'][award][info_type]]
        structured[award.lower()] = new_award
    item['structured'] = structured

    return item

def calc_weights(names, mappings):
    weights = {'nominees': {}, 'presenters': {}, 'awards': {}, 'hosts': {}}

    for item_type in ['nominees','presenters','awards','hosts']:
        if item_type in mappings:
            weights[item_type]['mappings'] = (check_metadata("%s - mappings"%item_type.title(),mappings[item_type]) - 1.0)/2.0
        else:
            weights[item_type]['mappings'] = 1.0

        if item_type in names:
            weights[item_type]['names'] = (check_metadata("%s - names"%item_type.title(),names[item_type]) - 1.0)/2.0
        else:
            weights[item_type]['mappings'] = 1.0

    return weights


def main(filename):
    with open(filename, 'r') as f:
        results = json.load(f)
    results['data'] = lowercase(results['data'])

    with open('gg%sanswers.json'%str(results['metadata']['year']),'r') as f:
        answers = lowercase(json.load(f))

    scores = {'unstructured': {},'structured': {}}
    translation = {}
    total = 0
    weights = calc_weights(results['metadata']['names'],results['metadata']['mappings'])

    if set(results['data']['unstructured']['winners']) < set(results['data']['unstructured']['nominees']):
        if weights['nominees']['mappings'] < 1:
            weights['winners'] = {'names': 0.5, 'mappings': 0.5}
        elif weights['nominees']['names'] < 1:
            weights['winners'] = {'names': 0.5, 'mappings': 1.0}
    else:
        weights['winners'] = {'names': 1.0, 'mappings': 1.0}

    unstructuredstring = ""

    for item in results['data']['unstructured']:
        size = weights[item]['names']*len(answers['unstructured'][item])
        if item == "awards":
            score, trans = calc_awards(set(results['data']['unstructured'][item]),set(answers['unstructured'][item]))
        else:
            score, trans = calc_translation(set(results['data']['unstructured'][item]),set(answers['unstructured'][item]))
            if item == "winners":
                score = calc_score(set([trans[w] if w in trans else w for w in results['data']['unstructured']['winners']]),set(answers['unstructured']['winners']))*size

        translation.update(trans)
        
        if weights[item]['names'] != 0:
            scores['unstructured'][item] = weights[item]['names']*score
            unstructuredstring += "\n%.2f / %3.2f\t%s\n"%(score,size,item)

        total += size
    pprint(translation)
    print "CALCULATING UNSTRUCTURED SCORES"
    print "============================="
    print "Each name/title is worth one point. The autograder does its best\nto match the correct answers to your answers. You receive full credit\nfor each matching award, and the edit distance between matches is\nused to give partial credit for non-exact matches. Also, for winners\nand awards, there are penalties for too many or too few answers.\n"
    print unstructuredstring
    scores['unstructured']['overall'] = sum(scores['unstructured'].values())
    scores['unstructured']['total'] = total
    print "-----------------------------"
    print "TOTAL\t%.2f / %.2f"%(scores['unstructured']['overall'],total)
    print "\n============================="
    print "CALCULATING STRUCTURED SCORES"
    print "============================="
    print "Using the translations generated during unstructured scoring,\n you are scored for accurately matching nominees, presenters, and\nwinners to award names (also determined using the translations dictionary).\nAlso, for presenters and nominees, there are penalties for too many or\ntoo few answers.\n"
    totals = {}

    for a in results['data']['structured']:
        if a in translation:
            translated = translation[a]
            print translated
            for item in results['data']['structured'][a]:
                if item == "winner":
                    if len(results['data']['structured'][a]['winner']) == 0:
                        size = 0
                        score = 0
                        print "empty string for winner"
                    else:
                        size = weights['winners']['mappings']
                        winner = results['data']['structured'][a]['winner']
                        if (winner in translation) and (answers['structured'][translated]['winner'] == translation[winner]):
                            score = size
                        else:
                            score = 0
                else:
                    length = len(answers['structured'][translated][item])
                                       
                    size = length*weights[item]['mappings']

                    transitem = set([translation[r] if r in translation else r for r in results['data']['structured'][a][item]])
                    if item == "nominees":
                        transitem = (transitem - set(answers['structured'][translated]['winner'])) - set(results['data']['structured'][a]['winner'])
                    score = calc_score(set(answers['structured'][translated][item]),transitem)*size
                if item not in scores['structured']:
                    scores['structured'][item] = score
                    totals[item] = size
                else:
                    scores['structured'][item] += score
                    totals[item] += size
                if size != 0:
                    print "\t%s:\t%.2f / %2.2f"%(item.capitalize(),score,size)

    print "============================="
    scores['structured']['overall'] = sum(scores['structured'].values())
    scores['structured']['total'] = sum([totals[item] for item in totals])

    if ('nominees' in scores['structured']) and (totals['nominees'] > 0):
        print "Structured nominees score:  \t%.2f / %.2f"%(scores['structured']['nominees'], totals['nominees'])
    if ('presenters' in scores['structured']) and (totals['presenters'] > 0):
        print "Structured presenters score:\t%.2f / %.2f"%(scores['structured']['presenters'],totals['presenters'])

    print "Structured winners score:   \t%.2f / %.2f"%(scores['structured']['winner'],totals['winner'])
    
    print "-----------------------------"
    print "TOTAL                       \t%.2f / %.2f\n"%(scores['structured']['overall'],scores['structured']['total'])
    print "============================="
    print "CALCULATING TOTAL SCORES"
    print "============================="

    scores['overall'] = scores['unstructured']['overall'] + scores['structured']['overall']
    scores['total'] = scores['unstructured']['total'] + scores['structured']['total']

    print "TOTAL\t%.2f / %.2f"%(scores['overall'],scores['total'])

    with open('gg%sscores.json'%str(results['metadata']['year']),'w') as f:
        json.dump(scores,f)

if __name__ == '__main__':
    main(sys.argv[1])