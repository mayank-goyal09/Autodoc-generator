# 🚀 AutoDoc-Generator: AI-Powered Documentation 🚀

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-brightgreen.svg)](.github/workflows/autodoc.yml)

**AutoDoc-Generator** is a high-impact developer tool that programmatically identifies, summarizes, and injects docstrings into your Python code using the `CodeGPT` AI model and AST parsing.

---

## ✨ Key Features
- **🧠 AI Summarization**: Uses transformer models to understand code logic and generate human-readable documentation.
- **🏗️ AST Analysis**: Surgically identifies undocumented functions using Python's Abstract Syntax Tree.
- **⚙️ CI/CD Ready**: Automated quality control via GitHub Actions.
- **🛠️ Flexible CLI**: Easy-to-use command-line interface for rapid development.

## 🛠️ Installation
```bash
git clone https://github.com/mayank-goyal09/Autodoc-generator.git
cd Autodoc-generator
pip install -r requirements.txt
```

## 🚀 Usage
To document a specific file:
```bash
python main.py --file your_script.py
```
This will create `your_script_documented.py` with injected docstrings.

## 📁 Project Structure
- `main.py`: Entry point for the CLI and docstring injection logic.
- `model_inference.py`: AI model loading and inference logic.
- `parser_engine.py`: AST parsing engine for code analysis.
- `.github/workflows/`: CI/CD pipeline configuration.

---

## 🔮 Future Initiatives
- [ ] **Multi-language Support**: Integration with Tree-sitter.
- [ ] **Web Dashboard**: A premium UI for tracking documentation health.
- [ ] **RAG Integration**: Project-wide context for better documentation.

---
*Built with ❤️ for the modern developer.*
