from packages.services.agent_run_store import AgentRunStore


class DummySession:
    def __init__(self) -> None:
        self.added = []
        self.flush_count = 0

    def add(self, obj):
        self.added.append(obj)

    def flush(self):
        self.flush_count += 1


def test_create_agent_run_persists_record() -> None:
    session = DummySession()
    store = AgentRunStore(session)  # type: ignore[arg-type]

    record = store.create_agent_run(
        agent_name="source_planner_agent",
        strategy_version="source_planner_v1",
        mode="heuristic_scaffold",
        product_id=None,
        vendor_id=None,
        request_payload={"product_id": "p1"},
        response_payload={"proposals": []},
    )

    assert record.agent_name == "source_planner_agent"
    assert record.strategy_version == "source_planner_v1"
    assert session.flush_count == 1
    assert len(session.added) == 1


def test_create_agent_eval_run_persists_scorecard() -> None:
    session = DummySession()
    store = AgentRunStore(session)  # type: ignore[arg-type]

    record = store.create_agent_eval_run(
        agent_name="source_planner_agent",
        evaluator_version="agent_evaluator_v1",
        request_payload={"agent_name": "source_planner_agent"},
        response_payload={"scorecard": {"score": 1.0}},
        score=1.0,
        overall_passed=True,
    )

    assert record.evaluator_version == "agent_evaluator_v1"
    assert record.score == 1.0
    assert record.overall_passed is True
    assert session.flush_count == 1
