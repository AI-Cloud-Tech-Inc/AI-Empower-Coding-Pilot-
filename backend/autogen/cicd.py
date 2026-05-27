"""GitHub Actions CI/CD pipeline auto-generator.

Generates complete CI/CD workflow YAML files based on the project's
tech stack and architecture.
"""

from __future__ import annotations

from typing import Any


class CICDGenerator:
    """Generates GitHub Actions workflow YAML for CI/CD pipelines."""

    def generate(self, architecture: dict[str, Any], project_name: str = "") -> dict[str, str]:
        """Generate CI/CD pipeline files from architecture."""
        name = project_name or "app"
        tech = architecture.get("tech_stack", {})
        frameworks = set(f.lower() for f in tech.get("frameworks", []))
        databases = tech.get("databases", [])

        files: dict[str, str] = {}

        files[".github/workflows/ci.yml"] = self._generate_ci(name, frameworks, databases)
        files[".github/workflows/cd.yml"] = self._generate_cd(name, frameworks)

        if "react" in frameworks:
            files[".github/workflows/frontend.yml"] = self._generate_frontend_ci(name)

        return files

    @staticmethod
    def _generate_ci(name: str, frameworks: set[str], databases: list[str]) -> str:
        services = ""
        if "PostgreSQL" in databases:
            services = (
                "    services:\n"
                "      postgres:\n"
                "        image: postgres:16\n"
                "        env:\n"
                "          POSTGRES_PASSWORD: test\n"
                "          POSTGRES_DB: test\n"
                "        ports:\n"
                "          - 5432:5432\n"
                "        options: >-\n"
                "          --health-cmd pg_isready\n"
                "          --health-interval 10s\n"
                "          --health-timeout 5s\n"
                "          --health-retries 5\n"
            )

        test_step = ""
        if "fastapi" in frameworks:
            test_step = (
                "      - name: Run tests\n"
                "        run: pytest tests/ -v --tb=short\n"
                "      - name: Lint\n"
                "        run: ruff check .\n"
                "      - name: Format check\n"
                "        run: ruff format --check .\n"
                "      - name: Type check\n"
                "        run: mypy . --ignore-missing-imports\n"
            )

        return (
            f"name: {name} CI\n\n"
            "on:\n"
            "  push:\n"
            "    branches: [main, develop]\n"
            "  pull_request:\n"
            "    branches: [main]\n\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            f"{services}"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: actions/setup-python@v5\n"
            "        with:\n"
            "          python-version: '3.12'\n"
            "      - name: Install dependencies\n"
            "        run: pip install -r requirements.txt\n"
            f"{test_step}"
            "\n"
            "  security:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - name: Run security scan\n"
            "        run: pip install bandit && bandit -r app/ -ll\n"
            "\n"
            "  docker:\n"
            "    runs-on: ubuntu-latest\n"
            "    needs: [test, security]\n"
            "    if: github.ref == 'refs/heads/main'\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - name: Build Docker image\n"
            f"        run: docker build -t {name}:${{{{ github.sha }}}} .\n"
        )

    @staticmethod
    def _generate_cd(name: str, frameworks: set[str]) -> str:
        return (
            f"name: {name} CD\n\n"
            "on:\n"
            "  push:\n"
            "    tags: ['v*']\n\n"
            "jobs:\n"
            "  deploy:\n"
            "    runs-on: ubuntu-latest\n"
            "    environment: production\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - name: Build and push\n"
            "        run: |\n"
            f"          docker build -t {name}:${{{{ github.ref_name }}}} .\n"
            f'          echo "Built {name}:${{{{ github.ref_name }}}}"\n'
            "      - name: Deploy\n"
            "        run: |\n"
            '          echo "Deploying to production..."\n'
            "          # Add deployment commands here\n"
        )

    @staticmethod
    def _generate_frontend_ci(name: str) -> str:
        return (
            f"name: {name} Frontend CI\n\n"
            "on:\n"
            "  push:\n"
            "    paths: ['frontend/**']\n"
            "  pull_request:\n"
            "    paths: ['frontend/**']\n\n"
            "jobs:\n"
            "  build:\n"
            "    runs-on: ubuntu-latest\n"
            "    defaults:\n"
            "      run:\n"
            "        working-directory: frontend\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - uses: actions/setup-node@v4\n"
            "        with:\n"
            "          node-version: '20'\n"
            "      - run: npm ci\n"
            "      - run: npm run build\n"
            "      - name: Type check\n"
            "        run: npx tsc --noEmit\n"
        )

    @staticmethod
    def get_supported_platforms() -> list[str]:
        return ["github-actions"]
