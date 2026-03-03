import json
import math
from collections import Counter

def calculate_tfidf(tokens_list):
    """
    Calculate TF-IDF matrix for a list of token lists.
    Returns: list of TF-IDF vectors (dicts: token -> score)
    """
    # Flatten all tokens to get unique vocabulary
    all_tokens = set()
    for tokens in tokens_list:
        all_tokens.update(tokens)
    
    vocab = sorted(list(all_tokens))
    
    # Calculate document frequency (how many docs contain each token)
    doc_freq = Counter()
    for tokens in tokens_list:
        doc_tokens = set(tokens)
        for token in doc_tokens:
            doc_freq[token] += 1
    
    num_docs = len(tokens_list)
    
    # Calculate TF-IDF for each document
    tfidf_vectors = []
    for tokens in tokens_list:
        term_freq = Counter(tokens)
        tfidf = {}
        
        for token in vocab:
            tf = term_freq.get(token, 0) / len(tokens) if tokens else 0
            idf = math.log(num_docs / (1 + doc_freq.get(token, 0)))
            tfidf[token] = tf * idf
        
        tfidf_vectors.append(tfidf)
    
    return tfidf_vectors, vocab


def cosine_similarity(vec1, vec2, vocab):
    """
    Calculate cosine similarity between two TF-IDF vectors.
    """
    dot_product = sum(vec1.get(token, 0) * vec2.get(token, 0) for token in vocab)
    
    mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
    mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
    
    if mag1 == 0 or mag2 == 0:
        return 0
    
    return dot_product / (mag1 * mag2)


def get_related_posts(current_tokens, siteurls_file='data/siteurls.json'):
    """
    Find 3-5 related posts based on TF-IDF cosine similarity.
    
    Args:
        current_tokens: list of keywords from the current post
        siteurls_file: path to siteurls.json
    
    Returns:
        list of dicts: [{"title": ..., "url": ..., "anchor_text": ...}, ...]
    """
    try:
        with open(siteurls_file, 'r', encoding='utf-8') as f:
            posts = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
    if not posts:
        return []
    
    # Extract tokens from all existing posts
    existing_tokens_list = [post.get('tfidf_tokens', []) for post in posts]
    
    if not existing_tokens_list:
        return []
    
    # Calculate TF-IDF vectors
    tfidf_vectors, vocab = calculate_tfidf(existing_tokens_list + [current_tokens])
    
    current_vector = tfidf_vectors[-1]  # Last vector is the new post
    existing_vectors = tfidf_vectors[:-1]
    
    # Calculate similarities
    similarities = []
    for idx, post in enumerate(posts):
        score = cosine_similarity(current_vector, existing_vectors[idx], vocab)
        if score > 0.1:  # Threshold to avoid noise
            similarities.append((idx, score, post))
    
    # Sort by score descending, take top 5, limit to 3-5 results
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_similar = similarities[:5]
    
    # Format results
    results = []
    for idx, score, post in top_similar:
        results.append({
            'title': post.get('title', 'مقال بدون عنوان'),
            'url': post.get('url', '/'),
            'anchor_text': post.get('title', 'مقال')
        })
    
    return results
