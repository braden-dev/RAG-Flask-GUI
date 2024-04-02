from flask import Flask, request, jsonify
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama

app = Flask(__name__)

# Initialize your model here (simplified for brevity)
def init_model():
  documents = SimpleDirectoryReader("data-pdf").load_data()
  # Different embedding models:
  # - Salesforce/SFR-Embedding-Mistral
  # - BAAI/bge-small-en-v1.5
  Settings.embed_model = resolve_embed_model("local:BAAI/bge-large-en")
  Settings.llm = Ollama(model="llama2:13b", request_timeout=240.0)
  index = VectorStoreIndex.from_documents(documents)
  return index.as_query_engine()

query_engine = init_model()

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
  app.run(debug=True)
