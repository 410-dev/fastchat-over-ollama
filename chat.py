from ollama import Client
import queue
import json
import os
from termcolor import cprint
import colorama

# Initialize colorama for Windows compatibility
colorama.init()

contextExceedNoticed: bool = False
contextExceeded: bool = False
lastTruncated: str = ""
custom_name: str = ""
system_prompt: str = ""
ollama_server_url: str = ""
ollama_server_port: str = ""

def load_config(filename="config.txt"):
    config = {}
    if os.path.exists(filename):
        with open(filename, "r") as file:
            for line in file:
                key, value = line.strip().split("=", 1)
                config[key.strip()] = value.strip()
    return config

# Load configuration
config = load_config()

# Set defaults if not provided in the config
ollama_server_url = config.get('OllamaServerURL')
ollama_server_port = config.get('OllamaServerPort')
if not ollama_server_url or not ollama_server_port:
    print("Unable to start: OllamaServerURL and OllamaServerPort must be explicitly specified in config.txt!!")
    exit(0)

default_context_length = int(config.get('DefaultContextLength', 128000))
default_model_name = config.get('DefaultModelName', 'llama3.1:70b')
default_history_enabled = config.get('DefaultHistoryEnabled', 'True').lower() == 'true'
default_custom_model_name = config.get('DefaultCustomModelName', '')
default_system_prompt = config.get('DefaultSystemPrompt', '')

# History management class to keep track of conversation
class ChatHistory:
    def __init__(self, max_tokens=default_context_length):
        self.history = []
        self.max_tokens = max_tokens
        self.include_history = default_history_enabled

    def add(self, user_input=None, model_output=None, role='user'):
        """Add user input and model output to the history."""
        if self.include_history:
            if role == 'user' and user_input is not None and model_output is not None:
                self.history.append({'user': user_input, 'assistant': model_output})
            elif role == 'system' and user_input is not None:
                self.history.append({'system': user_input})
            self.truncate_history()

    def truncate_history(self):
        """Remove older conversations beyond the token limit, except for system prompts."""
        global lastTruncated
        global contextExceeded
        global contextExceedNoticed
        while self.get_total_tokens() > self.max_tokens:
            # Find the first non-system message to remove
            for i in range(len(self.history)):
                if 'system' not in self.history[i]:
                    contextExceeded = True
                    lastRemovedHistory = self.history.pop(i)  # Remove the oldest non-system conversation
                    lastTruncated = f"User: {lastRemovedHistory.get('user', '')}\nAssistant: {lastRemovedHistory.get('assistant', '')}"
                    break

        if contextExceeded and not contextExceedNoticed:
            print("WARNING: Context exceeded!")
            contextExceedNoticed = True

    def get_total_tokens(self):
        """Estimate the total tokens in the current history."""
        token_count = 0
        for chat in self.history:
            if 'user' in chat and 'assistant' in chat:
                token_count += len(chat['user'].split()) + len(chat['assistant'].split())
            elif 'system' in chat:
                token_count += len(chat['system'].split())
        return token_count

    def get_history_messages(self):
        """Return the entire chat history as an array of messages."""
        messages = []
        if self.include_history:
            for chat in self.history:
                if 'user' in chat:
                    messages.append({"role": "user", "content": chat['user']})
                if 'assistant' in chat:
                    messages.append({"role": "assistant", "content": chat['assistant']})
                if 'system' in chat:
                    messages.append({"role": "system", "content": chat['system']})
        return messages

    def toggle_history(self, state=None):
        """Enable, disable, or view the current status of including history in the chat."""
        if state is None:
            status = "enabled" if self.include_history else "disabled"
            print(f"Chat history is currently {status}.")
        elif state.lower() == 'enable':
            self.include_history = True
            print("Chat history enabled.")
        elif state.lower() == 'disable':
            self.include_history = False
            print("Chat history disabled.")

    def set_max_tokens(self, length=None):
        """Set the maximum token length for history or display the current length."""
        if length is None:
            print(f"Current history token length is {self.max_tokens}.")
        else:
            try:
                if int(length) > self.max_tokens:
                    global contextExceeded
                    global contextExceedNoticed
                    global lastTruncated
                    contextExceeded = False
                    contextExceedNoticed = False
                    lastTruncated = None
                    print("History trigger reset.")
                self.max_tokens = int(length)
                print(f"History token length set to {length}.")
            except ValueError:
                print("Invalid length value.")

    def save_history(self, name, model_name, custom_name, system_prompt):
        """Save the current chat history and configuration."""
        data = {
            'history': self.history,
            'max_tokens': self.max_tokens,
            'include_history': self.include_history,
            'model_name': model_name,
            'contextExceeded': contextExceeded,
            'contextExceedNoticed': contextExceedNoticed,
            'lastTruncated': lastTruncated,
            'custom_name': custom_name,
            'system_prompt': system_prompt
        }
        with open(f"{name}.json", "w") as file:
            json.dump(data, file, indent=4)
        print(f"Chat history saved as '{name}'.")

    def load_history(self, name):
        """Load chat history and configuration from a file."""
        global contextExceeded
        global contextExceedNoticed
        global lastTruncated
        global custom_name
        global system_prompt
        try:
            with open(f"{name}.json", "r") as file:
                data = json.load(file)
                self.history = data['history']
                self.max_tokens = data['max_tokens']
                self.include_history = data['include_history']
                contextExceeded = data['contextExceeded']
                contextExceedNoticed = data['contextExceedNoticed']
                lastTruncated = data['lastTruncated']
                custom_name = data.get('custom_name', '')
                system_prompt = data.get('system_prompt', '')
                print(f"Chat history '{name}' loaded successfully.")
                print(f"Model: {data['model_name']}, Max Tokens: {self.max_tokens}, History Included: {self.include_history}, Custom Name: {custom_name}, System Prompt: {system_prompt}")
                print(f"Last Truncated: {lastTruncated}")
                # Print the loaded conversation with color coding
                for chat in self.history:
                    if 'user' in chat:
                        cprint(f"You: {chat['user']}", 'green')
                        print()
                        print()
                    if 'assistant' in chat:
                        cprint(f"{custom_name if custom_name else data['model_name']}: {chat['assistant']}", 'magenta')
                        print()
                        print()
                    if 'system' in chat:
                        cprint(f"System: {chat['system']}", 'cyan')
                        print()
                        print()
        except FileNotFoundError:
            print(f"No saved chat history found with the name '{name}'.")

# Chat interface function
def interactive_chat():

    global system_prompt
    global custom_name

    history = ChatHistory()
    model_name = default_model_name
    custom_name = default_custom_model_name
    system_prompt = default_system_prompt
    client = Client(host=f"http://{ollama_server_url}:{ollama_server_port}")

    print("Welcome to the interactive LLM chat. Type /help for a list of commands.")

    while True:
        cprint("You: ------------------------------", 'green')
        user_input = input("")

        # Handle commands
        if user_input.startswith("/history"):
            parts = user_input.split(maxsplit=1)
            action = parts[1] if len(parts) > 1 else None
            history.toggle_history(action)
            continue
        elif user_input.startswith("/length"):
            parts = user_input.split(maxsplit=1)
            length = parts[1] if len(parts) > 1 else None
            history.set_max_tokens(length)
            continue
        elif user_input.startswith("/model"):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                model_name = parts[1]
                print(f"Model set to: {model_name}")
            else:
                print(f"Current model: {model_name}")
            continue
        elif user_input.startswith("/name"):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                custom_name = parts[1]
                print(f"Custom name set to: {custom_name}")
            else:
                print(f"Current custom name: {custom_name if custom_name else 'None'}")
            continue
        elif user_input.startswith("/save"):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                history.save_history(parts[1], model_name, custom_name, system_prompt)
            else:
                print("Please provide a name for the save.")
            continue
        elif user_input.startswith("/load"):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                history.load_history(parts[1])
            else:
                print("Please provide the name of the saved chat history to load.")
            continue
        elif user_input.startswith("/system"):
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                system_prompt = parts[1]
                history.add(user_input=system_prompt, role='system')
                print(f"System prompt set: {system_prompt}")
            else:
                print("Current System Prompt:")
                cprint(f"{system_prompt}", 'cyan')
            continue
        elif user_input == "/help":
            print("""
Available commands:
    /history - Show if chat history is enabled or disabled
    /history enable - Enable chat history
    /history disable - Disable chat history
    /length - Show the current maximum token length for history
    /length [number] - Set maximum token length for history
    /model - Show current model
    /model [name] - Set current model
    /name - Show current custom name
    /name [name] - Set a custom name to display for the model
    /system [message] - Set a system prompt that is retained in the chat
    /save [name] - Save current chat history and configuration
    /load [name] - Load chat history and configuration
    /lastcontext - Show last truncated context
    /exit - Exit the chat
    /help - Show this help message
            """)
            continue
        elif user_input == "/lastcontext":
            global lastTruncated
            global contextExceeded
            if not contextExceeded:
                print("No context dropped.")
                continue
            else:
                print(f"Last truncated context: {lastTruncated}")
                continue
        elif user_input == "/exit":
            print("Goodbye!")
            break
        elif user_input.startswith("/"):
            print("Unknown command.")
            continue

        # Get the history messages to maintain context
        history_messages = history.get_history_messages()

        # Send the messages to the LLM, including the system prompt
        if system_prompt:
            history_messages.insert(0, {"role": "system", "content": system_prompt})

        history_messages.append({"role": "user", "content": user_input})

        # Send the messages to the LLM
        try:
            stream = client.chat(
                model=model_name,
                messages=history_messages,
                stream=True
            )

            strBuild: str = ""
            print()
            print()
            cprint(f"{custom_name if custom_name else model_name} ---------------------", 'magenta')
            for chunk in stream:
                # Collect the response
                model_output = chunk['message']['content']
                print(model_output, end='', flush=True)
                strBuild += f"{model_output}"
            print()
            print()
            print()
            model_output = strBuild

            # Add user and model messages to history
            history.add(user_input, model_output)
        except Exception as e:
            print(f"Model failed: {e}")


if __name__ == "__main__":
    interactive_chat()
