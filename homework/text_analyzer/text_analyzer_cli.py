import argparse


from typing import List
from text_analyzer import TextAnalyzer, AnalysisReport
from concurrent.futures import ProcessPoolExecutor


def generate_report(text: TextAnalyzer) -> AnalysisReport:
    return text.generate_analysis_report()


def get_texts() -> List[TextAnalyzer]:
    parser = argparse.ArgumentParser(description='Text analyzer CLI', add_help=True)
    parser.add_argument('-f', action='store', nargs='*', help='File to read')
    parser.add_argument('-r', action='store', nargs='*', help='Resource to read')
    args = vars(parser.parse_args())

    text_types = {'f': 'FILE', 'r': 'RESOURCE'}

    texts = [
        TextAnalyzer(text_name=text_name, text_type=text_types[text_type])
        for text_type in args if args[text_type] and text_type in text_types for text_name in args[text_type]
    ]

    return texts


def get_reports_in_parallel(texts: List[TextAnalyzer]) -> List[AnalysisReport]:
    with ProcessPoolExecutor() as executor:
        results = executor.map(generate_report, texts)

    return list(results)


def main():
    texts = get_texts()
    print(texts)
    analysis_reports = get_reports_in_parallel(texts)
    for index, report in enumerate(analysis_reports, start=1):
        print(f'Report {index}. -------------------------------------------')
        print(report)


if __name__ == '__main__':
    main()
