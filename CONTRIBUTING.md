# Contributing to the SATCN Pipeline

We welcome contributions to improve the SATCN pipeline. This document provides guidelines for reporting mis-corrections and adding new regression files.

## Reporting Mis-corrections

If you find a mis-correction, please open an issue on our GitHub repository. In the issue, please include:

- The original text.
- The incorrect output from the pipeline.
- The expected output.

This information will help us to identify and fix the issue.

## Adding New Regression Files

To add a new regression file, please follow these steps:

1. Create a new input file in the `tests/regression_corpus` directory. The file should be named `input_<slug>.md`, where `<slug>` is a short, descriptive name for the test case.
2. Run the pipeline on the input file to generate the "golden" output file.
3. Review the golden file to ensure that it is correct.
4. Add both the input and golden files to a new pull request.
