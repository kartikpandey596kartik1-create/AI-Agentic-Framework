"""
Constitutional AI System
Implements ethical guidelines and decision-making framework for AI agents
"""

import yaml
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

class ConstitutionLevel(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class ConstitutionalAI:
    """
    Constitutional AI system that governs agent behavior based on defined principles
    Similar to Claude's constitutional approach
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.principles = self._load_default_principles()
        self.violation_history = []
        
        if config_path:
            self.load_constitution(config_path)
    
    def _load_default_principles(self) -> Dict[str, Any]:
        """Load default constitutional principles"""
        return {
            "core_values": {
                "helpfulness": {
                    "priority": 1,
                    "description": "Be maximally helpful within ethical bounds",
                    "weight": 1.0
                },
                "harmlessness": {
                    "priority": 1,
                    "description": "Avoid causing harm or promoting harmful content",
                    "weight": 1.0
                },
                "honesty": {
                    "priority": 1,
                    "description": "Provide accurate and truthful information",
                    "weight": 1.0
                }
            },
            "behavioral_guidelines": {
                "respect_autonomy": {
                    "description": "Respect user autonomy and decision-making",
                    "enabled": True
                },
                "transparency": {
                    "description": "Be transparent about capabilities and limitations",
                    "enabled": True
                },
                "privacy": {
                    "description": "Protect user privacy and data",
                    "enabled": True
                },
                "fairness": {
                    "description": "Treat all users fairly and without bias",
                    "enabled": True
                }
            },
            "prohibited_actions": {
                "harm": {
                    "level": ConstitutionLevel.CRITICAL,
                    "categories": [
                        "physical_harm",
                        "psychological_harm",
                        "financial_harm",
                        "reputational_harm"
                    ]
                },
                "illegal_activities": {
                    "level": ConstitutionLevel.CRITICAL,
                    "categories": [
                        "illegal_instructions",
                        "fraud",
                        "theft",
                        "violence"
                    ]
                },
                "misinformation": {
                    "level": ConstitutionLevel.HIGH,
                    "categories": [
                        "deliberate_falsehoods",
                        "conspiracy_theories",
                        "medical_misinformation"
                    ]
                },
                "privacy_violations": {
                    "level": ConstitutionLevel.HIGH,
                    "categories": [
                        "data_theft",
                        "unauthorized_access",
                        "doxxing"
                    ]
                }
            },
            "decision_framework": {
                "conflict_resolution": "prioritize_safety_over_helpfulness",
                "uncertainty_handling": "acknowledge_and_clarify",
                "ethical_dilemmas": "apply_utilitarian_with_deontological_constraints"
            }
        }
    
    def load_constitution(self, config_path: str):
        """Load constitution from YAML configuration file"""
        try:
            with open(config_path, 'r') as f:
                custom_principles = yaml.safe_load(f)
                self.principles.update(custom_principles)
            self.logger.info(f"Constitution loaded from {config_path}")
        except Exception as e:
            self.logger.error(f"Failed to load constitution: {e}")
    
    def evaluate_action(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate an action against constitutional principles
        
        Args:
            action: The proposed action
            context: Context information about the action
            
        Returns:
            Dict containing evaluation results
        """
        evaluation = {
            "allowed": True,
            "confidence": 1.0,
            "violations": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Check for prohibited actions
        for category, details in self.principles["prohibited_actions"].items():
            if self._check_prohibited_category(action, context, category, details):
                evaluation["allowed"] = False
                evaluation["violations"].append({
                    "category": category,
                    "level": details["level"].value,
                    "reason": f"Action violates {category} principle"
                })
        
        # Apply behavioral guidelines
        for guideline, config in self.principles["behavioral_guidelines"].items():
            if config["enabled"]:
                guideline_check = self._apply_guideline(action, context, guideline)
                if not guideline_check["passed"]:
                    evaluation["warnings"].append(guideline_check["message"])
                    evaluation["confidence"] *= 0.9
        
        # Generate recommendations
        if evaluation["warnings"] or evaluation["violations"]:
            evaluation["recommendations"] = self._generate_recommendations(
                evaluation["violations"],
                evaluation["warnings"]
            )
        
        return evaluation
    
    def _check_prohibited_category(
        self,
        action: str,
        context: Dict[str, Any],
        category: str,
        details: Dict[str, Any]
    ) -> bool:
        """Check if action falls into prohibited category"""
        # This is a simplified check - in production, use ML models
        prohibited_keywords = {
            "harm": ["harm", "hurt", "damage", "injure", "kill", "destroy"],
            "illegal_activities": ["hack", "steal", "fraud", "illegal", "crime"],
            "misinformation": ["fake news", "false claim", "conspiracy"],
            "privacy_violations": ["private data", "passwords", "steal information"]
        }
        
        action_lower = action.lower()
        if category in prohibited_keywords:
            return any(keyword in action_lower for keyword in prohibited_keywords[category])
        
        return False
    
    def _apply_guideline(
        self,
        action: str,
        context: Dict[str, Any],
        guideline: str
    ) -> Dict[str, Any]:
        """Apply a behavioral guideline to an action"""
        result = {"passed": True, "message": ""}
        
        guideline_checks = {
            "respect_autonomy": self._check_autonomy,
            "transparency": self._check_transparency,
            "privacy": self._check_privacy,
            "fairness": self._check_fairness
        }
        
        if guideline in guideline_checks:
            result = guideline_checks[guideline](action, context)
        
        return result
    
    def _check_autonomy(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if action respects user autonomy"""
        coercive_terms = ["must", "have to", "forced", "required without choice"]
        has_coercion = any(term in action.lower() for term in coercive_terms)
        
        return {
            "passed": not has_coercion,
            "message": "Action may not respect user autonomy" if has_coercion else ""
        }
    
    def _check_transparency(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if action maintains transparency"""
        deceptive_terms = ["hide", "conceal", "deceive", "trick", "mislead"]
        has_deception = any(term in action.lower() for term in deceptive_terms)
        
        return {
            "passed": not has_deception,
            "message": "Action may lack transparency" if has_deception else ""
        }
    
    def _check_privacy(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if action protects privacy"""
        privacy_risks = ["share personal", "expose data", "leak information"]
        has_risk = any(risk in action.lower() for risk in privacy_risks)
        
        return {
            "passed": not has_risk,
            "message": "Action may violate privacy" if has_risk else ""
        }
    
    def _check_fairness(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if action is fair"""
        bias_terms = ["discriminate", "prejudice", "unfair treatment"]
        has_bias = any(term in action.lower() for term in bias_terms)
        
        return {
            "passed": not has_bias,
            "message": "Action may not be fair to all parties" if has_bias else ""
        }
    
    def _generate_recommendations(
        self,
        violations: List[Dict],
        warnings: List[str]
    ) -> List[str]:
        """Generate recommendations based on violations and warnings"""
        recommendations = []
        
        if violations:
            recommendations.append("Critical: Revise action to comply with constitutional principles")
            for violation in violations:
                recommendations.append(
                    f"Address {violation['category']} violation at {violation['level']} level"
                )
        
        if warnings:
            recommendations.append("Consider revising to address the following concerns:")
            recommendations.extend(warnings)
        
        return recommendations
    
    def log_decision(self, action: str, evaluation: Dict[str, Any], outcome: str):
        """Log decision for transparency and learning"""
        decision_log = {
            "action": action,
            "evaluation": evaluation,
            "outcome": outcome,
            "timestamp": self._get_timestamp()
        }
        
        self.violation_history.append(decision_log)
        
        if not evaluation["allowed"]:
            self.logger.warning(f"Constitutional violation prevented: {action}")
    
    def get_ethics_summary(self) -> Dict[str, Any]:
        """Get summary of constitutional adherence"""
        total_decisions = len(self.violation_history)
        violations = sum(1 for d in self.violation_history if not d["evaluation"]["allowed"])
        
        return {
            "total_decisions": total_decisions,
            "violations_prevented": violations,
            "compliance_rate": (total_decisions - violations) / total_decisions if total_decisions > 0 else 1.0,
            "principles": self.principles["core_values"]
        }
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
