import openai


class ChatGPTPersona:
    def __init__(self, api_key: str, persona: str):
        """
        Initializes the ChatGPT with a specific persona.

        :param api_key: Your OpenAI API key.
        :param persona: A string describing the persona the bot should take on.
        """
        self.api_key = api_key
        self.persona = persona

        # Set up OpenAI API
        openai.api_key = self.api_key

        # Initial system message to set the persona for the conversation
        self.messages = [
            {"role": "system", "content": f"You are {self.persona}. Please respond accordingly."}
        ]

    def _get_response(self) -> str:
        """
        Sends the accumulated conversation to OpenAI's API and returns the assistant's reply.

        :return: The response from ChatGPT.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # You can choose another model (like gpt-4)
                messages=self.messages,
                temperature=0.7,  # Adjust the temperature for creativity
                max_tokens=150
            )
            message = response['choices'][0]['message']['content']
            return message
        except Exception as e:
            return f"Error: {e}"

    def ask(self, user_input: str) -> str:
        """
        Adds the user's input to the conversation and returns ChatGPT's response.

        :param user_input: The message from the user.
        :return: ChatGPT's reply based on the persona and the conversation so far.
        """
        # Add user input to the conversation history
        self.messages.append({"role": "user", "content": user_input})

        # Get and return the response from ChatGPT
        return self._get_response()

    def reset_conversation(self):
        """
        Resets the conversation history, keeping the persona intact.
        Useful for starting a new conversation with the same persona.
        """
        self.messages = [
            {"role": "system", "content": f"You are {self.persona}. Please respond accordingly."}
        ]


# Example Usage
if __name__ == "__main__":
    # Replace 'your_openai_api_key' with your actual API key
    chat_gpt_persona = ChatGPTPersona(api_key="your_openai_api_key", persona="a friendly and helpful librarian")

    # Ask a question
    user_message = "Can you tell me about the history of programming?"
    response = chat_gpt_persona.ask(user_message)
    print(f"ChatGPT (as a librarian): {response}")

    # Ask another question
    user_message = "What are the best resources to learn Python?"
    response = chat_gpt_persona.ask(user_message)
    print(f"ChatGPT (as a librarian): {response}")
