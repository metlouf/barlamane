import json
import re

def process_commission(word):
    
    result = word.replace("لجنة","").replace("و ","و").replace("لإ","لا").strip()
    if "عدل" in word:
        return "العدل"
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
    with open('data/parliamentarians_arabic_2016_2021.json', 'r') as file:
        data = json.load(file)

    # Extract the set of commissions without redundancy
    commissions = set()
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
    with open('data/questions.json', 'r') as file:
        data = json.load(file)

    # Extract the set of commissions without redundancy
    ministy = set()
    for q in data:
        ministy.add(q['to'])

    # Print the set of commissions
    return ministy
    for a in list(ministy):
        print(a)

#check_laws()
#print("(#################)")
#check_deputies()
#print("(#################)")
#check_questions()

def check_inter() : 
    with open('data/questions.json', 'r') as file:
        data_q = json.load(file)

    with open('data/parliamentarians_arabic_2016_2021.json', 'r') as file:
        data_d = json.load(file)

    # Extract the set of commissions without redundancy
    hq = set()
    for q in data_q:
        hq.add(q['author'])

    # Print the set of commissions
    hd= set()
    for d in data_d:
        hd.add(d['name'])
    
    for a in list(set.intersection(hq,hd)):
        print(a)

#check_inter()