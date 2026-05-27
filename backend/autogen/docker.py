"""Docker configuration auto-generator.

Generates Dockerfile, docker-compose.yml, and .dockerignore files
based on the project architecture.
"""

from __future__ import annotations

from typing import Any


class DockerGenerator:
    """Generates Docker configurations from architecture descriptions."""

    def generate(self, architecture: dict[str, Any], project_name: str = "") -> dict[str, str]:
        """Generate Docker files from architecture."""
        name = project_name or "app"
        components = architecture.get("components", [])
        tech = architecture.get("tech_stack", {})
        frameworks = set(f.lower() for f in tech.get("frameworks", []))
        databases = tech.get("databases", [])

        files: dict[str, str] = {}

        if "fastapi" in frameworks or any(c.get("type") == "service" for c in components):
            files["Dockerfile"] = self._generate_backend_dockerfile(name)

        if "react" in frameworks or any(c.get("type") == "application" for c in components):
            files["frontend/Dockerfile"] = self._generate_frontend_dockerfile(name)

        files["docker-compose.yml"] = self._generate_compose(name, frameworks, databases)
        files[".dockerignore"] = self._generate_dockerignore()

        return files

    @staticmethod
    def _generate_backend_dockerfile(name: str) -> str:
        return (
            f"# {name} backend\n"
            "FROM python:3.12-slim AS base\n\n"
            "ENV PYTHONUNBUFFERED=1 \\\n"
            "    PYTHONDONTWRITEBYTECODE=1 \\\n"
            "    PIP_NO_CACHE_DIR=1\n\n"
            "WORKDIR /app\n\n"
            "# Dependencies\n"
            "COPY requirements.txt .\n"
            "RUN pip install --no-cache-dir -r requirements.txt\n\n"
            "# Application\n"
            "COPY . .\n\n"
            "EXPOSE 8000\n\n"
            "HEALTHCHECK --interval=30s --timeout=5s --retries=3 \\\n"
            '  CMD python -c "import urllib.request; '
            "urllib.request.urlopen('http://localhost:8000/api/health')\"\n\n"
            'CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]\n'
        )

    @staticmethod
    def _generate_frontend_dockerfile(name: str) -> str:
        return (
            f"# {name} frontend\n"
            "FROM node:20-alpine AS build\n"
            "WORKDIR /app\n"
            "COPY package*.json ./\n"
            "RUN npm ci\n"
            "COPY . .\n"
            "RUN npm run build\n\n"
            "FROM nginx:alpine\n"
            "COPY --from=build /app/dist /usr/share/nginx/html\n"
            "COPY nginx.conf /etc/nginx/conf.d/default.conf\n"
            "EXPOSE 80\n"
            'CMD ["nginx", "-g", "daemon off;"]\n'
        )

    @staticmethod
    def _generate_compose(
        name: str,
        frameworks: set[str],
        databases: list[str],
    ) -> str:
        services: list[str] = []

        if "fastapi" in frameworks:
            services.append(
                "  backend:\n"
                "    build: .\n"
                "    ports:\n"
                '      - "8000:8000"\n'
                "    environment:\n"
                "      - APP_ENV=development\n"
                "    volumes:\n"
                "      - .:/app\n"
                "    restart: unless-stopped\n"
                "    healthcheck:\n"
                "      test: ['CMD', 'curl', '-f', 'http://localhost:8000/api/health']\n"
                "      interval: 30s\n"
                "      timeout: 5s\n"
                "      retries: 3\n"
            )

        if "react" in frameworks:
            services.append(
                "  frontend:\n"
                "    build: ./frontend\n"
                "    ports:\n"
                '      - "3000:80"\n'
                "    depends_on:\n"
                "      - backend\n"
                "    restart: unless-stopped\n"
            )

        if "PostgreSQL" in databases:
            services.append(
                "  db:\n"
                "    image: postgres:16-alpine\n"
                "    environment:\n"
                f"      POSTGRES_DB: {name.replace('-', '_')}\n"
                "      POSTGRES_USER: app_user\n"
                "      POSTGRES_PASSWORD: changeme\n"
                "    ports:\n"
                '      - "5432:5432"\n'
                "    volumes:\n"
                "      - pgdata:/var/lib/postgresql/data\n"
                "    restart: unless-stopped\n"
            )

        services.append(
            "  redis:\n"
            "    image: redis:7-alpine\n"
            "    ports:\n"
            '      - "6379:6379"\n'
            "    restart: unless-stopped\n"
        )

        volumes = ""
        if "PostgreSQL" in databases:
            volumes = "\nvolumes:\n  pgdata:\n"

        return (
            f"# {name} docker-compose\n"
            "version: '3.9'\n\n"
            "services:\n" + "\n".join(services) + volumes
        )

    @staticmethod
    def _generate_dockerignore() -> str:
        return (
            "__pycache__\n"
            "*.pyc\n"
            ".git\n"
            ".env\n"
            "node_modules\n"
            ".pytest_cache\n"
            "*.egg-info\n"
            "dist\n"
            "build\n"
            ".venv\n"
            "venv\n"
            ".mypy_cache\n"
            ".ruff_cache\n"
            "terraform\n"
        )

    @staticmethod
    def get_supported_runtimes() -> list[str]:
        return ["python", "node"]
