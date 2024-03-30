# Retrieval Augmented Generation (RAG) with API and GUI Interface

This project integrates the [Ollama repository](https://github.com/ollama/ollama) and the [LLaMAIndex open-source project](https://www.llamaindex.ai) to provide a user-friendly interface for querying language models with RAG. It allows running a server with a specified embedding model and LLM model, and querying the LLM through a simple GUI.

## Requirements

- Listed in `requirements.txt`

## Installation

1. **Clone the Repository**:

   ```
   git clone https://github.com/<GitHub username>/RAG-Flask-GUI.git
   cd RAG-Flask-GUI
   ```

2. **Set Up a Virtual Environment** (optional but recommended):

   - **Python**
     ```
     python -m venv venv
     source venv/bin/activate  # On Windows use `venv\Scripts\activate`
     ```
   - **Conda**
     ```
     conda create --name myenv python=3.10.6 # Exact version not required
     conda activate myenv
     ```

3. **Install Requirements**:

   ```
   pip install -r requirements.txt
   ```

4. **Ollama Installation**:

   Ensure you have the Ollama application installed. Installers can be found [here](https://github.com/ollama/ollama?tab=readme-ov-file#ollama).

## Running the Server

### Headless Server Mode

You can run the server in a headless mode, suitable for production or when no GUI is required by doing:

```bash
python flask_rag_api.py --mode production --embed_model <your_embedding_model> --llm_model <your_llm_model>
```

Use the `--mode` argument to specify the running mode (`production` for a Waitress WSGI server or `debug` for Flask development server). The `--embed_model` and `--llm_model` arguments are optional and allow you to specify the embedding model and LLM model, which default to [local:BAAI/bge-large-en](https://huggingface.co/BAAI/bge-large-en/tree/main) and [llama2:13b](https://ollama.com/library/llama2:13b), respetively.

IndexLlama embedding model support: https://docs.llamaindex.ai/en/stable/module_guides/models/embeddings/#list-of-supported-embeddings

Ollama LLM model support: https://ollama.com/library

- **Production Mode**:

  Run the server in production mode using Waitress as the WSGI server. This mode is recommended for production deployments. Ensure that the data for the RAG is placed within the `./data/` directory.

  ```bash
  python flask_rag_api.py --mode production
  ```

- **Debug Mode**:

  For development purposes, you might want to run the server in debug mode, which enables Flask's debugger and auto-reloader.

  ```bash
  python flask_rag_api.py --mode debug
  ```

### GUI Mode

To interact with the application through a graphical user interface, launch gui_interface.py. This mode allows you to configure embedding and LLM models easily, start the Flask server in your chosen mode, and query the LLM directly from the interface.

```bash
python gui_interface.py
```

The GUI mode simplifies configuration and testing, making it ideal for users who prefer a visual interface for interacting with the application.

Within the GUI there are three tabs:

- Configuration
  - Specify the embedding and LLM model you want to use
  - Select/remove documents for RAG
- Server Control
  - Start/stop the API server (defaults to production mode)
- Query LLM
  - When the API server is running, allows you to talk with the LLM you selected on the Configuration tab

## API

Once the server is initiated in either production or debug mode, it exposes an API endpoint that can be interacted with by sending a `POST` request to `http://127.0.0.1:8000/query`.

### Sending a Query

The body of the request should contain the prompt intended for the LLM, structured as follows:

```json
{
  "query": "<Your prompt goes here>"
}
```

### API Response

Upon successful processing of the request, the API responds with the LLM's answer in the following format:

```json
{
  "response": "<Response from LLM>"
}
```

This structured response allows for straightforward integration and handling of the LLM's output in client applications.

## Features

- **Headless Server**: Run the desired LLM model server in a headless mode with command-line arguments for model configuration.
- **GUI Interface**: A user-friendly GUI for configuring models, starting the server, and interacting with the LLM.
- **API**: Simple API to communicate with the LLM server, allowing for easy integration into other applications or for direct use via HTTP requests. The API supports sending queries to the LLM and receiving responses in JSON format, making it accessible for a wide range of programming languages and tools.
- **Dynamic Data Handling**: Place your data in the `./data/` folder to be used with the RAG. Supports various formats as handled by the LLaMA Index AI project.

## Contributing

Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](./LICENSE)
