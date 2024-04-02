from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama

documents = SimpleDirectoryReader("data-pdf").load_data()

# bge embedding model
Settings.embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")

# ollama
Settings.llm = Ollama(model="llama2:13b", request_timeout=240.0)

index = VectorStoreIndex.from_documents(
    documents,
)

query_engine = index.as_query_engine()
response = query_engine.query("What page of the TailLife HSG is Flatwater BOATING on?")
print(response)