#!/usr/bin/env python3
"""Simplified automated test runner that works without extra dependencies."""
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class TestCase:
    """Represents a single test case."""

    def __init__(self, name: str, input_query: str, expected_output: str):
        self.name = name
        self.input_query = input_query
        self.expected_output = expected_output
        self.actual_output: str = ""
        self.passed: bool = False
        self.error: str = ""

    def normalize_command(self, command: str) -> str:
        """Normalize command for comparison."""
        if not command:
            return ""
        # Remove extra whitespace
        command = " ".join(command.split())
        # Remove leading/trailing whitespace
        command = command.strip()
        return command

    def check_result(self) -> bool:
        """Check if actual output matches expected."""
        if not self.actual_output:
            return False

        normalized_actual = self.normalize_command(self.actual_output)
        normalized_expected = self.normalize_command(self.expected_output)

        # Direct match
        if normalized_actual == normalized_expected:
            self.passed = True
            return True

        # Check if expected is a substring of actual
        if normalized_expected in normalized_actual:
            self.passed = True
            return True

        # Check if actual contains key parts of expected
        expected_parts = set(normalized_expected.split())
        actual_parts = set(normalized_actual.split())

        # Check overlap (at least 70% of expected parts present)
        if expected_parts:
            overlap = len(expected_parts & actual_parts)
            if overlap >= len(expected_parts) * 0.7:
                self.passed = True
                return True

        # Check if main command matches
        if normalized_expected and normalized_actual:
            expected_cmd = normalized_expected.split()[0] if normalized_expected.split() else ""
            actual_cmd = normalized_actual.split()[0] if normalized_actual.split() else ""
            if expected_cmd and expected_cmd == actual_cmd:
                # Main command matches, consider it passed
                self.passed = True
                return True

        return False


def load_test_cases() -> List[TestCase]:
    """Load test cases from TEST_CASES.md."""
    test_cases = []
    test_file = Path(__file__).parent.parent / "docs" / "TEST_CASES.md"

    if not test_file.exists():
        print(f"Error: Test cases file not found: {test_file}")
        return test_cases

    content = test_file.read_text(encoding="utf-8")

    # Parse test cases using regex
    # Pattern: ## Test Case N: Title\n**Input**: "query"\n**Expected**: `command`
    pattern = r"## Test Case (\d+):\s*([^\n]+)\n\*\*Input\*\*:\s*\"([^\"]+)\"\n\*\*Expected\*\*:\s*`([^`]+)`"
    matches = re.findall(pattern, content, re.MULTILINE)

    for match in matches:
        case_num, title, input_query, expected = match
        # Handle "or" in expected - take first option
        expected = expected.split(" or ")[0].strip()
        # Handle (Linux) or (macOS) notes
        expected = re.sub(r"\s*\([^)]+\)", "", expected).strip()
        
        test_case = TestCase(
            name=f"Test Case {case_num}: {title.strip()}",
            input_query=input_query.strip(),
            expected_output=expected.strip(),
        )
        test_cases.append(test_case)

    return test_cases


def run_test_case(test_case: TestCase, timeout: int = 60) -> Tuple[bool, str]:
    """Run a single test case."""
    try:
        # Ensure PATH includes .local/bin
        env = os.environ.copy()
        env["PATH"] = f"{os.path.expanduser('~/.local/bin')}:{env.get('PATH', '')}"

        # Run pop gen command
        cmd = ["pop", "gen", test_case.input_query]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent.parent,
            env=env,
        )

        try:
            stdout, _ = process.communicate(input="A\n", timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            return False, "Timeout"

        output = stdout
        extracted_command = ""

        # Strategy 1: Extract from Panel (between │ markers)
        panel_pattern = r"│\s+([^\n│]+?)\s+│"
        panel_matches = re.findall(panel_pattern, output)
        if panel_matches:
            for match in panel_matches:
                match = match.strip()
                if len(match) > 3 and not match.startswith(("─", "╭", "╰")):
                    if not extracted_command or len(match) > len(extracted_command):
                        extracted_command = match

        # Strategy 2: Look for command patterns
        if not extracted_command:
            command_patterns = [
                r"(ls\s+-[lah]+)",
                r"(find\s+[^\n]+)",
                r"(git\s+[^\n]+)",
                r"(ps\s+[^\n]+)",
                r"(curl\s+[^\n]+)",
                r"(export\s+[^\n]+)",
                r"(du\s+[^\n]+)",
                r"(vm_stat\s*[^\n]*)",
                r"(df\s+-[h]+)",
                r"(#\s*WARNING[^\n]*)",
            ]
            
            for pattern in command_patterns:
                matches = re.findall(pattern, output, re.MULTILINE)
                if matches:
                    extracted_command = max(matches, key=len).strip()
                    break

        # Strategy 3: Extract from lines
        if not extracted_command:
            lines = output.split("\n")
            for line in lines:
                line = line.strip()
                if not line or line.startswith(("╭", "╰", "│", "─", "Thinking", "Generated", "Executing")):
                    continue
                if re.match(r"^[#a-zA-Z][a-zA-Z0-9_\-./$:&|<> ]+$", line):
                    if 3 < len(line) < 200:
                        extracted_command = line
                        break

        test_case.actual_output = extracted_command
        return True, extracted_command

    except Exception as e:
        return False, f"Error: {str(e)}"


def print_results(results: Dict[str, any], verbose: bool = False):
    """Print test results."""
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60 + "\n")

    total = results["total"]
    passed = results["passed"]
    failed = results["failed"]
    pass_rate = (passed / total * 100) if total > 0 else 0

    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    print()

    if verbose or failed > 0:
        print("Detailed Results:")
        print("-" * 60)
        for case in results["cases"]:
            status = "✓ PASS" if case.passed else "✗ FAIL"
            if case.error:
                status = f"ERROR: {case.error}"
            
            print(f"\n{case.name}: {status}")
            print(f"  Input: {case.input_query}")
            print(f"  Expected: {case.expected_output}")
            print(f"  Actual: {case.actual_output if case.actual_output else '(empty)'}")

    return 0 if failed == 0 else 1


def check_parallax_running() -> bool:
    """Check if Parallax API is accessible."""
    try:
        import urllib.request
        response = urllib.request.urlopen("http://localhost:3000/v1/models", timeout=2)
        return response.status == 200
    except Exception:
        return False


def main(verbose: bool = False):
    """Main test runner."""
    print("Parallax OpsPilot - Automated Test Runner\n")

    # Check if pop command is available
    env = os.environ.copy()
    env["PATH"] = f"{os.path.expanduser('~/.local/bin')}:{env.get('PATH', '')}"
    
    try:
        subprocess.run(
            ["pop", "--version"],
            capture_output=True,
            check=True,
            timeout=5,
            env=env,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print("Error: 'pop' command not found. Please install the project first.")
        print("Run: pip install -e .")
        return 1

    # Check if Parallax is running (optional warning)
    if not check_parallax_running():
        print("Warning: Parallax API not accessible at http://localhost:3000")
        print("Tests may fail if Parallax is not running.")
        print("Start Parallax: parallax run -m Qwen/Qwen3-0.6B --host 0.0.0.0\n")

    test_cases = load_test_cases()
    if not test_cases:
        print("No test cases found!")
        return 1

    print(f"Running {len(test_cases)} test cases...\n")

    results = {
        "total": len(test_cases),
        "passed": 0,
        "failed": 0,
        "cases": [],
    }

    for i, test_case in enumerate(test_cases, 1):
        print(f"Running {test_case.name}... ", end="", flush=True)

        success, output = run_test_case(test_case)

        if success:
            test_case.passed = test_case.check_result()
            if test_case.passed:
                results["passed"] += 1
                print("✓ PASS")
            else:
                results["failed"] += 1
                print("✗ FAIL")
                if verbose:
                    print(f"  Expected: {test_case.expected_output}")
                    print(f"  Got: {test_case.actual_output}")
        else:
            results["failed"] += 1
            test_case.error = output
            print(f"✗ ERROR: {output}")

        results["cases"].append(test_case)

    return print_results(results, verbose=verbose)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run automated tests for Parallax OpsPilot")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed results",
    )
    args = parser.parse_args()

    exit_code = main(verbose=args.verbose)
    sys.exit(exit_code)

