# Relevant Documents Agent - Checks if retrieved documents are relevant to the query
# Restriction: Cannot use Langchain API for this agent
# Model: gpt-4.1-nano

from openai import OpenAI


class Relevant_Documents_Agent:
    def __init__(self, openai_client) -> None:
        self.client = openai_client
        self.prompt = (
            "You are a relevance evaluation assistant for a Machine Learning textbook chatbot.\n\n"
            "You will be given a user's query and a set of retrieved document chunks. "
            "Your task is to determine whether the retrieved documents are relevant to "
            "answering the user's query.\n\n"
            "Documents are considered RELEVANT if they contain information that can "
            "help answer the user's question about Machine Learning topics covered in the textbook.\n\n"
            "Documents are considered NOT RELEVANT if:\n"
            "- The user's question is completely unrelated to Machine Learning\n"
            "- The retrieved documents do not contain information related to the user's question\n"
            "- The documents are about a different topic than what the user asked\n\n"
            "Respond with EXACTLY one word: 'Yes' if the documents are relevant, "
            "or 'No' if they are not."
        )

    def get_relevance(self, query, docs) -> bool:
        if not docs:
            return False

        docs_text = "\n\n".join(
            [f"Document {i+1}:\n{doc.page_content}" for i, doc in enumerate(docs)]
        )

        user_message = (
            f"User Query:\n{query}\n\n"
            f"Retrieved Documents:\n{docs_text}"
        )

        response = self.client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.0
        )

        text = response.choices[0].message.content.strip().lower()
        return text.startswith("yes")
