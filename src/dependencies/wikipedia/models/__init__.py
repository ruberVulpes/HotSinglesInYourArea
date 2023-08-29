from dependencies.wikipedia.models.single import Single

characters_to_remove = ["“", "”", '"', "‘", "’", "'", "(", "[", "{", ")", "]", "}", "-", ".", ",", "!", "?"]
# dict word -> censored
censored_words = {"fuck": "f**k", "niggas": "ni**as", "pussy": "p*$$y", "&": "and", "Shit": "S**t"}
