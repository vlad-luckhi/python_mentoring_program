from text_analyzer import TextAnalyzer


if __name__ == '__main__':
    text_filename = 'text'
    text_analyzer = TextAnalyzer(filename=text_filename)
    analysis_report = text_analyzer.generate_analysis_report()
    print(analysis_report)