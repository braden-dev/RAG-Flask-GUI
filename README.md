# Retrieval Augmented Generation (RAG) Project with Flask and GUI Interface

This project integrates the [Ollama repository](https://github.com/ollama/ollama) and the [LLaMA Index AI open-source project](https://www.llamaindex.ai) to provide a user-friendly interface for querying language models. It allows running a server with a specified embedding model and LLM model, and querying the LLM through a simple GUI.

## Requirements

- Listed in `requirements.txt`

## Installation

1. **Clone the Repository**:

   ```
   git clone <repository-url>
   cd <repository-directory>
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

You can run the server in a headless mode, suitable for production or when no GUI is required. Use the `--mode` argument to specify the running mode (`production` for headless server mode or `debug` for development mode). The `--embed_model` and `--llm_model` arguments are optional and allow you to specify the embedding model and LLM model, respectively.

- **Production Mode**:

  Run the server in production mode using Waitress as the WSGI server. This mode is recommended for production deployments. Ensure that the data for the RAG is placed within the `./data/` directory.

  ```bash
  python flask_rag_api.py --mode production --embed_model <your_embedding_model> --llm_model <your_llm_model>
  ```

  Replace <your_embedding_model> and <your_llm_model> with the actual models you wish to use. If not specified, default models will be used.

- **Debug Mode**:

  For development purposes, you might want to run the server in debug mode, which enables Flask's debugger and auto-reloader.

  ```bash
  python flask_rag_api.py --mode debug
  ```

  The --embed_model and --llm_model arguments are optional in debug mode as well.

### GUI Mode

To interact with the application through a graphical user interface, launch gui_interface.py. This mode allows you to configure embedding and LLM models easily, start the Flask server in your chosen mode, and query the LLM directly from the interface.

```bash
python gui_interface.py
```

The GUI mode simplifies configuration and testing, making it ideal for users who prefer a visual interface for interacting with the application.

## Features

- **Headless Server**: Run the desired LLM model server in a headless mode with command-line arguments for model configuration.
- **GUI Interface**: A user-friendly GUI for configuring models, starting the server, and interacting with the LLM.
- **Dynamic Data Handling**: Place your data in the `./data/` folder to be used with the RAG. Supports various formats as handled by the LLaMA Index AI project.

## Contributing

Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](./LICENSE)
