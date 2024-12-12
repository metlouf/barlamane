import json
import re

DEBUG = False

def process_commission(word):
    
    result = word.replace("لجنة","").replace("و ","و").replace("لإ","لا").strip()
    if "عدل" in word:
        return "العدل"
    if "مراقبة المالية العامة" in word :
        return "مراقبة المالية العامة"
    if len(result)>40 :
        return result[:30].split(" ")[0]
    #result = re.sub("الخارجية", 'الخارجية*', result)
    #result = re.sub("الداخلية", 'الداخلية*', result)

    return result


def extract_commissions_from_laws() :
    with open('data/laws_arabic_version.json', 'r') as file:
        data = json.load(file)

    # Extract the set of commissions without redundancy
    commissions = set()
    for project in data['projets_de_loi']:
        for reading in project['readings']:
            if 'commission' in reading:
                commissions.add(process_commission(reading['commission']))

    for project in data['propositions_de_loi']:
        for reading in project['readings']:
            if 'commission' in reading:
                commissions.add(process_commission(reading['commission']))
    for project in data['textes_de_loi']:
            if 'commission' in project:
                commissions.add(process_commission(project['commission']))

    # Print the set of commissions
    return commissions
    for a in list(commissions):
        print(a)

def extract_commissions_from_deputies() :
    
    commissions = set()
    for term in ['2011_2016','2016_2021','2021_2026'] :
        with open('data/parliamentarians_arabic_%s.json'%term, 'r') as file:
            data = json.load(file)

        # Extract the set of commissions without redundancy
        for deputy in data:
            if 'function' in deputy:
                if "فريق" in deputy['function'] :
                    pass
                else :
                    commissions.add(process_commission(deputy['function']))

        # Print the set of commissions
    return commissions
    for a in list(commissions):
        print(a)

def extract_ministry_from_questions() :
    ministy = set()
    for i in range(1,6):
        with open('data/questions_%i.json'%i, 'r') as file:
            data = json.load(file)

        # Extract the set of commissions without redundancy
        for q in data:
            ministy.add(q['to'])

    # Print the set of commissions
    return ministy
    for a in list(ministy):
        print(a)

#check_laws()
#extract_commissions_from_laws()
#print("(#################)")
#extract_commissions_from_deputies()
#print(("#################"))
#extract_ministry_from_questions()


def check_inter() : 

    hq = set()
    for i in range(1,6):
        with open('data/questions_%d.json'%i, 'r') as file:
            data_q = json.load(file)
            for q in data_q:
                hq.add(q['author'])
    #print("##",len(hq))

    hd= set()

    for term in ['2011_2016','2016_2021','2021_2026'] :
        with open('data/parliamentarians_arabic_%s.json'%term, 'r') as file:
            data_d = json.load(file)

        for d in data_d:
            hd.add(d['name'])
    
    for a in list(set.intersection(hq,hd)):
        print(a)
    #print("##",len(hd))
    #print("################# Common",len(set.intersection(hq,hd)))
    for a in hq :
        if a not in hd:
            print(a)

#check_inter()