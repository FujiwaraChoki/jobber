from g4f.client import Client
from g4f.Provider import AiAsk

class GPT:
    def __init__(self) -> None:
        """
        Constructor for GPT class.
        """
        self.client = Client()
        self.base_model = "gpt-3.5-turbo"
        self.provider = AiAsk

    def ask(self, prompt: str) -> str:
        """
        Ask a question to GPT-3.5.

        :param prompt: The prompt to ask GPT-3.5.

        :return: The response from GPT-3.5.
        """
        response = self.client.chat.completions.create(
            model=self.base_model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        ).choices[0].message.content

        return response
