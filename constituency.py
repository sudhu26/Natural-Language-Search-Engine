#!/usr/bin/env python


import sys, nltk
from nltk.tree import Tree
import qa
from qa_engine.base import QABase


# See if our pattern matches the current root of the tree
def matches(pattern, root):
    # Base cases to exit our recursion
    # If both nodes are null we've matched everything so far
    if root is None and pattern is None: 
        return root
        
    # We've matched everything in the pattern we're supposed to (we can ignore the extra
    # nodes in the main tree for now)
    elif pattern is None:                
        return root
        
    # We still have something in our pattern, but there's nothing to match in the tree
    elif root is None:                   
        return None

    # A node in a tree can either be a string (if it is a leaf) or node
    plabel = pattern if isinstance(pattern, str) else pattern.label()
    rlabel = root if isinstance(root, str) else root.label()

    # If our pattern label is the * then match no matter what
    if plabel == "*":
        return root
    # Otherwise they labels need to match
    elif plabel == rlabel:
        # If there is a match we need to check that all the children match
        # Minor bug (what happens if the pattern has more children than the tree)
        for pchild, rchild in zip(pattern, root):
            match = matches(pchild, rchild) 
            if match is None:
                return None 
        return root
    
    return None
    
def pattern_matcher(pattern, tree):
    for subtree in tree.subtrees():
        node = matches(pattern, subtree)
        if node is not None:
            return node
    return None

def get_quesconstituency(question,filters):
    tree=question["par"]
    for filter in filters:
        pattern = nltk.ParentedTree.fromstring(filter)
        # # Match our pattern to the tree  
        subtree = pattern_matcher(pattern, tree)
        if subtree != None:
            answer = " ".join(subtree.leaves())
        else:
            answer =""
        return answer

def get_constituency(question,story,filter):
    story_type=""
    if question["type"]=='Sch':
        story_type="sch_par"
    else:
        story_type="story_par"
    tree = story[story_type][qa.get_Index(question,story)]
    sentences=nltk.sent_tokenize(story["text"])
    #print("STORYYY : ",sentences[qa.get_Index(question,story)])
     # Create our pattern
    pattern = nltk.ParentedTree.fromstring(filter)
    
    # # Match our pattern to the tree  
    subtree = pattern_matcher(pattern, tree)
    # print(" ".join(subtree.leaves()))
    
    # create a new pattern to match a smaller subset of subtree
   # pattern = nltk.ParentedTree.fromstring("(PP)")
    #print(tree)
    #if subtree == None:
        #print (tree)
    # Find and print the answer
    #subtree2 = pattern_matcher(pattern, subtree)
    answer = " ".join(subtree.leaves())
    print(answer)
    return answer

if __name__ == '__main__':

    driver = QABase()
    q = driver.get_question("fables-01-1")
    story = driver.get_story(q["sid"])

    tree = story["sch_par"][1]

    # Create our pattern
    pattern = nltk.ParentedTree.fromstring("(VP (*) (PP))")
    
    # # Match our pattern to the tree  
    subtree = pattern_matcher(pattern, tree)
    # print(" ".join(subtree.leaves()))
    
    # create a new pattern to match a smaller subset of subtree
    pattern = nltk.ParentedTree.fromstring("(PP)")

    # Find and print the answer
    subtree2 = pattern_matcher(pattern, subtree)
    print(" ".join(subtree2.leaves()))
