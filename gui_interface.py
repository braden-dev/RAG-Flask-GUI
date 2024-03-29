# gui_interface.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import requests, os, shutil, subprocess, threading, json

FLASK_APP_PATH = 'flask_rag_api_from_gui.py'

def select_files():
    file_paths = filedialog.askopenfilenames(title="Select Documents")
    if file_paths:
        lbl_documents.config(text="\n".join(file_paths))
    return file_paths
        
data_folder = './data/'

def add_documents():
    file_paths = filedialog.askopenfilenames(title="Select Documents")
    if file_paths:
        # Check if the data directory exists, create it if it doesn't
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        
        for file_path in file_paths:
            try:
                # Copy the selected files to the data folder
                shutil.copy(file_path, data_folder)
                update_document_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add documents: {e}")
                return

def delete_selected_document():
    selected_document = lb_documents.get(tk.ANCHOR)
    if selected_document:
        try:
            os.remove(os.path.join(data_folder, selected_document))
            update_document_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete document: {e}")

def update_document_list():
    # Clear the listbox
    lb_documents.delete(0, tk.END)
    # Fill the listbox with files from the data folder
    for filename in os.listdir(data_folder):
        lb_documents.insert(tk.END, filename)
      

# Placeholder for the Flask process
flask_process = None

def start_flask_app():
    global flask_process
    if flask_process is not None and flask_process.poll() is None:
        messagebox.showinfo("Flask Server", "Flask server is already running.")
        return

    def run_flask():
        embed_model_name = entry_embed_model.get() or "local:BAAI/bge-large-en"
        llm_model_name = entry_llm_model.get() or "llama2:13b"
        global flask_process
        flask_process = subprocess.Popen(
            ['python', FLASK_APP_PATH, embed_model_name, llm_model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Redirect stderr to stdout
            text=True,  # Open the pipes in text mode
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        for line in iter(flask_process.stdout.readline, ''):
            log_console.config(state=tk.NORMAL)
            log_console.insert(tk.END, line)
            log_console.see(tk.END)  # Auto-scroll
            log_console.config(state=tk.DISABLED)
        # After the process ends, safely close the streams
        if flask_process:
            flask_process.stdout.close()
            flask_process.wait()

    threading.Thread(target=run_flask, daemon=True).start()

def stop_flask_server():
    global flask_process
    if flask_process is not None:
        flask_process.terminate()
        try:
            flask_process.wait(timeout=10)  # Wait for the Flask process to terminate
        except subprocess.TimeoutExpired:
            flask_process.kill()  # Force kill if not terminated within timeout
        log_console.config(state=tk.NORMAL)
        log_console.insert(tk.END, "Flask server stopped.\n")
        log_console.see(tk.END)
        log_console.config(state=tk.DISABLED)
        flask_process = None

def toggle_log_console():
    if log_visible.get():
        log_frame.pack_forget()  # Hide the console
    else:
        log_frame.pack(fill=tk.BOTH, expand=True)  # Show the console
    log_visible.set(not log_visible.get())
    
# Function to update the conversation log in the GUI
def update_conversation_log(prompt, response):
    conversation_log.config(state=tk.NORMAL)
    conversation_log.insert(tk.END, "You: " + prompt + "\n")
    conversation_log.insert(tk.END, "LLM: " + response + "\n\n")
    conversation_log.see(tk.END)  # Auto-scroll to the end of the log
    conversation_log.config(state=tk.DISABLED)

# Function to send the query without freezing the GUI
def send_query_thread(prompt):
    def query_backend():
        try:
            response = requests.post('http://127.0.0.1:5000/query', json={'query': prompt})
            if response.status_code == 200:
                # Run update in the main thread
                root.after(0, update_conversation_log, prompt, response.json()['response'])
            else:
                messagebox.showerror("Error", f"Failed to get response: {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", str(e))
    # Start the backend query in a separate thread
    threading.Thread(target=query_backend, daemon=True).start()

# Function to handle the "Query" button click
def on_query():
    user_prompt = user_input.get("1.0", tk.END).strip()
    if user_prompt:
        send_query_thread(user_prompt)
        user_input.delete("1.0", tk.END)  # Clear the input area after sending the query
        
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        stop_flask_server()  # Stop the server if it's running
        root.destroy()


root = tk.Tk()
root.title("LLaMA RAG Configuration")
log_visible = tk.BooleanVar(value=True)  # State variable for log visibility
notebook = ttk.Notebook(root)
root.protocol("WM_DELETE_WINDOW", on_closing) # Stop the server when the window is closed

config_tab = ttk.Frame(notebook)
server_tab = ttk.Frame(notebook)
query_llm_tab = ttk.Frame(notebook)

notebook.add(config_tab, text='Configuration')
notebook.add(server_tab, text='Server Control')
notebook.add(query_llm_tab, text='Query LLM')
notebook.pack(expand=True, fill='both')

# Embedding model entry in the config tab
embedding_label = tk.Label(config_tab, text="Enter Embedding Model:")
embedding_label.pack()
entry_embed_model = tk.Entry(config_tab)
entry_embed_model.pack()
entry_embed_model.insert(0, "local:BAAI/bge-large-en")

# LLaMA model entry in the config tab
llama_label = tk.Label(config_tab, text="Enter LLaMA Model:")
llama_label.pack()
entry_llm_model = tk.Entry(config_tab)
entry_llm_model.pack()
entry_llm_model.insert(0, "llama2:13b")

# Add documents button in the config tab
btn_add_docs = tk.Button(config_tab, text="Add Documents for RAG", command=add_documents)
btn_add_docs.pack()

# Delete selected document button in the config tab
btn_delete_doc = tk.Button(config_tab, text="Delete Selected Document", command=delete_selected_document)
btn_delete_doc.pack()

# Listbox to display documents in the config tab
lb_documents = tk.Listbox(config_tab)
lb_documents.pack(fill=tk.BOTH, expand=True)

# Start Flask server button in the server tab
btn_start_flask = tk.Button(server_tab, text="Start Flask Server", command=start_flask_app)
btn_start_flask.pack()

# Stop Flask server button in the server tab
btn_stop_flask = tk.Button(server_tab, text="Stop Flask Server", command=stop_flask_server)
btn_stop_flask.pack()

# Toggle log console button in the server tab
btn_toggle_log = tk.Button(server_tab, text="Toggle Log Console", command=toggle_log_console)
btn_toggle_log.pack()

# Log frame in the server tab
log_frame = tk.Frame(server_tab)
log_frame.pack(fill=tk.BOTH, expand=True)
log_console = scrolledtext.ScrolledText(log_frame, state='disabled', height=8)
log_console.pack(fill=tk.BOTH, expand=True)

# Chat history log
conversation_log = scrolledtext.ScrolledText(query_llm_tab, state='normal', height=15)
conversation_log.pack(fill=tk.BOTH, expand=True)
conversation_log.insert(tk.END, "Conversation with LLM:\n\n")
conversation_log.config(state='disabled')  # Make the log read-only

# User input area
user_input = tk.Text(query_llm_tab, height=4)
user_input.pack(fill=tk.BOTH, expand=False)

# Query button
query_button = tk.Button(query_llm_tab, text="Query", command=on_query)
query_button.pack(side=tk.RIGHT)

root.mainloop()
