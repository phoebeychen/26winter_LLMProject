### Part A: Semantic Analysis & Observations
1. Which models got it right?
In our test case ("Roses are red, trucks are blue, and Seattle is grey right now"), the Sentence Transformer and OpenAI Large models correctly identified the core subjects, primarily ranking "Flowers" as the top category. OpenAI Small also performed well by identifying "Colors" as a highly relevant category due to the multiple color descriptors in the sentence.

2. Why did some fail?
The GloVe 50d model failed by incorrectly prioritizing the "Food" category. This failure stems from its architecture: GloVe relies on global word co-occurrence statistics. In its training data (2 billion tweets), words like "red," "blue," or "Seattle" frequently co-occur in food-related contexts (e.g., "red wine," "blueberries," or Seattle restaurant reviews). Because the model lacks a structural understanding of the sentence, these high-frequency associations "noise up" the vector representation.

3. What does this reveal about word order?
This experiment reveals that models using arithmetic averaging (like GloVe) are entirely "blind" to word order. They treat a sentence as a bag of words. Conversely, the success of the Transformers and OpenAI models demonstrates that capturing the syntactic structure—knowing that "Roses" is the subject and "red" is merely an attribute—is essential for accurate semantic retrieval.
