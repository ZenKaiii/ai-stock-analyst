from ai_stock_analyst.agents.analyzer import StockAnalyzer
from ai_stock_analyst.agents.base import AnalysisResult, BaseAgent


class DummyAgent(BaseAgent):
    def __init__(self):
        super().__init__("DummyAgent")

    def analyze(self, data):
        return AnalysisResult(
            agent_name=self.name,
            signal="HOLD",
            confidence=0.5,
            reasoning="dummy",
            indicators={},
            risks=[],
        )


def test_register_agent_updates_registry_and_pipeline():
    analyzer = StockAnalyzer()
    analyzer.register_agent("dummy", DummyAgent())
    assert "dummy" in analyzer.agents
    assert "dummy" in analyzer.list_agents()
