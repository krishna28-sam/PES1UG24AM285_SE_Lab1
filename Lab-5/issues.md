# Issues Found and Fixed

**Student:** Sripada Krishna (PES1UG24AM285)
**File:** `hospital_patient_system.py` (line numbers refer to the original file)

## Summary

| Tool | Before | After |
|------|--------|-------|
| Pylint | 5.19 / 10 (25 messages) | **10.00 / 10** |
| Bandit | 5 issues (2 High, 1 Medium, 2 Low) | **0 issues** |
| Flake8 | 11 violations | **0 violations** |

## Issue table

| # | Issue | Type | Severity | Line(s) | Description | Fix Approach | Commit |
|---|-------|------|----------|---------|-------------|--------------|--------|
| 1 | `os.system` with string concatenation (B605) | Security | High | 56 | The filename is concatenated into a shell command, so a crafted filename allows command injection. | Removed the shell call and used `print()` for the message. | 1 (Bandit) |
| 2 | Weak MD5 hash (B324) | Security | High | 45 | MD5 is cryptographically broken and unsuitable for a patient identifier hash. | Switched to `hashlib.sha256`. | 1 (Bandit) |
| 3 | Use of `eval` (B307, W0123) | Security | Medium | 40 | `eval(formula_expr)` runs arbitrary code from the caller-supplied string (remote code execution). | Parse with `ast.parse` and evaluate with a whitelist evaluator that allows only numbers, `base_bill` and `+ - * /`. Anything else raises `ValueError`. | 1 (Bandit) |
| 4 | `try/except/pass` with bare `except` (B110, W0702, E722) | Security / Bug | Low | 22-25 | Every error was silently swallowed, including typos and `KeyboardInterrupt`. | Replaced with an explicit `if p_id in patient_records` check. | 1 (Bandit) |
| 5 | `random` for a token (B311) | Security | Low | 49 | `random` is predictable and not suitable for security tokens. | Used `secrets.randbelow` (`1000 + randbelow(9000)` keeps the 1000-9999 range). | 1 (Bandit) |
| 6 | Hard-coded secret printed to stdout | Security | High | 68, 77 | The nurse master key was in source code and printed to the console. No tool flagged it. | Read from the `HOSPITAL_NURSE_KEY` environment variable and print only whether it is configured. | 1 (Bandit) |
| 7 | Float artefact in output | Bug | Medium | 72 | The cost printed as `1344.0000000000002`. No tool flagged it. | Round the result to 2 decimals. | 1 (Bandit) |
| 8 | Mutable default argument (W0102) | Bug | Medium | 13 | `intake_log=[]` is shared across all calls. | Default to `None` and create a new list inside the function. | 2 (Pylint) |
| 9 | Function name `admitPatient` (C0103) | Convention | Low | 13 | Not snake_case. | Renamed to `admit_patient` and updated the caller. | 2 (Pylint) |
| 10 | Missing module and function docstrings (C0114, C0116) | Convention | Low | 1, 13, 21, 28, 38, 44, 48, 52, 59, 67 | No documentation. | Added a docstring to the module and every function. | 2 (Pylint) |
| 11 | `== None` (C0121, E711) | Style / Bug risk | Low | 30 | Equality with `None` can be overridden. | Changed to `is None`. | 2 (Pylint) |
| 12 | Redundant `if/else` returning bools and unused `bed_charge` (R1703, R1705, W0612, F841) | Refactor | Low | 29, 32-35 | Dead variable and needless branching. | Removed the variable and returned `bool(...)` directly. | 2 (Pylint) |
| 13 | `open()` without `with` or encoding (R1732, W1514) | Bug risk | Medium | 53-55 | The file leaks if `write` raises and the encoding depends on the platform. | Used `with open(..., encoding="utf-8")`. | 2 (Pylint) |
| 14 | Shadowed global and unused loop variable (W0621, W0612) | Quality | Low | 59-64 | Parameter `patient_records` hides the global and `p` is unused. | Renamed the parameter to `records` and summed over `.values()`. | 2 (Pylint) |
| 15 | `%` string formatting (C0209) | Convention | Low | 17 | Old-style formatting. | Converted to an f-string. | 2 (Pylint) |
| 16 | `main()` runs on import | Design | Low | 80 | Importing the module runs the program. No tool flagged it. | Added `if __name__ == "__main__":`. | 2 (Pylint) |
| 17 | Unused import `math` (F401, W0611) | Style | Low | 4 | Dead import. | Removed it. | 3 (Flake8) |
| 18 | Lines longer than 79 characters (E501) | Style | Low | 7, 8, 9, 16, 72 | PEP 8 line length. | Wrapped the dictionaries and extracted `cost` into a variable. | 3 (Flake8) |
| 19 | No newline at end of file (W292, C0304) | Style | Low | 80 | Missing final newline. | Added it. | 2 and 3 |

## Note on a tool false positive

Pylint and Flake8 reported `base_bill` (line 39) as an unused variable. It was actually used, but only implicitly, because `eval()` read it from the local scope. The tools cannot see that. After replacing `eval` with the safe evaluator, `base_bill` is passed in explicitly and the warning is gone for the right reason.
