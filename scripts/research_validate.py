"""Run the isolated synthetic research suite and weight-free smoke harness."""

from scripts.dev import compose


def main():
    compose("run", "--rm", "tester", "python", "-m", "scripts.research_test")
    compose("run", "--rm", "tester", "python", "-m", "scripts.research_benchmark")


if __name__ == "__main__":
    main()
