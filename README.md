# 🧠 Inquiro — AI Research Assistant

**Inquiro** is an intelligent research assistant built with **FastAPI**, designed to simplify the management, summarization, and understanding of academic papers. With seamless integration of **LLMs** (Gemini) and **vector databases** (Qdrant), Inquiro allows you to:

- Upload and organize research papers by project
- Automatically generate intelligent summaries
- Chat with the collection of papers content for deeper understanding
- Translate or explain selection text in paper
- Facilitate notes taking
- Manage data with MongoDB and Qdrant

---

## Features

- **File Upload**: Upload and validate PDF research papers by project
- **Auto Summarization**: Extract content and summarize using LLMs
- **Paper Chat**: Ask questions and receive answers from paper content
- **Markdown Editing**: View, edit, and update summaries in `.md` format
- **Modular Architecture**: Clean separation of routes, controllers, models
- **Translator**: Translate the selection text
- **MongoDB Integration**: Store project, paper, and summary metadata
- **Qdrant Vector DB**: Efficient document embedding and retrieval

---

## Project Structure

```
backend/
├── main.py # FastAPI app entry
├── routes/ # API endpoints 
├── controllers/ # Business logic
├── models/ # DB models and schemas
├── AI/
│ ├── LLM/ # LLM providers (Gemini)
│ └── VectorDB/ # Vector DB (Qdrant)
├── utils/ # Utilities for PDFs, paths, enums
└── config/ # App settings and environment
```

## Tech Stack

- **Backend**: FastAPI
- **Frontend**: React Vite with TypeScript
- **Database**: MongoDB (via Motor)
- **LLMs**: Gemini AI
- **Vector DB**: Qdrant
- **PDF Processing**: PyMuPDF
- **Async File Handling**: Aiofiles

---

## Creator & Maintainer

This project is created and maintained by **ARMAN HOSSAIN**.

---

## 🤝 Contributions

Contributions are welcome! If you want to contribute or report a bug, please open an issue or submit a pull request.