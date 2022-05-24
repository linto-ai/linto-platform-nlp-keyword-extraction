import string
from collections import Counter
from typing import Dict, Any

def preprocess(s):
    stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your',
                  'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'just', 'don', 
                  'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'now',
                  'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'can', 'will', 
                  'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'should', 'how', 
                  'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'no', 
                  'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
                  'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about',
                  'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 
                  'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 
                  'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 
                  'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 
                  'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't']
    s = s.lower()
    s = s.translate(str.maketrans('', '', string.punctuation))
    words = [t for t in s.split(' ') if t not in stop_words and t != '']
    return words
    
    
def get_word_frequencies(doc: str) -> Dict[str: int]:
    words = preprocess(doc)
    return dict(Counter(words).most_common())
