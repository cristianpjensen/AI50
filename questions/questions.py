import nltk
import sys
import os
import string
import math
from copy import deepcopy

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    dictionary = dict()

    data = os.listdir(directory)
    for document in data:
        with open(os.path.join(directory, document), 'r', encoding='utf8') as text:
            dictionary[document] = text.read()

    return dictionary


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """    
    token = nltk.word_tokenize(document.lower())

    for word in token[:]:
        if word in nltk.corpus.stopwords.words('english'):
            token.remove(word)

    for word in token[:]:
        for punctuation in string.punctuation:
            if word == punctuation:
                token.remove(word)

    return token


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    idfs = dict()
    documents_copy = deepcopy(documents)
    num_docs = len(documents.keys())

    for document in documents_copy:
        for word in documents_copy[document]:
            num_docs_containing_word = 0

            for document, words in documents_copy.items():
                if word in words:
                    num_docs_containing_word += 1

                    # Remove all instances of `word`.
                    words[:] = [x for x in words if x != word]

            idf = math.log(num_docs / num_docs_containing_word)
            idfs[word] = idf

    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    scores = dict()
    best_files = list()

    for word in query:
        for document, words in files.items():
            tf = words.count(word)

            if document not in scores:
                scores[document] = 0

            scores[document] += (tf * idfs[word])

    num_files = 0
    while n > num_files:
        best_score = 0
        best_document = str()

        for document, score in scores.items():
            if score > best_score:
                best_score = score
                best_document = document

        best_files.append(best_document)
        num_files += 1

    return best_files


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    top_sentences = list()
    scores = dict()

    for sentence, words in sentences.items():
        for q_word in query:
            if q_word in words:

                if sentence not in scores:
                    scores[sentence] = 0

                scores[sentence] += idfs[q_word]

    sorted_scores = {k: v for k, v in sorted(scores.items(), 
                                             key=lambda item: item[1], 
                                             reverse=True)}

    for i in range(n):
        if (sorted_scores[list(sorted_scores.keys())[i]] == 
                sorted_scores[list(sorted_scores.keys())[i + 1]]):
            sentence0 = list(sorted_scores.keys())[i]
            sentence1 = list(sorted_scores.keys())[i + 1]

            query_words0 = 0
            query_words1 = 0

            for q_word in query:
                for word in sentences[sentence0]:
                    if q_word == word:
                        query_words0 += 1

            for q_word in query:
                for word in sentences[sentence1]:
                    if q_word == word:
                        query_words1 += 1

            query_term_density0 = query_words0 / len(sentences[sentence0])
            query_term_density1 = query_words1 / len(sentences[sentence1])

            if query_term_density0 > query_term_density1:
                top_sentences.append(sentence0)
            else:
                top_sentences.append(sentence1)

        else:
            top_sentences.append(list(sorted_scores.keys())[i])

    return top_sentences


if __name__ == "__main__":
    main()
