# flask_api.py
from flask import Flask, request, jsonify
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
from waitress import serve
import sys, argparse

app = Flask(__name__)

# Set up argument parsing
parser = argparse.ArgumentParser(description="Run Flask app with specific models")
parser.add_argument("--embed_model", default="local:BAAI/bge-large-en", help="Embedding model to use")
parser.add_argument("--llm_model", default="llama2:13b", help="LLM model to use")
parser.add_argument("--mode", choices=['debug', 'production'], default="production", help="Run mode: debug or production")
args = parser.parse_args()

# Use arguments
embed_model_arg = args.embed_model
llm_model_arg = args.llm_model
    
# Initialize your model here (simplified for brevity)
def init_model(embed_model_name, llm_model_name):
    documents = SimpleDirectoryReader("data").load_data()
    Settings.embed_model = resolve_embed_model(embed_model_name)
    Settings.llm = Ollama(model=llm_model_name, request_timeout=240.0)
    index = VectorStoreIndex.from_documents(documents)
    print("Model initialized")
    return index.as_query_engine()

print("Starting model initialization with:\n- Embedding Model: ", embed_model_arg, "\n- LLM Model: ", llm_model_arg)
query_engine = init_model(embed_model_arg, llm_model_arg)

@app.route('/query', methods=['POST'])
def handle_query():
    print("Received request")
    data = request.json
    query = data.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    response = query_engine.query(query)
    response = str(response)
    return jsonify({'response': response})

if __name__ == "__main__":
    if args.mode == 'debug':
        # Run the app in debug mode
        app.run(debug=True, port=8000)
    elif args.mode == 'production':
        # Run the app with Waitress in production mode
        serve(app, listen='*:8000')
