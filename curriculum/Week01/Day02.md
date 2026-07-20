# Day 02 - Professional Python Environment

## Goal

Build a production-ready Python development environment that will be used throughout the residency.

Estimated Time:
2 Hours

---

## Objectives

- Learn uv
- Learn virtual environments
- Learn project structure
- Learn Ruff
- Learn pytest
- Learn pyproject.toml

---

## Theory (20 mins)

Read

1. Python Packaging Guide
https://packaging.python.org/en/latest/

2. uv Documentation
https://docs.astral.sh/uv/

3. pyproject.toml
https://packaging.python.org/en/latest/guides/writing-pyproject-toml/

---

## Hands-on

### Create Lab

```
labs/python/python-environment/
```

---

### Create Project

```bash
uv init python-environment
```

---

### Enter Project

```bash
cd python-environment
```

---

### Create Virtual Environment

```bash
uv venv
```

---

### Activate

macOS

```bash
source .venv/bin/activate
```

---

### Install Packages

```bash
uv add requests

uv add rich

uv add python-dotenv

uv add typer
```

---

### Dev Packages

```bash
uv add --dev pytest

uv add --dev ruff

uv add --dev mypy
```

---

## Explore

Understand

pyproject.toml

uv.lock

.venv

---

## Exercise 1

Create

main.py

Requirements

- Print Python Version
- Print Current Directory
- Print Environment Variables
- Print Installed Packages

---

## Exercise 2

Create

config.py

Load

.env

using python-dotenv

---

## Exercise 3

Create

logger.py

Use logging module

Log

INFO

WARNING

ERROR

---

## Exercise 4

Create

cli.py

Use typer

Commands

hello

version

env

---

## Exercise 5

Write

tests/test_main.py

Use pytest

---

## Ruff

Run

```bash
ruff check .
```

Fix all issues.

---

## Mypy

Run

```bash
mypy .
```

---

## Deliverables

✔ Python Environment

✔ Virtual Environment

✔ CLI

✔ Logging

✔ Config

✔ Tests

---

## Git Commit

```
feat: setup professional python environment
```

---

## Reflection

Answer

1. Why use uv instead of pip?

2. Why use pyproject.toml?

3. What is dependency locking?

4. Why use virtual environments?

5. What is semantic versioning?