"""Project scaffolding auto-generator.

Generates a complete project directory structure from an architecture plan,
including boilerplate files, configuration, and dependency manifests.
"""

from __future__ import annotations

from typing import Any


class ScaffoldingEngine:
    """Generates full project scaffolding from architecture descriptions."""

    TEMPLATES: dict[str, dict[str, str]] = {
        "fastapi": {
            "app/main.py": (
                '"""Application entry point."""\n\n'
                "from fastapi import FastAPI\n\n"
                'app = FastAPI(title="{name}")\n\n\n'
                "@app.get('/health')\n"
                "async def health() -> dict:\n"
                '    return {{"status": "healthy"}}\n'
            ),
            "app/__init__.py": '"""Application package."""\n',
            "requirements.txt": "fastapi>=0.111.0\nuvicorn[standard]>=0.30.0\npydantic>=2.7.0\n",
            "pyproject.toml": (
                "[project]\n"
                'name = "{name}"\n'
                'version = "0.1.0"\n'
                'requires-python = ">=3.11"\n\n'
                "[tool.ruff]\n"
                "line-length = 100\n"
            ),
            ".gitignore": (
                "__pycache__/\n*.pyc\n.env\nvenv/\n*.egg-info/\ndist/\nbuild/\n.pytest_cache/\n"
            ),
        },
        "react": {
            "src/App.tsx": (
                "export default function App() {{\n"
                "  return (\n"
                '    <div className="min-h-screen bg-gray-50">\n'
                "      <h1>{name}</h1>\n"
                "    </div>\n"
                "  );\n"
                "}}\n"
            ),
            "src/main.tsx": (
                "import {{ StrictMode }} from 'react';\n"
                "import {{ createRoot }} from 'react-dom/client';\n"
                "import App from './App';\n"
                "import './index.css';\n\n"
                "createRoot(document.getElementById('root')!).render(\n"
                "  <StrictMode><App /></StrictMode>\n"
                ");\n"
            ),
            "package.json": (
                '{{\n  "name": "{name}",\n  "version": "0.1.0",\n'
                '  "type": "module",\n  "scripts": {{\n'
                '    "dev": "vite",\n    "build": "tsc && vite build",\n'
                '    "preview": "vite preview"\n  }},\n'
                '  "dependencies": {{\n'
                '    "react": "^18.3.0",\n    "react-dom": "^18.3.0"\n  }},\n'
                '  "devDependencies": {{\n'
                '    "@vitejs/plugin-react": "^4.3.0",\n'
                '    "typescript": "^5.5.0",\n    "vite": "^5.4.0"\n  }}\n}}\n'
            ),
            "tsconfig.json": (
                '{{\n  "compilerOptions": {{\n'
                '    "target": "ES2020",\n    "module": "ESNext",\n'
                '    "jsx": "react-jsx",\n    "strict": true\n  }}\n}}\n'
            ),
        },
        "database": {
            "migrations/001_init.sql": (
                "-- Initial schema\n"
                "CREATE TABLE IF NOT EXISTS {name} (\n"
                "    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),\n"
                "    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),\n"
                "    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()\n"
                ");\n"
            ),
            "alembic.ini": (
                "[alembic]\n"
                "script_location = migrations\n"
                "sqlalchemy.url = postgresql://localhost/{name}\n"
            ),
        },
    }

    def generate(self, architecture: dict[str, Any], project_name: str = "") -> dict[str, str]:
        """Generate scaffolding files from an architecture plan."""
        name = project_name or "my-project"
        files: dict[str, str] = {}
        components = architecture.get("components", [])
        tech = architecture.get("tech_stack", {})

        frameworks = set(f.lower() for f in tech.get("frameworks", []))
        databases = tech.get("databases", [])

        if "fastapi" in frameworks or any(c.get("type") == "service" for c in components):
            for path, template in self.TEMPLATES["fastapi"].items():
                files[path] = template.format(name=name)

        if "react" in frameworks or any(c.get("type") == "application" for c in components):
            for path, template in self.TEMPLATES["react"].items():
                files[f"frontend/{path}"] = template.format(name=name)

        if databases or any(c.get("type") == "infrastructure" for c in components):
            for path, template in self.TEMPLATES["database"].items():
                files[path] = template.format(name=name.replace("-", "_"))

        files["README.md"] = self._generate_readme(name, components, tech)
        files[".env.example"] = self._generate_env(name, tech)

        return files

    @staticmethod
    def _generate_readme(
        name: str,
        components: list[dict[str, Any]],
        tech: dict[str, Any],
    ) -> str:
        lines = [
            f"# {name}\n\n",
            "## Architecture\n\n",
        ]
        for comp in components:
            lines.append(f"- **{comp.get('name', 'module')}**: {comp.get('description', '')}\n")
        lines.append("\n## Tech Stack\n\n")
        for category, items in tech.items():
            if items:
                lines.append(f"- {category.title()}: {', '.join(items)}\n")
        lines.extend(
            [
                "\n## Quick Start\n\n",
                "```bash\npip install -r requirements.txt\n",
                "uvicorn app.main:app --reload\n```\n",
            ]
        )
        return "".join(lines)

    @staticmethod
    def _generate_env(name: str, tech: dict[str, Any]) -> str:
        lines = [
            f"# {name} environment\n",
            f"APP_NAME={name}\n",
            "APP_ENV=development\n",
            "DEBUG=true\n",
            "LOG_LEVEL=INFO\n",
        ]
        if "PostgreSQL" in tech.get("databases", []):
            lines.append(f"DATABASE_URL=postgresql://localhost/{name.replace('-', '_')}\n")
        if "Redis" in tech.get("infrastructure", []):
            lines.append("REDIS_URL=redis://localhost:6379/0\n")
        return "".join(lines)

    def get_supported_templates(self) -> list[str]:
        return list(self.TEMPLATES.keys())
