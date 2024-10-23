# FastChat over Ollama - README

## Overview
This project provides an interactive interface to communicate with a large language model (LLM) using the `ollama` Python library. It allows users to maintain a running conversation with the LLM, including features like saving and loading chat history, setting custom system prompts, and configuring various options such as the LLM model type and chat history length.

The project is built to manage conversational state intelligently, making it easy to continue interactions over time, even across multiple sessions.

## Features
- **Chat History Management**: Tracks user and model responses while allowing you to enable, disable, or truncate the history.
- **System Prompts**: Add system-level messages to guide the LLM's behavior consistently throughout the chat.
- **Model Configuration**: Dynamically change the model used for conversation or provide a custom name for display.
- **Save and Load Conversations**: Save the state of a conversation, including history, model settings, and system prompts, to resume later.
- **Flexible Commands**: A variety of commands are available to configure the conversation and history in real time.

## Requirements
- Python 3.x
- Libraries: `ollama`, `colorama`, `termcolor`

Install the required libraries via pip:
```sh
pip install ollama colorama termcolor
```

## Configuration

The configuration is handled through a config.txt file, which should be placed in the same directory as the script. The file should have the following structure:

```
OllamaServerURL=192.168.1.35
OllamaServerPort=11434
DefaultContextLength=128000
DefaultModelName=llama3.1:70b
DefaultHistoryEnabled=True
DefaultCustomModelName=CustomLLM
DefaultSystemPrompt=This is a default system prompt.
```

## Usage
The script provides an interactive prompt where users can type messages to the LLM or use various commands to control and configure the chat experience.

### Running the Script
To start the interactive chat, simply run:
```sh
python interactive_chat.py
```

### Commands
Here are the available commands for managing the interactive chat:
- `/history` - Show if chat history is enabled or disabled
- `/history enable` - Enable chat history
- `/history disable` - Disable chat history
- `/length` - Show the current maximum token length for history
- `/length [number]` - Set the maximum token length for history
- `/model` - Show the current LLM model in use
- `/model [name]` - Set a new model for the LLM
- `/name` - Show the current custom name for the LLM
- `/name [name]` - Set a custom name for the LLM
- `/system [message]` - Set a system prompt that is retained in the chat
- `/save [name]` - Save the current chat history and configuration to a file
- `/load [name]` - Load chat history and configuration from a file
- `/lastcontext` - Show the last truncated part of the conversation
- `/exit` - Exit the chat
- `/help` - Show a list of available commands

## Example
Here is an example of a typical session:
1. Start the script.
2. Type `/model llama3.1:70b` to switch to the specified model.
3. Enter `/system Please answer in a friendly tone.` to provide a system prompt.
4. Have a conversation with the LLM by typing your messages.
5. Save your progress using `/save session1`.
6. Load a saved session using `/load session1`.

## System Prompts
The system prompt helps set the context or behavior for the LLM across the entire session. Use `/system` to specify instructions for the model that affect its tone, format, or other behaviors.

## Error Handling
- If you attempt to load a non-existent session, the script will notify you.
- If tokens exceed the allowed limit, older parts of the conversation (except system prompts) are truncated, with warnings provided.

## Color-Coded Interaction
- **User Messages**: Displayed in **green**.
- **Model Responses**: Displayed in **magenta**.
- **System Prompts**: Displayed in **cyan**.

This helps distinguish between the user, the assistant, and system-level instructions visually, enhancing the interactive experience.

## Contributing
Contributions are welcome! Feel free to fork the repository and make pull requests. Please ensure that all features are well-tested.

## License
This project is licensed under the MIT License. Feel free to use and modify it as needed.


### Note
All of the code and README file is written by ChatGPT (GPT-4o with Canvas).
