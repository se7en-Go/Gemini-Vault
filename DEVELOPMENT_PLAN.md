# Gemini-Vault: Development Framework and Plan

This document outlines the development framework, technology stack, and phased plan for the Gemini-Vault project. It serves as a living document to track progress.

---

## 1. Project Overview

**Gemini-Vault** is a commercial-ready, high-performance proxy and load balancer for the Google Gemini API. It is designed from the ground up to support user management, API key issuance, and usage-based metering.

## 2. Technology Stack

- **Backend Framework:** FastAPI
- **Database:** SQLAlchemy (ORM), with support for SQLite (dev) and PostgreSQL (prod)
- **Database Migrations:** Alembic
- **Authentication:** JWT (JSON Web Tokens) with Passlib for password hashing
- **Configuration:** Pydantic
- **Deployment:** Docker, with CI/CD via GitHub Actions

---

## 3. Phased Development Plan

### Phase 1: Core Proxy & Automated Deployment (MVP)

**Goal:** Build the foundational API proxy service and automate its deployment.

- [x] **1.1: Project Scaffolding:** Initialize the FastAPI project structure.
- [x] **1.2: Configuration Management:** Implement Pydantic-based settings management (`.env` support).
- [x] **1.3: Core Proxy Logic:** Implement API forwarding to Gemini with round-robin key rotation.
- [x] **1.4: Robust Key Management:** Implement logic to disable and re-enable failing API keys.
- [x] **1.5: Containerization:** Create a `Dockerfile` for the application.
- [x] **1.6: CI/CD Pipeline:** Set up a GitHub Actions workflow to build and push the Docker image to Docker Hub.
- [x] **1.7: Documentation:** Create the initial `README.md` file.

### Phase 2: User Management & Authentication

**Goal:** Implement a complete user system, allowing users to register, log in, and receive authentication tokens.

- [x] **2.1: Add Dependencies:** Add `sqlalchemy`, `alembic`, `passlib`, `python-jose` to `requirements.txt`.
- [x] **2.2: Database Integration:** Configure the database connection (`DATABASE_URL`).
- [x] **2.3: User Model:** Define the `User` table using SQLAlchemy.
- [x] **2.4: Pydantic Schemas:** Create `UserCreate` and `User` schemas for API validation.
- [x] **2.5: CRUD Operations:** Implement functions for creating and retrieving users from the database.
- [x] **2.6: User Registration Endpoint:** Create the `POST /auth/users/` endpoint.
- [x] **2.7: JWT & Login Endpoint:** Implement the `POST /auth/token` endpoint for user login and JWT issuance.
- [x] **2.8: Protected "Me" Endpoint:** Create the `GET /auth/users/me` endpoint to verify authentication.

- [x] **2.9: User-Specific API Keys:**
    - [x] 2.9.1: Create a new `UserApiKey` model in the database to store keys linked to users.
    - [x] 2.9.2: Create CRUD functions for generating, retrieving, and revoking these keys.
    - [x] 2.9.3: Create a protected endpoint (e.g., `POST /api-keys/`) where a logged-in user can generate their first API key.

### Phase 3: API Metering & Admin Dashboard

**Goal:** Track API usage per user and provide an admin interface for management.

- [x] **3.1: Metering Middleware:**
    - [x] 3.1.1: Create a FastAPI middleware to intercept requests to the core proxy (`/v1/chat/completions`). *(Implemented via endpoint dependency)*
    - [x] 3.1.2: The middleware will authenticate the request using the user-specific API key from the `Authorization` header.
    - [x] 3.1.3: Implement logic to increment a `usage_count` or decrement a `balance` on the user's API key record.
    - [x] 3.1.4: Reject requests if the key is invalid or the user has insufficient balance.

- [x] **3.2: Admin Dashboard:**
    - [x] 3.2.1: Create admin-only endpoints to view all users and their usage stats.
    - [x] 3.2.2: Implement endpoints for an admin to manually adjust a user's balance or active status.

---

- [x] **3.3: Finalize API Documentation:** Provide instructions for accessing the auto-generated `openapi.json` schema for frontend development.

## **Next Step:**

- **All backend development is complete.** The project is ready for frontend development or direct API integration.

### Phase 4: Basic Frontend UI (Server-Rendered)

**Goal:** Create a modern-looking, server-rendered UI for basic user interactions using Jinja2 and Tailwind CSS.

- [x] **4.1: Add Dependencies & Configuration:**
    - [x] 4.1.1: Add `jinja2` to `requirements.txt`.
    - [x] 4.1.2: Create `templates` and `static` directories.
    - [x] 4.1.3: Configure `main.py` to serve static files and use Jinja2 templates.

- [x] **4.2: Create Base Layout:**
    - [x] 4.2.1: Create a `base.html` template with the Tailwind CSS CDN link and common page structure (navbar, footer).

- [x] **4.3: Implement Frontend Routes & Pages:**
    - [x] 4.3.1: Create a new `frontend` router.
    - [x] 4.3.2: Create a `login.html` page and the corresponding GET/POST routes for login.
    - [x] 4.3.3: Create a `register.html` page and the corresponding GET/POST routes for registration.
    - [x] 4.3.4: Create a `dashboard.html` page for logged-in users to view and manage their API keys.
