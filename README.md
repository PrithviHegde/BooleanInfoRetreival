## Tolerant Boolean Information Retreival System
This program is an implementation of a tolerant boolean information retreival system.
Usage:
Run the `Code.py`  file. This is a menu driven interactive program which allows users to enter queries.
Please note that the documents which need to be searched should be in the same folder/directory as `Code.py`.
 
**Functions and their uses:**
 
`InvertedIndex(documentList)`
		Functions that takes a dictionary named `documentList` (which has key value pairs of the form { documentID : documentName } ), and returns and Inverted Index table for all the words in the corpus as well as a Bi Word Inverted index table.
		ex: 
		 if `documentList = {1:'FirstDocument'}`
	     then `InvertedIndex(documentList)` returns
		 `{ 'This' : [1],
		'is' : [1],
		'the' : [1],
		'first' : [1],
		'document' : [1]
		} `
 
 
`QueryPreProccess(rawQuery)`
		Function that takes in the raw query and returns a preprocessed query string, after implementing stop word removal, tokenization, lemmatization, and spelling correction.
		ex:
		`QueryPreProccess("c*s to and california or brutus")`
		returns
		`"c*s and calphurnia or brutus"`
 
`ParseBoolean(PreprocessedQueryString, invertedIndexTable)`
		Function that takes the Preprocessed Query String and the Inverted Index Table, performs the search and returns a list of all the Document IDs that match our query.
		ex:
		`ParseBoolean("c*s and calphurnia or brutus", invertedIndexTable)`
		returns
		`[3, 5, 39, 7, 11, 14, 15, 19, 30]`
