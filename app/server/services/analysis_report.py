from app.server.models.analysis_report import AnalysisReport, CreateUpdateAnalysisReport

from datetime import datetime
from typing import Dict, List
from collections import Counter
from functools import cached_property

import logging
import httpx
import time
import re


class TextAnalyzer:
    def __init__(self, create_text_analysis: CreateUpdateAnalysisReport) -> None:
        self.create_text_analysis = create_text_analysis
        self.text_name = create_text_analysis.name
        self.need_download = True if create_text_analysis.url else False
        self.text = ''

    async def generate_analysis_report(self) -> AnalysisReport:

        self.logger.info(f'Started analysis. Text name = {self.text_name}. ')
        start_time = time.time()
        self.text = await self.get_text()

        analysis_report = AnalysisReport(
            name=self.text_name,
            text=self.text,
            url=self.create_text_analysis.url,
            time_of_processing=None,
            report_generation_datetime=None,

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
        )

        analysis_report.time_of_processing = round((time.time() - start_time) * 1000, 2)
        analysis_report.report_generation_datetime = datetime.now()

        self.logger.info(f'Finished analysis. Processing time -> {analysis_report.time_of_processing}.')
        return analysis_report

    @cached_property
    def logger(self) -> logging.Logger:
        logger = logging.getLogger(f'{self.text_name} Logger')
        logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler('textanalyzer.log')
        file_handler.setFormatter(
            logging.Formatter(
                f'%(asctime)s || {self.text_name} || %(message)s'
            )
        )
        logger.addHandler(file_handler)

        return logger

    async def get_text(self) -> str:
        if not self.need_download:
            return self.create_text_analysis.text
        else:
            text = await self.download_text()
            return text

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

    async def download_text(self) -> str:
        try:
            self.logger.info(f'Downloading from {self.create_text_analysis.url}...')
            async with httpx.AsyncClient() as client:
                result = await client.get(self.create_text_analysis.url)
            if result.status_code == 200:
                self.logger.info(f'Download finished successfully.')
                return result.text
            else:
                raise Exception(f'Response from server -> {result.status_code}.')

        except Exception as e:
            self.logger.error(f'Unable to download text: {e}')
            raise Exception(e)



