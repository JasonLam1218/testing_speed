class TestScenarios:
    SCENARIOS = [
        {"name": "Quick Math", "prompt": "What is 15+27?", "category": "simple"},
        {"name": "Short Explanation", "prompt": "Define AI in one sentence.", "category": "simple"},
        {"name": "Medium Analysis", "prompt": "Pros and cons of renewable energy.", "category": "medium"},
        {"name": "Code Generation", "prompt": "Python factorial function.", "category": "medium"},
        {"name": "Long Essay", "prompt": "Impact of social media.", "category": "complex"},
        {"name": "Technical Deep Dive", "prompt": "Explain quantum computing principles and applications.", "category": "complex"}
    ]

    @classmethod
    def get_scenarios_by_category(cls, cat):
        return [s for s in cls.SCENARIOS if s["category"] == cat]

    @classmethod
    def get_all_scenarios(cls):
        return cls.SCENARIOS
