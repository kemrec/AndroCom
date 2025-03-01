import json
import re
from gensim.models import Word2Vec
import numpy as np

def tokenize_code(code_lines):
    """
    Tokenizes code lines into a single list of words.
    """
    tokens = []
    for line in code_lines:
        # Basit bir tokenizasyon işlemi
        tokens.extend(re.findall(r"[A-Za-z_]\w*", line))
    return tokens

def train_word2vec(tokenized_data, vector_size=100, window=5, min_count=1, workers=4):
    """
    Trains a Word2Vec model using the tokenized data.
    """
    model = Word2Vec(
        sentences=tokenized_data,
        vector_size=vector_size,
        window=window,
        min_count=min_count,
        workers=workers
    )
    return model

def vectorize_deleted_lines(deleted_lines, model):
    """
    Converts deleted_lines into a single vector by averaging all word vectors.
    """
    tokens = tokenize_code(deleted_lines)
    vectors = [model.wv[word] for word in tokens if word in model.wv]
    if vectors:
        avg_vector = np.mean(vectors, axis=0)
    else:
        avg_vector = np.zeros(model.vector_size)
    return avg_vector

def process_json_file(input_file, output_file, vector_size=100):
    """
    Processes a JSON file to tokenize, train Word2Vec, and vectorize code lines.
    """
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Tokenize data for Word2Vec training
    tokenized_data = [tokenize_code(entry.get("deleted_lines", [])) for entry in data]

    # Train Word2Vec model
    print("Training Word2Vec model...")
    model = train_word2vec(tokenized_data, vector_size=vector_size)

    # Vectorize deleted_lines
    print("Vectorizing deleted_lines...")
    results = []
    for entry in data:
        vector = vectorize_deleted_lines(entry.get("deleted_lines", []), model)
        results.append({
            "filename": entry["filename"],
            "vector": vector.tolist()
        })

    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"Vektörler {output_file} dosyasına kaydedildi!")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Vektörize deleted_lines into a single vector using Word2Vec.")
    parser.add_argument("--input", required=True, help="Input JSON file path.")
    parser.add_argument("--output", required=True, help="Output JSON file path.")
    parser.add_argument("--vector_size", type=int, default=100, help="Word2Vec vector size.")
    args = parser.parse_args()

    process_json_file(args.input, args.output, args.vector_size)
