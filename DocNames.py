''' 
Boolean Information Retreival System
 
Query priority is as given in the following example

1. Calpurnia and Ceasar or not Brutus --> (Calpurnia and Caesar) or not Brutus

2. calpurnia, and, ceasar --> subQueries = [calpurnia, and, ceasar]

3. not, calpurnia, and, not ceasar --> subQueries = [(not, calpurina), and, (not, ceasar)]

'''

from ast import parse
import os
from unittest import result
import nltk
import pprint
import re

# downloads
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

# naming the lemmatizer
lemmatizer = nltk.WordNetLemmatizer()

dirList = os.listdir()
''' Store names of files in dictionaries '''

# dictionary with documentID as key
documentList = {}

# dictionary with documentName as key, stores the inverted document list
invertedDocumentList = {}
docCounter = 1

for file in dirList:
    # if txt file then 
    if(file[-3:] == "txt"):
        documentList[docCounter] = file
        invertedDocumentList[file] = docCounter
        docCounter += 1

# number of documents
documentCount = len(documentList)

# using the stopwords provided in nltk package
stopWords = set(nltk.corpus.stopwords.words('english'))
stopWords.remove("and")
stopWords.remove("not")

def InvertedIndex(documentList):
    '''Makes a inverted index table and a bigram inverted index table for the documents in the corpus'''
    # input is the document list in the corpus
    InvertedIndexTable = {}
    BiGramInvertedIndex = {}
    
    for docID in documentList:
        # opens and read the doc accessed thru docID
        fo = open(str(documentList[docID]))
        rawText = fo.read()
        
        # splits on the spaces, special chars and numbers in the docs
        words = re.split(r"[\. \\\,\/\?\!\@\#\$\%\^\&\*\(\)\:\{\[\]\}\<\>\t\r\`\~\n\=\:\-\"\'\;\d]", rawText)
        
        # lemmatizing the words obtained from the doc after spliting
        for word in words:
            lemmatizedWord = lemmatizer.lemmatize(word)
            lemmatizedWord = lemmatizedWord.lower()
            
            # skipping the word if it is a stopword
            if lemmatizedWord in stopWords:
                continue
            
            # editing word for bigram inverted index table
            # adding '$' as prefix and suffix to lemmatized word
            biwordinput = '$' + lemmatizedWord + '$'
            
            # if empty string, move to next word
            if biwordinput == '$$':
                continue
            
            # creating a bigram inverted index table
            for i in range(len(biwordinput) - 1):
                biword = biwordinput[i:i+2]
                # if bigram word already present, then append the satisfying the lemmatized word 
                # else bigram not present, add 
                if biword in BiGramInvertedIndex:
                    BiGramInvertedIndex[biword].append(lemmatizedWord)
                else:
                    BiGramInvertedIndex[biword] = [lemmatizedWord]
            
            # creating inverted index table
            # if lemmatized word present, then add the docID of doc containing the lemmatized word(key)
            # else append the docID of doc to lemmatized word as key
            # values of docID is a set to ensuring no duplicates
            if lemmatizedWord in InvertedIndexTable:
                InvertedIndexTable[lemmatizedWord].add(docID)
            else:
                InvertedIndexTable[lemmatizedWord] = set([docID])  
    
    # converting the docIDs set to docIDs list in the dictionary
    for word in InvertedIndexTable:
        InvertedIndexTable[word] = list(InvertedIndexTable[word])
        
    # returns inverted index table and biGram inverted index table
    return InvertedIndexTable, BiGramInvertedIndex


def LevenshteinDistance(str1, str2):
    '''Calculates the LevenshteinDistance or the mininum edit distance'''
    
    # str1 –> first word input
    # str2 –> second word input; 
    str1Length = len(str1)
    str2Length = len(str2)

    # initalizing the matrix for calculating the levenshtein distance
    LevenshteinArray = [[0 for i in range(str2Length+1)] for j in range(str1Length + 1)]
    for i in range(1,str1Length+1):
        LevenshteinArray[i][0] = i
    for i in range(1,str2Length+1):
        LevenshteinArray[0][i] = i
    
    # recursive function to calculate the levenshtein distance
    for i in range(1,str1Length+1):
        for j in range(1,str2Length+1):
            LevenshteinArray[i][j] = min(LevenshteinArray[i-1][j-1] + (0 if str1[i-1] == str2[j-1] else 1), (LevenshteinArray[i-1][j] +1), (LevenshteinArray[i][j-1] +1))
            
    # returns the levenshtein distance between str1 and str2
    return LevenshteinArray[str1Length][str2Length]


def QueryPreProccess(rawQuery):
    '''Pre-processses the rawQuery'''
    
    # Spaces, special chars and numbers removed from the query (as they were removed when making the inverted index table)
    words = re.split(r"[\. \\\,\/\?\!\@\#\$\%\^\&\(\)\:\{\[\]\}\<\>\t\r\`\~\n\=\:\-\"\'\;\d]", rawQuery)
    ind = 0
    
    stoplessWords = []



    # lemmatizing the words in query
    # Query is processed the same way as the words from the doc corpus
    for word in words:
        lemmatizedWord = lemmatizer.lemmatize(word)
        lemmatizedWord = lemmatizedWord.lower()
        if word not in stopWords:
            stoplessWords.append(word)
    
    words = stoplessWords

    for word in words:
        # boolean operation as words and wildcard query symbol(*) in the query are ignored
        if (word in ('and', 'or', 'not')) or ('*' in word) :
            # index increased 
            ind += 1
            continue

        # ans stores the updated queryWord with it's levenshtein distance with the orginial queryWord
        ans = (None, None)
        
        for dictword in InvertedIndex1:
            
            # calculating the levenshtein distance of queryWord and word in the inverted index table
            dist = LevenshteinDistance(word,dictword)
            
            # updates the queryWord with word in inverted index table with minimun levenshtein distance 
            if (ans[1] == None) or (dist <= ans[1]):
                ans = (dictword, dist)
        
        # stores the updated queryWord after spell correction(min levenshtein distance)
        words[ind] = ans[0]
        ind += 1
    
    # final query after skipping stop words and the boolean operation words
    # contains the main queryWords after spell correction
    finalWordList = []
    for word in words:
        if (word not in stopWords) or (word in ('and','or','not')):
            finalWordList.append(word)
            
    # final queryWords to be searched in the corpus
    resultStr = ''
    for word in finalWordList:
        resultStr += word + ' '
        
    # removes the extra space after the last word
    resultStr.strip()
    
    # Returns the querywords as a list after spell correction 
    # and removed the stop words, boolean operation words 
    return resultStr
     
def BigramQuery(word):
    '''Converting input wildcard query for Bi-Gram Query search'''
    # making the query ready for bigram search
    word = '$' + word + '$'
    
    # splits on '*' for wildcard query searches
    wordList = word.split('*')
    
    # empty list
    bigrams = []
    
    # making bigrams from the input wildcardQuery
    for elem in wordList:
        for i in range(len(elem)-1):
            bigrams.append(elem[i:i+2])
    
    # starts with first bi-gram word 
    result = BiGramInvertedIndex[bigrams[0]]
    
    # updates(takes intersection) of the result for all the possible bi-grams of the query
    for i in range(1, len(bigrams)):
        # set to remove duplicates
        result = set(result)
        
        # temp set to store words satisfying the next bi-gram query 
        temp = set(BiGramInvertedIndex[bigrams[i]])
        
        # taking intersection of bi-grams
        result = result.intersection(temp)
        result = list(result)

    # returns bi-grams 
    return result

def BigramSearch(words):
    '''Bi-gram search function'''
    
    result = InvertedIndex1[words[0]]
    for i in range(1, len(words)):
        # set to remove duplicates
        result = set(result)
        
        # temp set to store words satisfying the next bi-gram query 
        temp = set(InvertedIndex1[words[i]])
        
        # taking union of all the queries which satisifed
        result = result.union(temp)
        result = list(result)
    
    # returns list containing biGram matches
    return result

def ParseBoolean(PreprocessedQueryString, invertedIndexTable):
    '''Used for boolean query search'''
    stack = []
    
    for query in PreprocessedQueryString.split():
        stack.append(query)
    
    intermediateResult = invertedIndexTable[stack.pop()]

    # while stack is not empty
    while(stack):
        
        # top element in the stack
        popped_elem = stack.pop()
        
        if(popped_elem == "not"):
            intermediateResult = unaryNot(intermediateResult)
            continue
        
        elif(popped_elem == "or"):
            temporaryResult = invertedIndexTable[stack.pop()]
            intermediateResult = booleanOr(intermediateResult, temporaryResult)
            continue
        
        elif(popped_elem == "and"):
            temporaryResult = invertedIndexTable[stack.pop()]
            intermediateResult = booleanAnd(intermediateResult, temporaryResult)
            continue
        
    ResultDocumentSet = intermediateResult

    # returns
    return ResultDocumentSet

def unaryNot(documentSet):
    '''Unary NOT search'''
    allDocs = set([document for document in range(1, documentCount+1)])
    return list(allDocs.difference(set(documentSet)))

def booleanOr(DocumentSet1, DocumentSet2):
    '''Boolean OR search'''
    DocumentSet1 = set(DocumentSet1)
    DocumentSet2 = set(DocumentSet2)
    
    # returns union of docIDs containing the query(s)
    return list(DocumentSet1.union(DocumentSet2))

def booleanAnd(DocumentSet1, DocumentSet2):
    '''Boolean AND search'''
    DocumentSet1 = set(DocumentSet1)
    DocumentSet2 = set(DocumentSet2)
    
    # returns intersection of docIDs containing the queries
    return list(DocumentSet1.intersection(DocumentSet2))


InvertedIndex1, BiGramInvertedIndex = InvertedIndex(documentList)
'''Making the Inverted Index table and BiGram Inverted Index table for the docs in the corpsus'''

# Driver code
print("Welcome to our Tolerant Boolean Retrieval System (with spelling correction)\n")

choice = int(input("Press 1 for a new query, 0 to quit: "))
while(True):
    if(choice == 1):
        query = input("Enter your query: ")
        
        preProcessedQuery = QueryPreProccess(query)
        
        print("The query being run is: ", preProcessedQuery)
        
        # parsing thru the complete query
        for word in preProcessedQuery.split():
            # determing if any wildcard requests in the query
            if '*' in word:
                wordSet = BigramQuery(word)
                bigramDocList = list(set(BigramSearch(wordSet)))
                InvertedIndex1[word] = bigramDocList

        finalDocList = ParseBoolean(preProcessedQuery, InvertedIndex1)
        print('\n')
        print("The retreived documents that match your query are: ")
        for i in finalDocList:
            print(documentList[i])

        print("\n\n\n\n")

    elif choice == 0:
        break
    else:
        print("\nInvalid input; Please try again")
    
    choice = int(input("Press 1 for a new query, 0 to quit: "))

print("You chose to quit. Thank you\n\n")
