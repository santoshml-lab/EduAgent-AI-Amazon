from agent import EduAgent


def main():
    agent = EduAgent()

    print("Testing EduAgent AI")
    print("=" * 40)

    test_cases = [
        "Create a 7 day study plan for Python",
        "Give me learning resources for machine learning",
        "Calculate 125 * 48"
    ]

    for user_input in test_cases:
        print(f"\nUser: {user_input}")

        result = agent.process(user_input)

        print("Agent:")
        print(result)


if __name__ == "__main__":
    main()
