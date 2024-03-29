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

- **Headless Server Mode**:

  You can run the server without the GUI by launching `flask_rag_api.py` with the desired embedding model and LLM model as arguments. Ensure that the data for the RAG is placed within the `./data/` directory.

  ```
  python flask_rag_api.py <embedding_model> <llm_model>
  ```

- **GUI Mode**:

  Launch `gui_interface.py` to use the graphical user interface for setting the embeddings and LLM models, starting the Flask server, and querying the LLM.

  ```
  python gui_interface.py
  ```

## Features

- **Headless Server**: Run the desired LLM model server in a headless mode with command-line arguments for model configuration.
- **GUI Interface**: A user-friendly GUI for configuring models, starting the server, and interacting with the LLM.
- **Dynamic Data Handling**: Place your data in the `./data/` folder to be used with the RAG. Supports various formats as handled by the LLaMA Index AI project.

## Contributing

Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](./LICENSE)
