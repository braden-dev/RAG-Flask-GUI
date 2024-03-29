# flask_api.py
from flask import Flask, request, jsonify
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
import sys

app = Flask(__name__)

# Read arguments from command line
embed_model_arg = sys.argv[1] if len(sys.argv) > 1 else "local:BAAI/bge-large-en"
llm_model_arg = sys.argv[2] if len(sys.argv) > 2 else "llama2:13b"
    
# Initialize your model here (simplified for brevity)
def init_model(embed_model_name, llm_model_name):
    documents = SimpleDirectoryReader("data").load_data()
    Settings.embed_model = resolve_embed_model(embed_model_name)
    Settings.llm = Ollama(model=llm_model_name, request_timeout=240.0)
    index = VectorStoreIndex.from_documents(documents)
    return index.as_query_engine()

print("Starting model initialization with embed_model: ", embed_model_arg, " and llm_model: ", llm_model_arg)
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

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
