from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
from collections import Counter
from functools import cached_property

import logging
import requests
import time
import re


@dataclass
class AnalysisReport:
    number_of_characters: int
    number_of_words: int
    number_of_sentences: int
    frequency_of_characters: Dict[str, float]
    distribution_of_characters: Dict[str, str]
    average_word_length: float
    average_words_in_sentence: float
    ten_most_used_words: List[str]
    ten_longest_words: List[str]
    ten_shortest_words: List[str]
    ten_longest_sentences: List[str]
    ten_shortest_sentences: List[str]
    number_of_palindrome_words: int
    ten_longest_palindrome_words: List[str]
    is_text_a_palindrome: bool
    reversed_text: str
    # “This is the text.” -> ”.txet desrever ehT”
    reversed_text_with_correct_words_order: str
    # “This is the text.” -> ”.text the is This”
    time_of_processing: int = None
    report_generation_datetime: datetime = None

    def __str__(self):
        return f"""Text Analysis Report
        Statistics information:
            Number of characters - {self.number_of_characters} |
            Number of words - {self.number_of_words} |
            Number of sentences - {self.number_of_sentences} |
            Frequency of characters - {self.frequency_of_characters} |
            Distribution of characters as a percentage of total - {self.distribution_of_characters} |
            Average word length - {self.average_word_length} |
            The average number of words in a sentence - {self.average_words_in_sentence} |
            Top 10 most used words - {self.ten_most_used_words} |
            Top 10 longest words - {self.ten_longest_words} |
            Top 10 shortest words - {self.ten_shortest_words} |
            Top 10 longest sentences - {self.ten_longest_sentences} |
            Top 10 shortest sentences - {self.ten_shortest_sentences} |
            Number of palindrome words - {self.number_of_palindrome_words} |
            Top 10 longest palindrome words - {self.ten_longest_palindrome_words} |
            Is the whole text a palindrome? - {self.is_text_a_palindrome} |
            
            
        Reversed texts:
            The reversed text - {self.reversed_text} |
            The reversed text but the character order in words kept intact - {self.reversed_text_with_correct_words_order} |
        
        
        Datetime information:
            The time it took to process the text in ms - {self.time_of_processing} |
            Date and time when the report was generated - {self.report_generation_datetime} |
        """


class TextAnalyzer:
    def __init__(self, text_name: str, text_type: str) -> None:
        self.text_name = text_name
        self.text_type = text_type

    def generate_analysis_report(self) -> AnalysisReport:

        self.logger.info('Started analysis.')
        start_time = time.time()

        if not self.text:
            return None

        analysis_report = AnalysisReport(
            number_of_characters=self.number_of_characters,
            number_of_words=self.number_of_words,
            number_of_sentences=self.number_of_sentences,
            frequency_of_characters=self.frequency_of_characters,
            distribution_of_characters=self.distribution_of_characters,
            average_word_length=self.average_word_length,
            average_words_in_sentence=self.average_words_in_sentence,
            ten_most_used_words=self.ten_most_used_words,
            ten_longest_words=self.ten_longest_words,
            ten_shortest_words=self.ten_shortest_words,
            ten_longest_sentences=self.ten_longest_sentences,
            ten_shortest_sentences=self.ten_shortest_sentences,
            number_of_palindrome_words=self.number_of_palindrome_words,
            ten_longest_palindrome_words=self.ten_longest_palindrome_words,
            is_text_a_palindrome=self.is_text_a_palindrome,
            reversed_text=self.reversed_text,
            reversed_text_with_correct_words_order=self.reversed_text_with_correct_words_order
        )

        analysis_report.time_of_processing = round((time.time() - start_time) * 1000, 2)
        analysis_report.report_generation_datetime = datetime.now()

        self.logger.info(f'Finished analysis. Processing time -> {analysis_report.time_of_processing}.')
        return analysis_report

    @cached_property
    def logger(self) -> logging.Logger:
        logger = logging.getLogger(f'{self.text_type} {self.text_name} Logger')
        logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler('textanalyzer.log')
        file_handler.setFormatter(
            logging.Formatter(
                f'%(asctime)s|{self.text_type}|{self.text_name}|%(message)s'
            )
        )
        logger.addHandler(file_handler)

        return logger

    @cached_property
    def text(self) -> str:
        try:
            if self.text_type == 'FILE':
                return self.read_file(self.text_name)
            elif self.text_type == 'RESOURCE':
                return self.read_resource(self.text_name)
        except Exception as e:
            self.logger.error(f'Unable to read the text: {e}')
            return None

    @cached_property
    def sentences(self) -> List[str]:
        sentence_pattern = re.compile(r'([A-Z][^\.!?]*[\.!?])', re.M)
        return sentence_pattern.findall(self.text)

    @cached_property
    def words(self) -> List[str]:
        return list(map(lambda word: word.lower(), re.findall(r'\b\S+\b', self.text)))

    @cached_property
    def characters(self) -> List[str]:
        alphanumeric = filter(lambda c: c.isalnum(), self.text)
        return list(map(lambda c: c.lower(), alphanumeric))

    @cached_property
    def number_of_characters(self) -> int:
        return len(self.characters)

    @cached_property
    def number_of_words(self) -> int:
        return len(self.words)

    @cached_property
    def number_of_sentences(self) -> int:
        return len(self.sentences)

    @cached_property
    def frequency_of_characters(self) -> Dict[str, int]:
        characters_counter = Counter(self.characters)
        return dict(sorted(characters_counter.items(), key=lambda x: x[1], reverse=True))

    @cached_property
    def palindrome_words(self) -> List[str]:
        return [word for word in self.words if self.is_palindrome(word)]

    @property
    def distribution_of_characters(self) -> Dict[str, str]:
        return {character: f'{round(count / self.number_of_characters * 100, 2)}%'
                for character, count in self.frequency_of_characters.items()}

    @property
    def average_word_length(self) -> float:
        return round(sum(len(word) for word in self.words) / self.number_of_words, 2)

    @property
    def average_words_in_sentence(self) -> float:
        return round(self.number_of_words / self.number_of_sentences, 2)

    @property
    def ten_most_used_words(self) -> List[str]:
        most_common = Counter(self.words).most_common(10)
        return [common_tuple[0] for common_tuple in most_common]

    @property
    def ten_longest_words(self) -> List[str]:
        return self.get_ten_longest(self.words)

    @property
    def ten_shortest_words(self) -> List[str]:
        return self.get_ten_shortest(self.words)

    @property
    def ten_longest_sentences(self) -> List[str]:
        return self.get_ten_longest(self.sentences)

    @property
    def ten_shortest_sentences(self) -> List[str]:
        return self.get_ten_shortest(self.sentences)

    @property
    def number_of_palindrome_words(self) -> int:
        return len(self.palindrome_words)

    @property
    def ten_longest_palindrome_words(self) -> List[str]:
        return self.get_ten_longest(self.palindrome_words)

    @property
    def is_text_a_palindrome(self) -> bool:
        return self.is_palindrome(self.get_text_without_spaces_and_punctuation(self.text))

    @property
    def reversed_text(self) -> str:
        return self.text[::-1]

    @property
    def reversed_text_with_correct_words_order(self) -> str:
        return ' '.join(self.text.split()[::-1])

    @staticmethod
    def get_text_without_spaces_and_punctuation(text) -> str:
        return re.sub(r'\W', '', text)

    @staticmethod
    def get_ten_longest(strings: List[str]) -> List[str]:
        return sorted(set(strings), key=len, reverse=True)[:10]

    @staticmethod
    def get_ten_shortest(strings: List[str]) -> List[str]:
        return sorted(set(strings), key=len)[:10]

    @staticmethod
    def is_palindrome(string: str) -> bool:
        return string == string[::-1]

    @staticmethod
    def read_file(filename: str) -> str:
        with open(filename, 'r') as file:
            text = file.read()

        return text

    @staticmethod
    def read_resource(resource_name: str) -> str:
        result = requests.get(resource_name)

        if result.status_code == 200:
            return result.text
        else:
            raise Exception(f'Response from server -> {result.status_code}.')
