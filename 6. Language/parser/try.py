sentence = input("sentence: ")
sentence = sentence.lower()

if all(not char.isalpha() for char in sentence):
    quit()

print(sentence)