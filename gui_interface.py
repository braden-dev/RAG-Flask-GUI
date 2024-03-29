# gui_interface.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import requests, os, shutil, subprocess, threading, json, time
from functools import partial

# Global vars
FLASK_APP_PATH = 'flask_rag_api.py'
data_folder = './data/'
# Placeholder for the Flask process
flask_process = None
# Global flag to control the "Thinking..." message updating
is_thinking = False

def select_files():
    file_paths = filedialog.askopenfilenames(title="Select Documents")
    if file_paths:
        lbl_documents.config(text="\n".join(file_paths))
    return file_paths
        

def add_documents():
    file_paths = filedialog.askopenfilenames(title="Select Documents")
    if file_paths:        
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
    # Check if the data directory exists, create it if it doesn't
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
            
    # Fill the listbox with files from the data folder
    for filename in os.listdir(data_folder):
        lb_documents.insert(tk.END, filename)      

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
def update_conversation_log(prompt, response, replace_last=False):
    conversation_log.config(state=tk.NORMAL)
    if replace_last:
        # Delete the last two lines (user's prompt and the "Thinking..." message)
        conversation_log.delete("end-1l", tk.END)
    # Insert the user's prompt again only if it's being replaced
    # if replace_last:
    #     conversation_log.insert(tk.END, "You: " + prompt + "\n")
    # Insert the response or "Thinking..." message
    conversation_log.insert(tk.END, "\nLLM: " + response + "\n\n")
    conversation_log.see(tk.END)  # Auto-scroll to the end of the log
    conversation_log.config(state=tk.DISABLED)

def update_thinking_message():
    global is_thinking
    is_thinking = True
    dots = 0
    # Insert an initial "Thinking..." message
    conversation_log.config(state=tk.NORMAL)
    conversation_log.insert(tk.END, "LLM: Thinking\n\n")
    conversation_log.config(state=tk.DISABLED)
    # Remember the starting line of "Thinking..." for replacement
    start_line = conversation_log.index("end-3l")
    
    while is_thinking:
        thinking_message = "LLM: Thinking" + "." * (dots % 4) + "\n\n"
        # Schedule the update on the main thread
        def update_message():
            if is_thinking:  # Ensure we should still update
                conversation_log.config(state=tk.NORMAL)
                # Replace the "Thinking..." message directly
                conversation_log.delete(start_line, "end-1c")
                conversation_log.insert(start_line, thinking_message)
                # conversation_log.see(tk.END)
                conversation_log.config(state=tk.DISABLED)
        root.after(0, update_message)
        dots += 1
        time.sleep(0.5)
    # Clear the "Thinking..." message once done
    if not is_thinking:
        conversation_log.config(state=tk.NORMAL)
        conversation_log.delete(start_line, "end-1c")
        conversation_log.config(state=tk.DISABLED)


def send_query_thread(prompt):
    def query_backend():
        global is_thinking
        # Start the "Thinking..." animation in a separate thread
        threading.Thread(target=update_thinking_message, daemon=True).start()
        try:
            response = requests.post('http://127.0.0.1:5000/query', json={'query': prompt}) 
            is_thinking = False  # Stop the "Thinking..." animation
            if response.status_code == 200:
                # Use partial to pass arguments to the function called by after
                time.sleep(1)
                func_call = partial(update_conversation_log, prompt, response.json()['response'], replace_last=True) 
                root.after(0, func_call)
            else:
                # Handle errors similarly with partial
                error_message = f"Failed to get response: {response.status_code}"
                time.sleep(1)
                func_call = partial(update_conversation_log, prompt, error_message, replace_last=True)
                root.after(0, func_call)
        except requests.exceptions.RequestException as e:
            is_thinking = False  # Stop the "Thinking..." animation
            messagebox.showerror("Error", str(e))
    threading.Thread(target=query_backend, daemon=True).start()

def on_query():
    user_prompt = user_input.get("1.0", tk.END).strip()
    if user_prompt:
        # Immediately show the user's prompt
        conversation_log.config(state=tk.NORMAL)
        conversation_log.insert(tk.END, "You: " + user_prompt + "\n")
        conversation_log.config(state=tk.DISABLED)
        send_query_thread(user_prompt)
        user_input.delete("1.0", tk.END)  # Clear the input area after sending the query
        
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        stop_flask_server()  # Stop the server if it's running
        root.destroy()


# Define dark theme colors
dark_theme = {
    'background': '#2D2D2D',
    'foreground': '#CCCCCC',
    'button_background': '#393939',
    'button_foreground': '#CCCCCC',
    'entry_background': '#333333',
    'entry_foreground': '#CCCCCC',
    'text_background': '#333333',
    'text_foreground': '#CCCCCC',
}

# Initialize root window
root = tk.Tk()
root.title("LLM RAG Configuration")
root.configure(bg=dark_theme['background'])
root.protocol("WM_DELETE_WINDOW", on_closing) # Stop the server when the window is closed

# Create and configure a ttk style
style = ttk.Style()
style.theme_use('default')  # 'alt', 'default', 'classic', or 'clam' might also work depending on the platform

# Configure the colors for ttk widgets
style.configure('TFrame', background=dark_theme['background'])
style.configure('TLabel', background=dark_theme['background'], foreground=dark_theme['foreground'])
style.configure('TButton', background=dark_theme['button_background'], foreground=dark_theme['button_foreground'])
style.map('TButton', background=[('active', dark_theme['button_background'])])

# Style for Entry widget is not directly available in ttk, so it's styled as tk Entry

# Create notebook
notebook = ttk.Notebook(root)
config_tab = ttk.Frame(notebook)  # No need to set background here; it follows the style
server_tab = ttk.Frame(notebook)
query_llm_tab = ttk.Frame(notebook)

notebook.add(config_tab, text='Configuration')
notebook.add(server_tab, text='Server Control')
notebook.add(query_llm_tab, text='Query LLM')
notebook.pack(expand=True, fill='both')

# Configuration tab components
embedding_label = ttk.Label(config_tab, text="Enter Embedding Model:")
embedding_label.pack()

entry_embed_model = tk.Entry(config_tab, bg=dark_theme['entry_background'], fg=dark_theme['entry_foreground'], insertbackground=dark_theme['foreground'], width=50)
entry_embed_model.pack()
entry_embed_model.insert(0, "local:BAAI/bge-large-en")

llm_label = ttk.Label(config_tab, text="Enter LLM Model:")
llm_label.pack()

entry_llm_model = tk.Entry(config_tab, bg=dark_theme['entry_background'], fg=dark_theme['entry_foreground'], insertbackground=dark_theme['foreground'], width=50)
entry_llm_model.pack()
entry_llm_model.insert(0, "llama2:13b")

btn_add_docs = ttk.Button(config_tab, text="Add Documents for RAG", command=add_documents)
btn_add_docs.pack()

btn_delete_doc = ttk.Button(config_tab, text="Delete Selected Document", command=delete_selected_document)
btn_delete_doc.pack()

lb_documents = tk.Listbox(config_tab, bg=dark_theme['text_background'], fg=dark_theme['text_foreground'])
lb_documents.pack(fill=tk.BOTH, expand=True)

update_document_list() # Update the document list on startup

# Start Flask server button in the server tab
btn_start_flask = tk.Button(server_tab, text="Start Flask Server", bg=dark_theme['button_background'], fg=dark_theme['button_foreground'], command=start_flask_app)
btn_start_flask.pack()

# Stop Flask server button in the server tab
btn_stop_flask = tk.Button(server_tab, text="Stop Flask Server", bg=dark_theme['button_background'], fg=dark_theme['button_foreground'], command=stop_flask_server)
btn_stop_flask.pack()

# Toggle log console button in the server tab
btn_toggle_log = tk.Button(server_tab, text="Toggle Log Console", bg=dark_theme['button_background'], fg=dark_theme['button_foreground'], command=toggle_log_console)
btn_toggle_log.pack()

# Log frame in the server tab
log_frame = tk.Frame(server_tab, bg=dark_theme['background'])
log_frame.pack(fill=tk.BOTH, expand=True)

log_console = scrolledtext.ScrolledText(log_frame, bg=dark_theme['text_background'], fg=dark_theme['text_foreground'], state='disabled', height=8)
log_console.pack(fill=tk.BOTH, expand=True)

# Chat history log
conversation_log = scrolledtext.ScrolledText(query_llm_tab, bg=dark_theme['text_background'], fg=dark_theme['text_foreground'], state='normal', height=15)
conversation_log.pack(fill=tk.BOTH, expand=True)
conversation_log.insert(tk.END, "Conversation with LLM:\n\n")
conversation_log.config(state='disabled')  # Make the log read-only

# User input area
user_input = tk.Text(query_llm_tab, bg=dark_theme['text_background'], fg=dark_theme['text_foreground'], height=4)
user_input.pack(fill=tk.BOTH, expand=False)

# Query button
query_button = tk.Button(query_llm_tab, text="Query", bg=dark_theme['button_background'], fg=dark_theme['button_foreground'], command=on_query)
query_button.pack(side=tk.RIGHT)


root.mainloop()
