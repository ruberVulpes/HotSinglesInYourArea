from typing import Hashable, Sequence

from rapidfuzz.utils import default_process

words_to_remove = ["fuck", "f**k", "niggas", "ni**as", "pussy", "p*$$y", "Shit", "S**t"]
translation_table = {word: None for word in words_to_remove}


def custom_processor(sentence: Sequence[Hashable] | str) -> Sequence[Hashable] | str:
    return default_process(sentence.translate(translation_table))
