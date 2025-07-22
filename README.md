# Gemini-Vault

**Gemini-Vault** 是一个为商业用途打造的、高性能的 Google Gemini API 代理和负载均衡器。本项目使用 Python 和 FastAPI 构建，为您提供一个坚实的基础来对外提供可管理的 API 服务。

本项目从零开始编写，其架构设计受到了 `gemini-balance` 项目的启发，但专为商业应用场景设计，核心关注点在于用户管理、API 计量和系统的可扩展性。

---

## ✨ 功能特性

*   **高性能:** 基于 FastAPI 构建，支持异步、高吞吐量的请求处理。
*   **智能负载均衡:** 通过轮询一个 Gemini API 密钥池来有效分配请求负载。
*   **智能容错机制:**
    *   当某个密钥请求失败时，自动使用下一个可用密钥进行重试。
    *   当某个密钥连续失败多次后，会自动将其暂时禁用，并在冷却期后重新启用。
*   **兼容 OpenAI API:** 对外暴露一个标准的 `/v1/chat/completions` 接口，使其能够与大量现有的工具和库无缝协作。
*   **自动化持续集成/部署 (CI/CD):**
    *   项目内含 `Dockerfile`，可轻松将应用容器化。
    *   预先配置了 GitHub Actions 工作流，能够自动构建 Docker 镜像并将其推送到 Docker Hub。
*   **可扩展的配置:** 使用 Pydantic 进行类型安全和环境感知的配置管理。

---

## 🚀 快速上手

### 1. 环境准备

*   Docker
*   一个 GitHub 账号
*   一个 Docker Hub 账号

### 2. 初始化设置

1.  **创建 GitHub 仓库:** 在 GitHub 上创建一个新的仓库（私有或公开均可），并将本项目的所有文件上传。

2.  **配置环境变量文件:**
    *   将项目中的 `.env.example` 文件重命名为 `.env`。
    *   打开 `.env` 文件并填入您的配置信息，尤其是您的 `GEMINI_API_KEYS` 列表。

3.  **配置 GitHub Secrets:**
    *   在您的新 GitHub 仓库中，导航至 `Settings` > `Secrets and variables` > `Actions`。
    *   添加以下两个仓库秘密变量 (Repository secrets):
        *   `DOCKERHUB_USERNAME`: 您的 Docker Hub 用户名。
        *   `DOCKERHUB_TOKEN`: 您的 Docker Hub 访问令牌 (Access Token)。

### 3. 自动化部署 (CI/CD)

*   完成上述设置后，只需将代码 `git push` 到您 GitHub 仓库的 `main` 分支。
*   `.github/workflows/main.yml` 中定义的 GitHub Actions 工作流将自动触发。它会构建 Docker 镜像，并将其推送到您的 Docker Hub 账户下，镜像名称默认为 `your-username/gemini-vault:latest`。

### 4. 手动部署 (以 ClawCloud 为例)

当您的镜像成功推送到 Docker Hub 后，您可以将其部署到任何支持容器的云平台。

1.  登录您的云平台 (例如 ClawCloud)。
2.  创建一个新的应用或服务。
3.  **镜像名称 (Image Name):** 填入您在 Docker Hub 上的完整镜像地址 (例如 `your-dockerhub-username/gemini-vault:latest`)。
4.  **容器端口 (Container Port):** 设置为 `8000`。
5.  **环境变量 (Environment Variables):** **这是最关键的一步。** 您必须将本地 `.env` 文件中的所有键值对，逐一复制并添加到平台的环填变量配置中。
6.  启动部署。

---

## ⚙️ API 使用方法

部署成功后，您的服务将可以通过云平台提供的 URL 进行访问。

*   **接口地址:** `POST /v1/chat/completions`
*   **请求体 (Body):** 该接口接受与 OpenAI Chat Completions API 完全相同的 JSON 请求体。

**`curl` 调用示例:**

```bash
curl -X POST "http://your-deployment-url/v1/chat/completions" \
-H "Content-Type: application/json" \
-d '{
  "model": "gemini-1.5-flash-latest",
  "messages": [
    {
      "role": "user",
      "content": "你好，法国的首都是哪里？"
    }
  ]
}'
