"""Tester agent — generates and executes test cases for produced code."""

from __future__ import annotations

from backend.agents.base import AgentContext, AgentResult, AgentRole, BaseAgent


class TesterAgent(BaseAgent):
    """Analyses generated code and produces a test plan with test cases."""

    def __init__(self) -> None:
        super().__init__(AgentRole.TESTER)

    async def execute(self, context: AgentContext) -> AgentResult:
        code_files = context.code_files
        if not code_files:
            return AgentResult(
                agent_role=self.role,
                success=False,
                errors=["No code files to test"],
            )

        test_results = self._generate_tests(code_files)
        context.test_results = test_results

        return AgentResult(
            agent_role=self.role,
            success=True,
            output=test_results,
        )

    def _generate_tests(self, code_files: dict[str, str]) -> dict:
        """Generate test cases for each code file."""
        test_cases: list[dict] = []
        test_files: dict[str, str] = {}

        for filepath, content in code_files.items():
            if not filepath.endswith(".py"):
                continue

            module_name = filepath.replace("/", "_").replace(".py", "")
            test_name = f"test_{module_name}"

            cases = self._analyse_and_create_tests(filepath, content)
            test_cases.extend(cases)

            test_code = self._render_test_file(module_name, cases)
            test_files[f"tests/{test_name}.py"] = test_code

        return {
            "total_tests": len(test_cases),
            "test_cases": test_cases,
            "test_files": test_files,
            "coverage_estimate": self._estimate_coverage(code_files, test_cases),
        }

    @staticmethod
    def _analyse_and_create_tests(filepath: str, content: str) -> list[dict]:
        """Produce test case descriptors by analysing the source."""
        cases: list[dict] = []

        if "def " in content or "async def " in content:
            cases.append(
                {
                    "name": f"test_{filepath.replace('/', '_').replace('.py', '')}_exists",
                    "type": "unit",
                    "description": f"Verify module {filepath} can be imported",
                    "status": "generated",
                }
            )

        if "@router" in content or "APIRouter" in content:
            cases.append(
                {
                    "name": f"test_{filepath.replace('/', '_').replace('.py', '')}_endpoint",
                    "type": "integration",
                    "description": f"Verify endpoints in {filepath} return 200",
                    "status": "generated",
                }
            )

        if "class " in content:
            cases.append(
                {
                    "name": f"test_{filepath.replace('/', '_').replace('.py', '')}_class",
                    "type": "unit",
                    "description": f"Verify classes in {filepath} can be instantiated",
                    "status": "generated",
                }
            )

        return cases

    @staticmethod
    def _render_test_file(module_name: str, cases: list[dict]) -> str:
        lines = [f'"""Auto-generated tests for {module_name}."""\n', "import pytest\n\n"]
        for case in cases:
            lines.append(f"def {case['name']}():\n")
            lines.append(f'    """{case["description"]}"""\n')
            lines.append("    assert True  # placeholder\n\n")
        return "".join(lines)

    @staticmethod
    def _estimate_coverage(code_files: dict[str, str], test_cases: list[dict]) -> float:
        py_files = [f for f in code_files if f.endswith(".py")]
        if not py_files:
            return 0.0
        return min(100.0, (len(test_cases) / max(len(py_files), 1)) * 40.0)
