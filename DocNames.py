import os
import nltk
import pprint
import re

#ps = nltk.PorterStemmer()
lemmatizer = nltk.WordNetLemmatizer()

#Store names of txt files in dictionaries

dirList = os.listdir()

# Has DocumentID as key
documentList = {}

# Has DocumentName as key
invertedDocumentList = {}
docCounter = 1

for i in dirList:
    
    if(i[-3:] == "txt"):
        documentList[docCounter] = i
        invertedDocumentList[i] = docCounter
        docCounter += 1

#print(documentList, '\n\n\n', invertedDocumentList)
#print(documentList[15])
################################################
documentCount = len(documentList)
#Query input

def inputQuery(query):
    query = input("Enter your query: ")

    queryList = []

    # splits on space
    for q in query.split():
        queryList.append(q.lower())
    #QueryList now contains the individual words of the query

    #print(queryList)

    # Calpurnia and Ceasar or not Brutus --> (Calpurnia and Caesar) or not Brutus
    '''# AND:
        1. calpurnia, and, ceasar --> subQueries = [calpurnia, and, ceasar]
        2. calpurnia, and, not, ceasar --> subQueries = [calpurnia, and, (not, ceasar)]
        3. not, calpurnia, and, not ceasar --> subQueries = [(not, calpurina), and, (not, ceasar)]
        4. subqery, and, calpurnia 
    '''
    # if boolean search
 
            
    # wildcard searches; query will have * like cea*, *cea, bru*us, b*u*u*, *r*thu*
            
    return queryList

stopWords = set(nltk.corpus.stopwords.words('english'))


def InvertedIndex(documentList):
    InvertedIndexTable = {}
    for docID in documentList:
        fo = open(str(documentList[docID]))
        rawText = fo.read()
        words = re.split(r"[\. \\\,\/\?\!\@\#\$\%\^\&\*\(\)\:\{\[\]\}\<\>\t\r\`\~\n\=\:\-\"\'\;\d]", rawText)
        #words = rawText.split(".", " ", "?", "{", "}", "/", "\t", "\n", "\r", "\\", "")
        # try the stemmer tokensiation etc 
        #words = nltk.word_tokenize(rawText)
        
        for word in words:
            #stemmedWord = ps.stem(word)
            lemmatizedWord = lemmatizer.lemmatize(word)
            lemmatizedWord = lemmatizedWord.lower()
            if lemmatizedWord in stopWords:
                continue
            # remove stop words and useless
            if lemmatizedWord in InvertedIndexTable:
                InvertedIndexTable[lemmatizedWord].add(docID)
            else:
                InvertedIndexTable[lemmatizedWord] = set([docID])  
    
    for word in InvertedIndexTable:
        InvertedIndexTable[word] = list(InvertedIndexTable[word])
        
    return InvertedIndexTable


InvertedIndex1 = InvertedIndex(documentList)



def LevenshteinDistance(str1, str2):
    str1Length = len(str1)
    str2Length = len(str2)

    LevenshteinArray = [[0 for i in range(str2Length+1)] for j in range(str1Length + 1)]
    for i in range(1,str1Length+1):
        LevenshteinArray[i][0] = i
    for i in range(1,str2Length+1):
        LevenshteinArray[0][i] = i

    for i in range(1,str1Length+1):
        for j in range(1,str2Length+1):
            LevenshteinArray[i][j] = min(LevenshteinArray[i-1][j-1] + (0 if str1[i-1] == str2[j-1] else 1), (LevenshteinArray[i-1][j] +1), (LevenshteinArray[i][j-1] +1))

    return LevenshteinArray[str1Length][str2Length]

#Preprocessing Query
def normalQuery(rawQuery):
    words = re.split(r"[\. \\\,\/\?\!\@\#\$\%\^\&\*\(\)\:\{\[\]\}\<\>\t\r\`\~\n\=\:\-\"\'\;\d]", rawQuery)
    ind = 0
    for word in words:
        #stemmedWord = ps.stem(word)
        lemmatizedWord = lemmatizer.lemmatize(word)
        lemmatizedWord = lemmatizedWord.lower()
        if word in ('and', 'or', 'not'):
            ind+=1
            continue

        # (word, edit dist)
        ans = (None,None)
        for dictword in InvertedIndex1:
            dist = LevenshteinDistance(word,dictword)
            if (ans[1] == None) or (dist <= ans[1]):
                ans = (dictword,dist)
        words[ind] = ans[0]
        ind+=1
    finalWordList = []
    for word in words:
        if (word not in stopWords) or (word in ('and','or','not')):
            finalWordList.append(word)
    resultStr = ''
    for word in finalWordList:
        resultStr += word+' '
    resultStr.strip()
    return resultStr
    
class TrieNode:
     
    # Trie node class
    def __init__(self):
        self.children = [None]*26
 
        # isEndOfWord is True if node represent the end of the word
        self.isEndOfWord = False

class Trie:
     
    # Trie data structure class
    def __init__(self):
        self.root = self.getNode()
 
    def getNode(self):
     
        # Returns new trie node (initialized to NULLs)
        return TrieNode()
 
    def _charToIndex(self,ch):
         
        # private helper function
        # Converts key current character into index
        # use only 'a' through 'z' and lower case
         
        return ord(ch)-ord('a')
 
 
    def insert(self,key):
         
        # If not present, inserts key into trie
        # If the key is prefix of trie node,
        # just marks leaf node
        pCrawl = self.root
        length = len(key)
        for level in range(length):
            index = self._charToIndex(key[level])
 
            # if current character is not present
            if not pCrawl.children[index]:
                pCrawl.children[index] = self.getNode()
            pCrawl = pCrawl.children[index]
 
        # mark last node as leaf
        pCrawl.isEndOfWord = True
 
    def search(self, key):
         
        # Search key in the trie
        # Returns true if key presents
        # in trie, else false
        pCrawl = self.root
        length = len(key)
        for level in range(length):
            index = self._charToIndex(key[level])
            if not pCrawl.children[index]:
                return False
            pCrawl = pCrawl.children[index]
 
        return pCrawl.isEndOfWord
 

t = Trie()

'''for key in InvertedIndex1:
    if key.isalpha():
        t.insert(key)

print(t.search("erafwevgwer"))'''


#Parse Tree
def ParseBoolean(PreprocessedQueryString, invertedIndexTable):
    stack = []
    for query in PreprocessedQueryString.split():
        stack.append(query)
    
    intermediateResult = invertedIndexTable[stack.pop()]


    while(stack):
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

    return ResultDocumentSet

def unaryNot(documentSet):
    allDocs = set([document for document in range(1, documentCount+1)])
    return list(allDocs.difference(set(documentSet)))

def booleanOr(DocumentSet1, DocumentSet2):
    DocumentSet1 = set(DocumentSet1)
    DocumentSet2 = set(DocumentSet2)
    return list(DocumentSet1.union(DocumentSet2))

def booleanAnd(DocumentSet1, DocumentSet2):
    DocumentSet1 = set(DocumentSet1)
    DocumentSet2 = set(DocumentSet2)
    return list(DocumentSet1.intersection(DocumentSet2))


query = input("Enter a query: ")
preprocessedQuery = normalQuery(query)
print("Showing Results for: ", preprocessedQuery)
print(ParseBoolean(preprocessedQuery, InvertedIndex1))

