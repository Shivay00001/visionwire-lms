# Visionwire Lms

Built by [VisionQuantech](https://visionquantech.com) — AI agents, apps & tools for small businesses.

An enterprise-grade solution engineered for high performance.

![Language](https://img.shields.io/badge/Language-Python-blue)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 Overview

Welcome to the **Visionwire Lms** repository. This project is built to deliver a robust and scalable solution tailored to modern development standards.

## ✨ Features

- **High Performance:** Optimized for speed and efficiency.
- **Scalable Architecture:** Designed to grow with your needs.
- **Clean Codebase:** Follows best practices and industry standards.
- **Secure by Default:** Engineered with security in mind.

## 🛠️ Prerequisites

Ensure you have the following installed in your environment before proceeding:
- Appropriate runtime/compiler for `Python`
- Standard development tools

## 📦 Installation

Follow standard installation steps for `Python` to set up the project locally:

1. Clone the repository:
   ```bash
   git clone https://github.com/Shivay00001/visionwire-lms.git
   ```
2. Navigate to the project directory:
   ```bash
   cd visionwire-lms
   ```
3. Install dependencies according to the standard `Python` ecosystem.

## 💻 Usage

Run the project using standard execution commands for `Python`. Ensure all environment variables and configurations are set prior to execution.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## 📝 License

This project is licensed under standard terms.

---

## 🔧 Wave-1 fix notes (2026-09-24)

- **Fixed imports:** `backend/services/llm_client.py` imported nonexistent `app.config`
  and `app.core.exceptions` modules and hard-required provider SDKs at import time.
  It now uses a local env-backed settings object, a local `ContentGenerationError`,
  and lazy provider-SDK imports — it imports cleanly with zero provider packages
  installed (a SDK is only needed when you instantiate that provider; without an API
  key it raises a clear error).
- **Real course CRUD:** `backend/main.py` no longer serves a hardcoded course list.
  Courses live in SQLite (`backend/lms.db`, stdlib only), seeded once from
  `backend/data/courses_seed.json`. Endpoints: `GET /courses`, `POST /courses`,
  `GET/PUT/DELETE /courses/{id}`, `GET /stats`, `GET /health`.
- Verified 2026-09-24: uvicorn booted on :8007; full CRUD round-trip via curl
  (create id=5 → update rating → get → delete → 404 on missing id; stats correct).
  Backend requirements: `fastapi`, `uvicorn`, `pydantic` (see `backend/requirements.txt`).
  Run: `cd backend && uvicorn main:app --host 0.0.0.0 --port 8007`.