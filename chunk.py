'''
Created on May 14, 2014
@author: Reid Swanson

Modified on May 21, 2015
'''

from rake_nltk import rake
import re, sys, nltk
from nltk.stem.wordnet import WordNetLemmatizer
from qa_engine.base import QABase

LMTZR = WordNetLemmatizer()

# Our simple grammar from class (and the book)
GRAMMAR =   """
            N: {<PRP>|<NN.*>}
            V: {<V.*>}
            ADJ: {<JJ.*>}
            NP: {<DT>? <ADJ>* <N>+}
            {<DT|PP\$>?<JJ>*<NN>}   
            {<NNP>+}
            PP: {<IN> <NP>}
            VP: {<TO>? <V> (<NP>)*}
            RP: {<PP><VP>?<ADJ|VP>?<NP>?}
            """

def get_sentences(text):
    output = []
    sentences = nltk.sent_tokenize(text)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]    
    for sent in sentences:
        #temp = lemmatize(sent)
        temp = sent
        output.append(temp)
    return output

def lemmatize(tagged_sent):
    temp = []
    for word_pair in tagged_sent:
        if re.search("VB", word_pair[1]):
            temp.append((LMTZR.lemmatize(word_pair[0], "v"),word_pair[1]))
        else:
            temp.append(word_pair)
    return temp

def pp_filter(subtree):
    return subtree.label() == "PP"
def vp_filter(subtree):
    return subtree.label() == "VP"
def np_filter(subtree):
    return subtree.label() == "NP"
def rp_filter(subtree):
    return subtree.label() == "RP"

def is_location(prep):
    return bool(re.search("IN",prep[1]))
    #return prep[0] in LOC_PP

def find_prepphrases(tree):
    # Starting at the root of the tree
    # Traverse each node and get the subtree underneath it
    # Filter out any subtrees who's label is not a PP
    # Then check to see if the first child (it must be a preposition) is in
    # our set of locative markers
    # If it is then add it to our list of candidate locations
    
    # How do we modify this to return only the NP: add [1] to subtree!
    # How can we make this function more robust?
    # Make sure the crow/subj is to the left
    locations = []
    for subtree in tree.subtrees(filter=pp_filter):
        #print(subtree)
        if is_location(subtree[0]):
            locations.append(subtree)
    
    return locations

def find_reasons(tree, indicators=["because","since","for","to"]):
    output = []
    #print(tree)
    for subtree in tree.subtrees(filter=rp_filter):
        if (subtree[0][0][0] in indicators):
            output.append(subtree)
    return output

def find_nounphrase(tree):
    nounphrase=[]
    for subtree in tree.subtrees(filter=np_filter):
        nounphrase.append(subtree)
    return nounphrase
def find_verbphrase(tree):
    verbphrase=[]
    for subtree in tree.subtrees(filter=vp_filter):
        verbphrase.append(subtree)
    return verbphrase

def find_times(tree, indicators = ["by","after","during","before","at", "on"]):
    output = []
    #print(tree)
    for subtree in tree.subtrees(filter=pp_filter):
        if (subtree[0][0] in indicators):
            output.append(subtree)
    return output

def find_candidates(sentences, chunker):
    candidates = []
    for sent in sentences:
        tree = chunker.parse(sent)
        # print(tree)
        locations = find_reasons(tree)
        candidates.extend(locations)
        
    return candidates

def find_sentences(patterns, sentences):
    # Get the raw text of each sentence to make it easier to search using regexes
    raw_sentences = [" ".join([LMTZR.lemmatize(token[0]) for token in sent]) for sent in sentences]
    
    result = []
    for sent, raw_sent in zip(sentences, raw_sentences):
        for pattern in patterns:
            if not re.search(pattern, raw_sent):
                matches = False
            else:
                matches = True
        if matches:
            result.append(sent)
    return result

def get_Subject(np):
    subject=[]

    for t in np:
        for token in t.leaves():
            if bool(re.search("NN[PS]?|PRP",token[1])):
                subject.append(token[0])
    return subject

def get_Action(vp):
    action=[]
    for t in vp:
        for token in t.leaves():
            if bool(re.search("VB[DGNPZ]?",token[1])):
                action.append(token[0])
    return action







if __name__ == '__main__':
    # Our tools
    chunker = nltk.RegexpParser(GRAMMAR)
    lmtzr = WordNetLemmatizer()
    
    question_id = "fables-01-1"

    driver = QABase()
    q = driver.get_question(question_id)
    story = driver.get_story(q["sid"])
    text = story["text"]
    
    question=q["text"]
    question=get_sentences(question)
    qtree=chunker.parse(question[0])
    np=find_nounphrase(qtree)
    vp=find_verbphrase(qtree)
    vp=vp[len(vp)-1]

    #print("Noun Phrase")
    #for t in np:
    #    print(" ".join([token[0] for token in t.leaves()]))
    #print("Verb Phrase")
    #for t in vp:
    #    print(" ".join([token[0] for token in t.leaves()]))

    
    # Apply the standard NLP pipeline we've seen before
    sentences = get_sentences(text)
    
    # Assume we're given the keywords for now
    # What is happening
    verb = "sitting"
    # Who is doing it
    subj = "crow"
    subj=get_Subject(np)[0]
    verb=get_Action(vp)[0]
    # Where is it happening (what we want to know)
    loc = None
    
    # Might be useful to stem the words in case there isn't an extact
    # string match
    subj_stem = lmtzr.lemmatize(subj, "n")
    verb_stem = lmtzr.lemmatize(verb, "v")
    
    # Find the sentences that have all of our keywords in them
    # How could we make this better?
    crow_sentences = find_sentences([subj_stem, verb_stem], sentences)
    
    # Extract the candidate locations from these sentences
    locations = find_candidates(crow_sentences, chunker)
    
    # Print them out
    for loc in locations:
        print(loc)
       # print(" ".join([token[0] for token in loc.leaves()]))