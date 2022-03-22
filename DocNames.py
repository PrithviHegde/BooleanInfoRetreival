import os
import nltk
import pprint
import re

#ps = nltk.PorterStemmer()
# naming the lemmatizer
lemmatizer = nltk.WordNetLemmatizer()

# Store names of txt files in dictionaries
dirList = os.listdir()

# dictionary with documentID as key
documentList = {}

# dictionary with documentName as key, stores the inverted document list
invertedDocumentList = {}
docCounter = 1

'''  '''
for i in dirList:
    if(i[-3:] == "txt"):
        documentList[docCounter] = i
        invertedDocumentList[i] = docCounter
        docCounter += 1

#print(documentList, '\n\n\n', invertedDocumentList)
#print(documentList[15])
################################################
documentCount = len(documentList)


''' 
Query input function, input is the query and returns the individual words of query in a list.
for example: 
calpurnia AND ceasar --> ['calpurnia', 'and', 'ceasar']
Calpurnia AND Ceasar OR NOT Brutus --> ['calpurnia', 'and', 'ceasar', 'or', 'not', 'brutus']

Query priority is as given in the following example
Calpurnia and Ceasar or not Brutus --> (Calpurnia and Caesar) or not Brutus

subQueries: 
1. calpurnia, and, ceasar --> subQueries = [calpurnia, and, ceasar]
2. calpurnia, and, not, ceasar --> subQueries = [calpurnia, and, (not, ceasar)]
3. not, calpurnia, and, not ceasar --> subQueries = [(not, calpurina), and, (not, ceasar)]
4. subqery, and, calpurnia 
'''
def inputQuery(query):
    query = input("Enter your query: ")
    queryList = []

    # splits on space
    for q in query.split():
        queryList.append(q.lower())
    # queryList now contains the individual words of the query
    return queryList

# using the stopwords provided in nltk package?
stopWords = set(nltk.corpus.stopwords.words('english'))

''' InvertedIndex function, input is the document list in the corpus and returns inverted index table(dictionary) '''
def InvertedIndex(documentList):
    InvertedIndexTable = {}
    for docID in documentList:
        # opens and read the doc accessed thru docID
        fo = open(str(documentList[docID]))
        rawText = fo.read()
        
        # splits on the space, special chars and numbers in the docs
        words = re.split(r"[\. \\\,\/\?\!\@\#\$\%\^\&\*\(\)\:\{\[\]\}\<\>\t\r\`\~\n\=\:\-\"\'\;\d]", rawText)
        
        # lemmatizing the words obtained from the doc after removing the space, special chars and numbers
        for word in words:
            lemmatizedWord = lemmatizer.lemmatize(word)
            lemmatizedWord = lemmatizedWord.lower()
            # skipping the word if it is a stopword
            if lemmatizedWord in stopWords:
                continue
            
            # if lemmatized word not present in the inverted index table
            #   then lemmatized words as key and the docID of doc containing it
            #   (values of docID is a set to ensuring no duplicates)
            # else if present, then add the docID of doc containing the lemmatized word(key)
            if lemmatizedWord in InvertedIndexTable:
                InvertedIndexTable[lemmatizedWord].add(docID)
            else:
                InvertedIndexTable[lemmatizedWord] = set([docID])  
    
    # converting the docIDs set to docIDs list in the dictionary
    for word in InvertedIndexTable:
        InvertedIndexTable[word] = list(InvertedIndexTable[word])
        
    # returning the complete inverted index table
    return InvertedIndexTable


# making the invertedIndexTable of the docs in the corpus
InvertedIndex1 = InvertedIndex(documentList)

''' 
Function to calculate the LevenshteinDistance or the mininum edit distance;
used for spell check
takes two strings as input, 
    str1 --> first word
    str2 --> second word;
returns the levenshtein distance between str1 and str2
'''
def LevenshteinDistance(str1, str2):
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

    return LevenshteinArray[str1Length][str2Length]

'''
Function to pre-process the query.
Input is the raw query.
Query is processed the same way as the words from the doc corpus
Query goes thru spell check using the levenshtein distance between the query word and words present in the inverted index table
Return the querywords as a list after spell correction and removing the stop words, bit operation words 
'''
def normalQuery(rawQuery):
    # Spaces, special chars and numbers removed from the query (as they were removed when making the inverted index table)
    words = re.split(r"[\. \\\,\/\?\!\@\#\$\%\^\&\*\(\)\:\{\[\]\}\<\>\t\r\`\~\n\=\:\-\"\'\;\d]", rawQuery)
    ind = 0
    
    # lemmatizing the words in query
    for word in words:
        lemmatizedWord = lemmatizer.lemmatize(word)
        lemmatizedWord = lemmatizedWord.lower()
        
        # bit operation as words in the query are ignored
        if word in ('and', 'or', 'not'):
            # index increased as bit operation remain the same after spell check of the queries
            ind += 1
            continue

        # ans stores the updated queryWord with it's levenshtein distance with the orginial queryWord
        ans = (None, None)
        
        for dictword in InvertedIndex1:
            
            # calculating the levenshtein distance of query word and word in the inverted index table
            dist = LevenshteinDistance(word,dictword)
            
            # updates the queryWord with word in inverted index table with minimun levenshtein distance 
            if (ans[1] == None) or (dist <= ans[1]):
                ans = (dictword, dist)
        
        # stores the updated queryWord after spell correction(min levenshtein distance)
        words[ind] = ans[0]
        ind += 1
    
    # list for the final query after skipping stop words and the bit operation words
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
    
    return resultStr
    
''' Trie class and TrieNode '''
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
# for key in InvertedIndex1:
    # if key.isalpha():
        # t.insert(key)
# print(t.search("erafwevgwer"))


'''
Function for booleanQuery search
Input is Pre-processed query string and inverted index table
Returns 
'''
def ParseBoolean(PreprocessedQueryString, invertedIndexTable):
    # stack
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



# Driver code

# get query input
query = input("Enter a query: ")

# preprocessing the query
preprocessedQuery = normalQuery(query)

print("Showing Results for: ", preprocessedQuery)

# 
print(ParseBoolean(preprocessedQuery, InvertedIndex1))

