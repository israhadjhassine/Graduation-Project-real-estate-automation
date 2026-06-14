# Collaboration & Git Guide

This guide explains how to manage this project on GitHub and how to collaborate with a partner.

## 1. Setting Up GitHub (For You)

If you haven't pushed the project yet, follow these steps:

1.  **Initialize Git**:
    ```bash
    git init
    ```
2.  **Verify .gitignore**:
    Ensure your `.gitignore` file includes:
    - `.env` (Security: Never push secrets!)
    - `node_modules/` (Heavy and can be re-installed)
    - `.nuxt/` and `.output/`
    - `__pycache__/`
3.  **Add all files**:
    ```bash
    git add .
    ```
4.  **Commit**:
    ```bash
    git commit -m "Initial commit: Setup FastAPI, Nuxt.js, and Seed data"
    ```
5.  **Create Repository on GitHub**:
    Go to [github.com/new](https://github.com/new), create a repository, and copy the URL.
6.  **Add remote and Push**:
    ```bash
    git remote add origin <your-repo-url>
    git push -u origin main
    ```

---

## 2. Shared Environment (.env)

Since `.env` is not pushed to GitHub, you need to share it with your partner manually (via WhatsApp, Email, etc.) or provide them with the values.

**Partner Action**:
1. Copy the `.env.example` file.
2. Rename it to `.env`.
3. Fill in the values you provided.

---

## 3. How your Partner joins the project

Send these instructions to your partner:

1.  **Clone the project**:
    ```bash
    git clone <your-repo-url>
    cd real-estate-automation
    ```
2.  **Setup Environment**:
    - Create a `.env` file from `.env.example`.
    - Install Docker Desktop.
3.  **Run the project**:
    ```bash
    docker-compose up --build -d
    ```

---

## 🔍 How to find your n8n Data Path

If your partner wants to use their existing n8n account (workflows and credentials), they need to find their `.n8n` folder:

- **Windows (Standard)**: `C:/Users/<Username>/.n8n`
- **Windows (Custom)**: `C:/n8n` (If they installed it directly on C:)
- **Mac/Linux**: `/home/<Username>/.n8n` or `~/.n8n`

**To find it quickly on Windows:**
1. Open File Explorer.
2. If it's not in your User folder, check `C:/n8n`.
3. Copy that full path into the `.env` file under `N8N_USER_DATA_PATH`.
   - Example: `N8N_USER_DATA_PATH=C:/n8n`

---

## 4. Seed the Database (Optional)
    If they want the same test data:
    ```bash
    docker exec -it FastAPI_backend python seed.py
    ```

---

## 5. Daily Workflow

- **Before starting work**: Pull latest changes.
  ```bash
  git pull origin main
  ```
- **After finishing a feature**:
  ```bash
  git add .
  git commit -m "Added property search feature"
  git push origin main
  ```

---

## 5. Branching (Best Practice)

Instead of working directly on `main`, it's better to use branches:
1. `git checkout -b feature/auth`
2. Work on the code.
3. `git push origin feature/auth`
4. Create a **Pull Request** on GitHub for your partner to review.
