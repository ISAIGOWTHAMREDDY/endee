import json
from sentence_transformers import SentenceTransformer
from endee_client import EndeeClient
import requests

INDEX_NAME = "arxiv_papers"

# Sample dataset of research paper abstracts
SAMPLE_PAPERS = [
    {
        "id": "paper_1",
        "title": "Attention Is All You Need",
        "authors": "Vaswani et al.",
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."
    },
    {
        "id": "paper_2",
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "authors": "Devlin et al.",
        "abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers."
    },
    {
        "id": "paper_3",
        "title": "Language Models are Few-Shot Learners",
        "authors": "Brown et al.",
        "abstract": "Recent work has demonstrated substantial gains on many NLP tasks and benchmarks by pre-training on a large corpus of text followed by fine-tuning on a specific task. While typically task-agnostic in architecture, this method still requires task-specific fine-tuning datasets of thousands or tens of thousands of examples. By contrast, humans can generally perform a new language task from only a few examples or from simple instructions. We show that scaling up language models greatly improves task-agnostic, few-shot performance, sometimes even reaching competitiveness with prior state-of-the-art fine-tuning approaches."
    },
    {
        "id": "paper_4",
        "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
        "authors": "Lewis et al.",
        "abstract": "Large pre-trained language models have been shown to store factual knowledge in their parameters, and achieve state-of-the-art results when fine-tuned on downstream NLP tasks. However, their ability to access and precisely manipulate knowledge is still limited. We explore a general-purpose fine-tuning recipe for retrieval-augmented generation (RAG) — models which combine pre-trained parametric and non-parametric memory for language generation."
    },
    {
        "id": "paper_5",
        "title": "Llama 2: Open Foundation and Fine-Tuned Chat Models",
        "authors": "Touvron et al.",
        "abstract": "In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters. Our fine-tuned LLMs, called Llama 2-Chat, are optimized for dialogue use cases. Our models outperform open-source chat models on most benchmarks we tested."
    }
]


def ingest_data():
    client = EndeeClient()
    
    if not client.health():
        print("Endee server is not reachable. Please start resolving the server first via docker-compose.")
        return

    print("Loading SentenceTransformer model...")
    # 'all-MiniLM-L6-v2' maps sentences to a 384 dimensional dense vector space
    model = SentenceTransformer('all-MiniLM-L6-v2')
    dim = model.get_sentence_embedding_dimension()

    print(f"Creating index '{INDEX_NAME}' with dimension {dim}...")
    success = client.create_index(index_name=INDEX_NAME, dim=dim, space_type="cosine")
    
    if not success:
        print("Could not create index. Check server logs.")
        return

    print("Embedding documents and preparing for insertion...")
    
    vectors_to_insert = []
    for paper in SAMPLE_PAPERS:
        text_to_embed = f"{paper['title']}: {paper['abstract']}"
        embedding = model.encode(text_to_embed).tolist()
        
        # Meta field stores arbitrary string data.
        # We store the paper info as JSON so we can decode it on retrieval.
        meta_data = {
            "title": paper["title"],
            "authors": paper["authors"],
            "abstract": paper["abstract"]
        }
        
        vector_obj = {
            "id": paper["id"],
            "vector": embedding,
            "meta": json.dumps(meta_data)
        }
        vectors_to_insert.append(vector_obj)
        
    print(f"Inserting {len(vectors_to_insert)} documents into '{INDEX_NAME}'...")
    insert_success = client.insert_vectors(INDEX_NAME, vectors_to_insert)
    
    if insert_success:
        print("Ingestion completed successfully!")
    else:
        print("Error during insertion.")

if __name__ == "__main__":
    ingest_data()
