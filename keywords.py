import tqdm
import json

import time
import re
from statistics import mean,median
from yake import KeywordExtractor
from nltk.stem.porter import PorterStemmer
def simplify(text):
    #This function simplifies doubled or more complex punctuation. The exception is '...'.
    corrected = str(text)
    corrected = re.sub(r'([!?,;.])\1+', r'\1', corrected)
    corrected = re.sub(r'\.{2,}', r'...', corrected)

    # normalizes whitespaces, removing duplicates.
    #corrected = str(corrected)
    corrected = re.sub(r"//t",r"\t", corrected)
    corrected = re.sub(r"( )\1+",r"\1", corrected)
    corrected = re.sub(r"(\n)\1+",r"\1", corrected)
    corrected = re.sub(r"(\r)\1+",r"\1", corrected)
    corrected = re.sub(r"(\t)\1+",r"\1", corrected)
    return corrected.strip(" ")


def normalization_pipeline(text):
    #print("Starting Normalization Process")
    text = simplify(text)
    #sentences = normalize_contractions(text)
    #sentences = spell_correction(sentences)
    #print("Normalization Process Finished")
    return text

def preprocess1(keywords_initial):
    #lower 转化为小写
    keywords_initial = keywords_initial.strip().lower()

    # split into array with multiple delimiters
    keywords_initial = re.split('[;,.]', keywords_initial)

    #remove space in string (front and end)
    for i in range(len(keywords_initial)):
        keywords_initial[i] = keywords_initial[i].strip()

    keywords_initial = [x for x in keywords_initial if x != '']
    return keywords_initial

def stemming(list):
    list_new = []
    for i in range(len(list)):
        #for j in range(len(list[i])):
        list_stemming=[]
        for word in list[i].split(' '):
            list_stemming.append(porter.stem(word))
        list_new.append(' '.join(list_stemming))
    return list_new

#remove punctuations
def remove_pun(list):
    #define punctuations
    list_new = []
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    for i in range(len(list)):
        # remove punctuation from the string
        no_punct = ""
        for char in list[i]:
            if char not in punctuations:
                no_punct = no_punct + char
        # display the unpunctuated string
        list_new.append(no_punct)
    return list_new


def second_processing_pipeline(text):
    #print("##############################")
    #print("Starting Processing ")
    text = stemming(text)     # step1: stemming
    text = remove_pun(text)   # step2: remove punctuation
    text = [x.lower() for x in text]
    text_list = list(set(text)) # step3: remove duplication
    #print("Processing Finished")
    #print("##############################")
    return text_list

def F1_score(a, b):
    n = len(a)
    m = len(b)
    TP = len(list(set(a) & set(b)))
    precision = TP / n
    recall = TP / m
    if precision + recall > 0:
        F1 = 2 * precision * recall / (precision + recall)
        return F1
    else:
        F1 = 0
        #print("No common keywords")
        return F1

#partial matching
def F11_score(a, b):
    list_a = []
    for i in range(len(a)):
        list1 = a[i].split()
        list_a += list1

    list_b = []
    for j in range(len(b)):
        list2 = b[j].split()
        list_b += list2

    list_a=set(list_a)
    list_b=set(list_b)
    TP = len(list(set(list_a) & set(list_b)))
    precision = TP / len(list_a)
    recall = TP / len(list_b)
    if precision + recall > 0:
        F11 = 2 * precision * recall / (precision + recall)
        return F11
    else:
        F11 = 0
        #print("No common keywords")
        return F11

def yakepara(doc, number, windowsize, threshold, defunction):
    # kw_extractor = KeyBERT('distilbert-base-nli-mean-tokens')
    n  = 15
    kw_extractor = KeywordExtractor(lan="en", n=number, top=n, dedupLim=threshold, dedupFunc=defunction, windowsSize=windowsize)
    keywords_yake = kw_extractor.extract_keywords(text=doc)
    keywords_yake = [x for x, y in keywords_yake]
   # print("running!")
    return keywords_yake

#kw_extractor = KeywordExtractor(lan="en", n=2, top=20, dedupLim=0.9, windowsSize=2)
#array_text = text_p[1]
#       keywords_yake = kw_extractor.extract_keywords(text=array_text)
#        keywords_yake = [x for x, y in keywords_yake]
#        print("running!")
#       keywords_yake


extract_dir = 'E:\Lei\project\paper\yfull\IEEEvis\extraction'
#extract_dir = 'F:\Py project\Y2020\IEEEvis\extraction'
#text = open(extract_dir+'\Extract_abstract_original.txt', 'rt', encoding='UTF-8').read().replace('\n', ' ')

#text = normalization_pipeline(text)
#array_text = [text]

text = open(extract_dir+'\Extract_ducument_original.txt', 'rt', encoding='UTF-8').read()
text_p = text.split('\n')


#with open(extract_dir+'\Extract_keyword_origin.txt', 'r') as file:
    #array_text.append(file.read().replace('\n', ''))
 #   keywords_initial = file.read().replace('\n', '')

#keywords_initial = preprocess1(keywords_initial)
porter = PorterStemmer()
#keywords_initial_pro = second_processing_pipeline(keywords_initial)



## initial keyword txt
## Text normalization for initial keyword

keywords_initial = open(extract_dir+'\Combined_keyword.txt', 'rt', encoding='UTF-8').read().lower()
#keywords_initial = open(extract_dir+'\Extract_keyword_origin.txt', 'rt', encoding='UTF-8').read().lower()

index_term = open(extract_dir+'\Extract_index_terms_origin.txt', 'rt', encoding='UTF-8').read().lower()

keywords_initial_p = keywords_initial.split('\n')
index_term_p = index_term.split('\n')

#yake_extractor = KeywordExtractor(lan="en", n=2, top=20)# top =10 or 20 or 30
best_yake_p=[]
keywords_combine = []
YAKE_score = []
p_yake = {
    'number': [1, 2],
    'window_size': [1, 2, 3],
    'threshold': [0.3, 0.5, 0.7],
    #'threshold': [0.1, 0.3, 0.5],
    #'threshold': [0.9],

    'defunction': ["leve", "jaro", "seqm"]
}

fileforoutput = open('all yearly result2.txt', 'a', encoding='UTF-8')
#for ii in range(len(keywords_initial)):
for ii in range(len(text_p)):
#for ii in range(100):
    keywords_initial1 = keywords_initial_p[ii] #+ ',' + index_term_p[ii] # combine keyword and index term per paper
    #keywords_initial1 = keywords_initial_p[ii]
    keywords_combine.append(preprocess1(keywords_initial1))
    text_p[ii] = normalization_pipeline(text_p[ii])  # normalization for abstract text
    doc = text_p[ii]
    if keywords_combine[-1] == []:
        print('ignore, paper',ii+1,"st has no keywords given\n")

        print(yakepara(doc, 2, 2, 0.7, "leve"))
        keywords_yake = yakepara(doc, 2, 2, 0.7, "leve")
        keywords_yake = ', '.join(keywords_yake)
        fileforoutput.write(keywords_yake)
        fileforoutput.write('\n')
    else:
        print('got it, paper', ii + 1, "st does\n")
        best_yake_score = 0
        for i in p_yake['number']:
          for k in p_yake['window_size']:
             for j in p_yake['threshold']:
                for g in p_yake['defunction']:
                    keywords_yake = yakepara(doc, i, k, j, g)
                    keywords_yake_pro = second_processing_pipeline(keywords_yake)
                # compare F1
                    if keywords_yake_pro != []:
                      yake_score = F1_score(keywords_yake_pro, keywords_combine[-1])
                    else:
                        yake_score = 0
                    if yake_score >= best_yake_score:
                        best_yake_score = yake_score
                        best_yake_p = [i, k, j, g]
        print(yakepara(doc,  best_yake_p[0], best_yake_p[1], best_yake_p[2], best_yake_p[3]))
        keywords_yake=yakepara(doc,  best_yake_p[0], best_yake_p[1], best_yake_p[2], best_yake_p[3])
        keywords_yake = ', '.join(keywords_yake)
        fileforoutput.write(keywords_yake)
        fileforoutput.write('\n')
        fileforoutput = open('all yearly result2.txt', 'a', encoding='UTF-8')
#print(yakepara(doc,  best_yake_p[0], best_yake_p[1], best_yake_p[2], best_yake_p[3])) #print("Running on the:", ii+1, "st paper:")
        print("Best keywords from yake:", keywords_yake[-1])
        print("Best parameters from yake:", best_yake_p)
        print("Best score from yake:", best_yake_score)
        #print("\n")
        YAKE_score.append(best_yake_score)



YAKE_mean=mean(YAKE_score)
print("YAKE Mean", YAKE_mean)


