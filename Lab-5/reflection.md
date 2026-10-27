# Reflection

**Student:** Sripada Krishna (PES1UG24AM285)

*The handout PDF refers to reflection questions without listing them, so these answers cover the four standard questions for this lab.*

## 1. Which issues were the easiest and which the hardest to fix?

The easiest were mechanical: removing the unused import, changing `== None` to `is None`, renaming `admitPatient`, adding docstrings and wrapping long lines. Each had one obvious fix. The hardest was `eval()` in `calculate_treatment_cost`. Deleting it would break the feature, so I had to design a replacement: a small evaluator built on `ast` that accepts only numbers, `base_bill` and `+ - * /`. I deliberately left out `**` because it can be used to exhaust memory and CPU. I then tested that it rejects `__import__('os').system('id')` and `base_bill ** 9`.

## 2. Did the tools report any false positives, or miss real problems?

One false positive: Pylint and Flake8 said `base_bill` was unused, but `eval()` was reading it from the local scope, which static analysis cannot see. The tools also missed real problems. None flagged the hard-coded nurse master key being printed to the console, `main()` running on import, or the output `1344.0000000000002`. I found those by running the program and reading the code, so static analysis supports a manual review but does not replace it.

## 3. How would you integrate static analysis into your workflow?

I would run all three tools as a pre-commit hook so problems are caught before they reach the repository, and again in CI (for example a GitHub Actions job) with Bandit set to fail the build on Medium or higher findings, Flake8 on any violation and Pylint below a minimum score such as 9.5. Running in CI means the checks do not depend on each developer remembering to run them. Findings that are deliberately accepted would be suppressed with a targeted `# nosec` or `# pylint: disable` comment that includes a reason, never a blanket disable.

## 4. What tangible improvements did you see in the code?

- **Security:** no code execution through `eval`, no shell injection, a stronger hash, a cryptographically secure token, and no secret in the source or output. Bandit went from 5 findings (2 High) to 0.
- **Robustness:** errors are no longer silently swallowed, the shared mutable default is gone, files are closed reliably and bad formulas fail with a clear `ValueError`.
- **Readability and maintainability:** consistent naming, docstrings, simpler functions and PEP 8 formatting. Pylint went from 5.19 to 10.00 and Flake8 from 11 violations to 0.
- **Behaviour is preserved:** the program produces the same output apart from the new SHA-256 hash and the corrected cost value `1344.0`.
