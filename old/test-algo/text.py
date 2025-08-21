# text.py: Module for text processing, independent of essay grading
#
# TODO:
# - Add support for resolving HTML/XML entities (e.g., "India&rsquo;s slums" => "India's slums")
# - Move NLTK support here (e.g., part-of-speech tagging, tokenization, etc.).
#

# Local packages
#
from common import *
debug_print("algo/standard.py: " + debug_timestamp())
import wordnet

# Other packages
#
import nltk

# preprocess(text, [use_part_of_speech=False]): Preprocesses TEXT string, returning list
# of words optionally with WordNet part-of-speech indicator.
# preprocess("The lawyer defended his client to the death.")
#
def preprocess(text, use_part_of_speech):
    # Tokenize and part-of-speech tag
    text_tokens = nltk.word_tokenize(full_text_proper)
    part_of_speech_tagged_words =  nltk.pos_tag(text_tokens)
    text_words = [nltk.corpus.wordnet.morphy(word.lower()) for (word, tag) in part_of_speech_tagged_words]
    text_words_proper = list(word for word in text_words if word)
    # Optionally prefix each word with WordNet part-of-speech indicator (e.g., ['fast', 'car'] => ['a:fast', 'n:car'])
    if use_part_of_speech:
        text_words_proper = [wordnet.get_part_of_speech(tag) + ":" + word
                             for (word, (token, tag)) in zip(text_words, part_of_speech_tagged_words) 
                             if word]
    return text_words_proper
