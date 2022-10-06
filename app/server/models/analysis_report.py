from datetime import datetime

from beanie import Document
from pydantic import BaseModel, validator, HttpUrl


class AnalysisReport(Document):
    name: str
    text: str
    url: HttpUrl | None = None
    time_of_processing: int | None = None
    report_generation_datetime: datetime | None = None

    # statistic information
    number_of_characters: int
    number_of_words: int
    number_of_sentences: int
    frequency_of_characters: dict[str, float]
    distribution_of_characters: dict[str, str]
    average_word_length: float
    average_words_in_sentence: float
    ten_most_used_words: list[str]
    ten_longest_words: list[str]
    ten_shortest_words: list[str]
    ten_longest_sentences: list[str]
    ten_shortest_sentences: list[str]
    number_of_palindrome_words: int
    ten_longest_palindrome_words: list[str]
    is_text_a_palindrome: bool

    class Settings:
        name = "text_analysis"


class CreateUpdateAnalysisReport(BaseModel):
    name: str
    text: str | None = None
    url: str | None = None

    @validator('url', always=True)
    def check_consistency(cls, v, values):
        if v is not None and values['text'] is not None:
            raise ValueError('Must not provide both text and url.')
        if v is None and values.get('text') is None:
            raise ValueError('Must provide text or url.')
        return v

