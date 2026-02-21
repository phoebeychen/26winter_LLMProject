# Obnoxious Agent - Detects rude, offensive, or inappropriate queries
# Restriction: Cannot use Langchain API for this agent
# Model: gpt-4.1-nano

from openai import OpenAI


class Obnoxious_Agent:
    def __init__(self, client) -> None:
        self.client = client
        self.prompt = (
            "You are a content moderation assistant. Your job is to determine whether "
            "a user's query is obnoxious, rude, offensive, or inappropriate.\n\n"
            "A query is considered obnoxious if it contains:\n"
            "- Insults, slurs, or personal attacks\n"
            "- Profanity or vulgar language directed at someone\n"
            "- Hostile, aggressive, or threatening tone\n"
            "- Deliberately disrespectful or demeaning language\n\n"
            "A query is NOT obnoxious if it is:\n"
            "- A normal question, even if off-topic\n"
            "- Casual or informal language without hostility\n"
            "- A greeting or small talk\n\n"
            "Respond with EXACTLY one word: 'Yes' if the query is obnoxious, "
            "or 'No' if it is not."
        )

    def set_prompt(self, prompt):
        self.prompt = prompt

    def extract_action(self, response) -> bool:
        text = response.choices[0].message.content.strip().lower()
        return text.startswith("yes")

    def check_query(self, query):
        response = self.client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.0
        )
        return self.extract_action(response)
