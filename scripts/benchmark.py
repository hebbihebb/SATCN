# benchmark.py
import cProfile
import os
import timeit

from pipeline.filters.epub_parser import EpubOutputGenerator, EpubParserFilter
from pipeline.filters.grammar_filter import GrammarCorrectionFilter
from pipeline.filters.markdown_parser import MarkdownOutputGenerator, MarkdownParserFilter

# from pipeline.filters.spelling_filter import SpellingCorrectionFilter
from pipeline.filters.tts_normalizer import TTSNormalizer
from pipeline.pipeline_runner import PipelineRunner


def get_pipeline(filepath):
    """Factory function to get the correct pipeline for a given file."""
    _, file_extension = os.path.splitext(filepath)
    if file_extension.lower() == ".md":
        parser_filter = MarkdownParserFilter()
        output_generator = MarkdownOutputGenerator()
    elif file_extension.lower() == ".epub":
        parser_filter = EpubParserFilter()
        output_generator = EpubOutputGenerator()
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

    return PipelineRunner(
        [
            parser_filter,
            # SpellingCorrectionFilter(),
            GrammarCorrectionFilter(),
            TTSNormalizer(),
            output_generator,
        ]
    )


def run_benchmark(filepath):
    """Runs the benchmark for a given file and prints the results."""
    print(f"--- Benchmarking {filepath} ---")
    pipeline = get_pipeline(filepath)

    # Timeit
    timer = timeit.Timer(lambda: pipeline.run(filepath))
    number, time_taken = timer.autorange()
    print(f"Timeit: {time_taken / number:.6f} seconds per run ({number} runs)")

    # cProfile
    profiler = cProfile.Profile()
    profiler.enable()
    pipeline.run(filepath)
    profiler.disable()
    profiler.print_stats(sort="cumtime")


def main():
    """Main function to run the benchmarks."""
    corpus_dir = "corpus"
    files_to_benchmark = [
        "small.md",
        "medium.md",
        "large.md",
        "small.epub",
        "medium.epub",
        "large.epub",
    ]

    for filename in files_to_benchmark:
        filepath = os.path.join(corpus_dir, filename)
        if os.path.exists(filepath):
            run_benchmark(filepath)
        else:
            print(f"File not found: {filepath}")


if __name__ == "__main__":
    main()
