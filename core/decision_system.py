class DecisionSystem:
    """决策系统 / Decision system"""
    def __init__(self):
        self.decision_tree = self._build_decision_tree()
        self.decision_weights = {
            "performance_impact": 0.4,
            "resource_cost": 0.3,
            "priority_level": 0.2,
            "cooperation_benefit": 0.1
        } 