# flask_api.py
from flask import Flask, request, jsonify
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.embeddings import resolve_embed_model
from llama_index.llms.ollama import Ollama
from llama_index.core.evaluation import FaithfulnessEvaluator
from waitress import serve
import sys, argparse

from llama_index.core.prompts import LangchainPromptTemplate
from langchain import hub

langchain_prompt = hub.pull("rlm/rag-prompt")
# print("LangChain Prompt:", langchain_prompt.messages[0].prompt.template)
new_template = """
You are an assistant for question-answering tasks. 
Based on the Trail Life Health and Safety Guide provided, answer the question succinctly.
If uncertain, state that the answer is unknown.
You must not infer or deduce answers based on external knowledge or assumptions. If an answer is not directly observable in the Trail Life Health and Safety Guide, you are to reply, "That information is not available to me, if you believe it should be in the document please read it to confirm."
Use up to three sentences for a concise response.
If the answer is in the context given, include the location of your answer from the document the format "Location: Page <page number>", "Location: Section <section number>", etc.

Question: {question}
Context: {context}
Answer:
"""

# new_template = """
# You are an assistant dedicated to providing answers to questions by closely examining the context given. Your role involves adhering to the following guidelines meticulously:

# Answer Precision: For every question, generate a succinct answer directly from the provided context. Limit your response to three sentences to ensure brevity and directness.
# Uncertainty Protocol: If you cannot find a clear answer within the provided context, explicitly state, "The answer is unknown based on the given context."
# Context-Only Responses: You must not infer or deduce answers based on external knowledge or assumptions. If an answer is not directly observable in the context, you are to reply, "That information is not available to me, if you believe it should be in the document please read it to confirm." This ensures answers are grounded solely in the provided text.
# Location Reference: When providing answers found within the context, always include a reference to the source location, such as "Location: Page <page number>", "Location: Section <section number>", or any other specific locator applicable. This helps in verifying the source of your answers.
# Given this framework, address the following:

# Question: {question}
# Context: {context}
# Answer:
# """
langchain_prompt.messages[0].prompt.template = new_template

lc_prompt_tmpl = LangchainPromptTemplate(
    template=langchain_prompt,
    template_var_mappings={"query_str": "question", "context_str": "context"},
)

app = Flask(__name__)

# Set up argument parsing
parser = argparse.ArgumentParser(description="Run Flask app with specific models")
parser.add_argument("--embed_model", default="local:BAAI/bge-large-en", help="Embedding model to use")
parser.add_argument("--llm_model", default="llama2:13b-chat", help="LLM model to use")
parser.add_argument("--mode", choices=['debug', 'production'], default="production", help="Run mode: debug or production")
args = parser.parse_args()

# Use arguments
embed_model_arg = args.embed_model
llm_model_arg = args.llm_model
    
# Initialize the model
def init_model(embed_model_name, llm_model_name):
    documents = SimpleDirectoryReader("data").load_data()
    Settings.embed_model = resolve_embed_model(embed_model_name)
    Settings.llm = Ollama(model=llm_model_name, request_timeout=240.0)
    index = VectorStoreIndex.from_documents(documents)
    print("Model initialized")
    return index.as_query_engine()

print("Starting model initialization with:\n- Embedding Model: ", embed_model_arg, "\n- LLM Model: ", llm_model_arg)
query_engine = init_model(embed_model_arg, llm_model_arg)

query_engine.update_prompts(
    {"response_synthesizer:text_qa_template": lc_prompt_tmpl}
)

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
