import os
import re

import spacy
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import numpy as np

spacy_nlp = None
stop_words = None
sbert_model = None
wikipedia_titles = None


def get_stop_words(lang='fr'):
    global stop_words

    if stop_words == None:
        print('Loading stopwords..')
        if lang.startswith('fr'):
            with open('/usr/src/app/keyword_extraction/data/stopwords_fr') as f:
                stop_words = [w.strip() for w in f]
        elif lang.startswith('en'):
            with open('/usr/src/app/keyword_extraction/data/stopwords_en') as f:
                stop_words = [w.strip() for w in f]
        else:
            raise Exception('Language not supported')

    return stop_words


def get_spacy_model(lang='fr'):
    global spacy_nlp

    if spacy_nlp == None:
        print('Loading SpaCy..')
        if lang.lower().startswith('fr'):
            spacy_nlp = spacy.load('fr_core_news_md')
        elif lang.lower().startswith('en'):
            spacy_nlp = spacy.load('en_core_web_md')
        else:
            raise Exception('Language not supported')
    
    
    return spacy_nlp


def get_sbert_model(lang='fr'):
    global sbert_model

    if sbert_model == None:
        print('Loading SentenceBert..')
        if lang.startswith('en'):
            model_name = "all-MiniLM-L6-v2"
        elif lang.startswith('fr'):
            model_name = "paraphrase-multilingual-MiniLM-L12-v2"
        else:
            raise Exception('Language not supported')
        sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    return sbert_model


def get_wikipedia_titles(lang='fr'):
    global wikipedia_titles

    if wikipedia_titles == None:
        print('Loading Wikipedia titles..')
        wikipedia_titles = []
        
        if lang.startswith('fr'):
            for file in os.listdir('/usr/src/app/keyword_extraction/data/wikipedia_titles/'):
                if file.startswith('wiki-fr'):
                    with open('/usr/src/app/keyword_extraction/data/wikipedia_titles/' + file) as f:
                        wikipedia_titles.extend([w.strip() for w in f if len(w.split()) < 6])
        elif lang.startswith('en'):
            for file in os.listdir('/usr/src/app/keyword_extraction/data/wikipedia_titles/'):
                if file.startswith('wiki-en'):
                    with open('/usr/src/app/keyword_extraction/data/wikipedia_titles/' + file) as f:
                        wikipedia_titles.extend([w.strip() for w in f if len(w.split()) < 6])
        else:
            raise Exception('Language not supported')
        
    return set(wikipedia_titles)


def filter_tf_cadidates(words_counter, conv_pos_tags, stopwords, valid_wikipedia_articles):
    result = []
    for kws, score in words_counter:
        words = kws.split(' ')
        # starts_with_preposition
        # ends with preposition
        if any([conv_pos_tags[w] == 'NOUN' or conv_pos_tags[w] == 'PROPN' for w in words]) and \
           any([w not in stopwords for w in words]) and \
           conv_pos_tags[words[0]] != 'VERB' and \
            kws in valid_wikipedia_articles:
            while kws[:2] in ['à '] or \
                  kws[:3] in ['le ', 'la ', 'un ', 'de ', 'du ', 'en ', 'au ', 'on ', 'ma ', 'ta ', 'sa '] or \
                  kws[:4] in ['les ', 'des ', 'une ', 'par ', 'pas ', 'mon ', 'ton ', 'son ', 'mes ', 'tes ', 'ses ', 'nos ', 'vos ', 'sur '] or \
                  kws[:5] in ['leur ', 'sous ', 'dans ', 'hors ', 'lors '] or \
                  kws[:6] in ['votre ', 'notre ', 'leurs ']:
                kws = ' '.join(kws.split(' ')[1:])
            result.append((kws, score))
    return result


def get_frekeybert_keywords(doc, config):
    n_segs = config.get('number_of_segments', 10)
    top_candidates = config.get('top_candidates', 50)
    verbose = config.get('verbose', False)
    top_n = config.get('top_n', len(doc.split()))

    language = os.environ.get("LANGUAGE", "fr")

    sbert = get_sbert_model(language) if 'sbert_model' not in config else SentenceTransformer(config['sbert_model'])
    stopwords = get_stop_words(language) if 'stopwords' not in config else config['stopwords']

    if 'add_stopwords' in config:
        stopwords.extend(config['add_stopwords'])
    
    keywords = extract_frekeybert_keywords(doc, n_segs=n_segs, 
                                           nlp=get_spacy_model(language), 
                                           sbert_model=sbert, 
                                           stopwords = stopwords,
                                           top_n=top_n,
                                           wikipedia_titles=get_wikipedia_titles(language), 
                                           top_candidates=top_candidates, 
                                           verbose=verbose)

    return dict(keywords)

def extract_frekeybert_keywords(text, n_segs=10, nlp=spacy_nlp, sbert_model=sbert_model, 
                            stopwords = stop_words, top_n=20,
                            wikipedia_titles=wikipedia_titles, top_candidates=50, verbose=False):
    if(verbose):
        print('# Tokenization and POS extraction through SpaCy[fr_core_news_md]..')
    text = re.sub(' +', ' ', text)
    doc = nlp(text.lower())
    pos_tags = {}
    for token in doc:
        if token.text not in pos_tags:
            pos_tags[token.text] = []
        pos_tags[token.text].append(token.pos_)
    for word in pos_tags:
        pos_tags[word] = Counter(pos_tags[word]).most_common()[0][0]
        
    if(verbose):
        print('# Extract word an d n-gram counts..')
    tf_keywords = []
    counter = CountVectorizer(ngram_range=(1, 3), lowercase= True, stop_words=[], tokenizer=lambda s: s.split(' '))
    X = counter.fit_transform([' '.join(tok.text for tok in doc)])
    for x in X.toarray():
        tf_keywords = sorted([(w, s) for s, w in zip(x, counter.get_feature_names_out())], key=lambda x: -x[1])    
        
    if(verbose):
        print('# Filter out non-valid keywords (no nouns, all stopwords, valid Wikipedia title, remove particles from beginning)')
    kept_keywords = filter_tf_cadidates(tf_keywords, pos_tags, stopwords, wikipedia_titles)

    if(verbose):
        print('# Fuse smaller keywords into the longest frequent one')
    fused_keywords = {}
    swallowed = set()
    trigrams = [(w, s) for w, s in kept_keywords if len(w.split()) == 3]
    bigrams  = [(w, s) for w, s in kept_keywords if len(w.split()) == 2]
    unigrams = [(w, s) for w, s in kept_keywords if len(w.split()) == 1]

    for u, s1 in unigrams:
        for b, s2 in bigrams:
            if u in b and s1 <= s2 * 2:
                swallowed.add(u)
                break

    for b, s1 in bigrams:
        for t, s2 in trigrams:
            if b in t and s1 <= s2 * 2:
                swallowed.add(b)
                break
    for w, s in trigrams + bigrams + unigrams:
        if w not in swallowed:
            score = max(s, max([0] + [dict(kept_keywords)[sw] for sw in swallowed if sw in w]))
            fused_keywords[w] = score

    fused_keywords = sorted(fused_keywords.items(), key=lambda e: -e[1])

    if(verbose):
        print('# Compute keywords embeddings..')
    sbert_embeddings = {}
    for w,s  in kept_keywords:
        # print('> Compute embedding for ' + w + '..')
        sbert_embeddings[w] = sbert_model.encode(w).reshape(1, -1) # np.zeros((1, 100))# 
    
    if(verbose):
        print('# Compute Keywords per segment of the document')
    
    context_size = len(text.split()) // n_segs
    sliding_window = context_size // n_segs

    doc_keywords = {}
    for i in range(n_segs):
        start = max(0, context_size*i - sliding_window)
        end = min(len(text.split()), context_size*(i+1) + sliding_window)

        doc_i = ' '.join(text.split()[start:end])
        doc_i_emb = sbert_model.encode([doc_i]) # np.zeros((1, 100)) # 

        scored_by_doc_i = {}
        for w, s in fused_keywords:
            scored_by_doc_i[w] = float(cosine_similarity(doc_i_emb, sbert_embeddings[w])[0][0])

        for w, s in scored_by_doc_i.items():
            doc_keywords[w] = s if w not in doc_keywords else max(doc_keywords[w], s)
            
    if(verbose):
        print('# Removing redundant keywords (plurals, synonym..) via embedding similarity')
    top_keywords = sorted(doc_keywords.items(), key=lambda x: -x[1])[:top_candidates]
    skip = set()

    for i, (w1, s1) in enumerate(top_keywords):
        for w2, s2 in top_keywords[i+1:]:
            if cosine_similarity(sbert_embeddings[w1], sbert_embeddings[w2])[0][0] > 0.9:
                # print(w1, 'and', w2, 'are similar, skipping', w2)
                skip.add(w2)

    final_keywords = {w:s for w, s in top_keywords if w not in skip}

    if(verbose):
        print('Done! Returning ' + str(len(final_keywords)) + ' keywords.')
    return sorted(final_keywords.items(), key=lambda x: -x[1])[:top_n]