"""
Advanced 50-Question Benchmark for Data Scientist AI Agent
Testing advanced ML, analytics, and visualization capabilities on advanced_customer_behavior.csv
"""

from typing import List, Dict
import json

class TestQuestionBank:
    """Collection of 50 advanced test questions for evaluating the AI agent."""
    
    def __init__(self):
        self.questions = self._generate_test_questions()
    
    def _generate_test_questions(self) -> List[Dict]:
        """Generate 50 advanced benchmark test questions for the AI agent."""
        
        return [
            # 🧠 Predictive Modeling (Supervised Learning) - 5 questions
            {
                "id": 1,
                "question": "Predict ChurnFlag using Age, Income, PurchaseFrequency, and TenureMonths → visualize ROC curve",
                "category": "predictive_modeling",
                "expected_type": "model",
                "difficulty": "hard"
            },
            {
                "id": 2,
                "question": "Train regression to predict CustomerLifetimeValue from Income, PurchaseFrequency, and AvgOrderValue → plot actual vs predicted",
                "category": "predictive_modeling",
                "expected_type": "model",
                "difficulty": "hard"
            },
            {
                "id": 3,
                "question": "Classify MarketingChannel using Age, Income, EngagementScore → show confusion matrix",
                "category": "predictive_modeling",
                "expected_type": "model",
                "difficulty": "hard"
            },
            {
                "id": 4,
                "question": "Predict SatisfactionScore with regression → visualize feature importance",
                "category": "predictive_modeling",
                "expected_type": "model",
                "difficulty": "hard"
            },
            {
                "id": 5,
                "question": "Forecast AvgOrderValue over LastPurchaseDate → include prediction intervals",
                "category": "predictive_modeling",
                "expected_type": "model",
                "difficulty": "hard"
            },

            # 🤖 Advanced ML + Forecasting - 5 questions
            {
                "id": 6,
                "question": "Build Random Forest to predict ChurnFlag → show feature importances",
                "category": "advanced_ml",
                "expected_type": "model",
                "difficulty": "hard"
            },
            {
                "id": 7,
                "question": "Train Gradient Boosting for CustomerLifetimeValue → SHAP summary plot",
                "category": "advanced_ml",
                "expected_type": "model",
                "difficulty": "hard"
            },
            {
                "id": 8,
                "question": "Use XGBoost to predict ChurnFlag → precision-recall curve",
                "category": "advanced_ml",
                "expected_type": "model",
                "difficulty": "hard"
            },
            {
                "id": 9,
                "question": "Forecast Income growth trend by Region using time-series decomposition",
                "category": "advanced_ml",
                "expected_type": "analysis",
                "difficulty": "hard"
            },
            {
                "id": 10,
                "question": "Use Prophet/ARIMA to forecast CustomerLifetimeValue across time → actual vs predicted plot",
                "category": "advanced_ml",
                "expected_type": "model",
                "difficulty": "hard"
            },

            # 📊 Clustering & Dimensionality Reduction - 5 questions
            {
                "id": 11,
                "question": "Cluster customers using k-means on Income, Age, PurchaseFrequency, EngagementScore → 2D cluster plot",
                "category": "clustering",
                "expected_type": "model",
                "difficulty": "hard"
            },
            {
                "id": 12,
                "question": "Compare silhouette scores for k=2 to k=10 on clustering results",
                "category": "clustering",
                "expected_type": "analysis",
                "difficulty": "hard"
            },
            {
                "id": 13,
                "question": "Run PCA on Income, AvgOrderValue, CustomerLifetimeValue → scatter first two components",
                "category": "clustering",
                "expected_type": "visualization",
                "difficulty": "hard"
            },
            {
                "id": 14,
                "question": "Visualize t-SNE embedding for Age, Income, EngagementScore → color by ChurnFlag",
                "category": "clustering",
                "expected_type": "visualization",
                "difficulty": "hard"
            },
            {
                "id": 15,
                "question": "Perform hierarchical clustering on AvgOrderValue, CustomerLifetimeValue, Income → dendrogram",
                "category": "clustering",
                "expected_type": "visualization",
                "difficulty": "hard"
            },

            # 🎨 Advanced Visualizations - 5 questions
            {
                "id": 16,
                "question": "Violin plot of DiscountRate distribution by Region",
                "category": "advanced_visualization",
                "expected_type": "visualization",
                "difficulty": "medium"
            },
            {
                "id": 17,
                "question": "Box plot of Income by MarketingChannel",
                "category": "advanced_visualization",
                "expected_type": "visualization",
                "difficulty": "medium"
            },
            {
                "id": 18,
                "question": "Parallel coordinates for Age, Income, AvgOrderValue, CustomerLifetimeValue → colored by ChurnFlag",
                "category": "advanced_visualization",
                "expected_type": "visualization",
                "difficulty": "hard"
            },
            {
                "id": 19,
                "question": "Heatmap of average SupportTickets by Region × MarketingChannel",
                "category": "advanced_visualization",
                "expected_type": "visualization",
                "difficulty": "medium"
            },
            {
                "id": 20,
                "question": "Ridgeline plot of CustomerLifetimeValue across different SatisfactionScore",
                "category": "advanced_visualization",
                "expected_type": "visualization",
                "difficulty": "hard"
            },

            # 🔎 Explainability (XAI) - 5 questions
            {
                "id": 21,
                "question": "SHAP waterfall plot for predicting CustomerLifetimeValue",
                "category": "explainability",
                "expected_type": "visualization",
                "difficulty": "hard"
            },
            {
                "id": 22,
                "question": "SHAP force plot for 10 random churn predictions (ChurnFlag)",
                "category": "explainability",
                "expected_type": "visualization",
                "difficulty": "hard"
            },
            {
                "id": 23,
                "question": "LIME explanation for one churned customer (ChurnFlag=1)",
                "category": "explainability",
                "expected_type": "analysis",
                "difficulty": "hard"
            },
            {
                "id": 24,
                "question": "Partial Dependence Plot (PDP) for Income impact on CustomerLifetimeValue",
                "category": "explainability",
                "expected_type": "visualization",
                "difficulty": "hard"
            },
            {
                "id": 25,
                "question": "ICE curves for EngagementScore impact on ChurnFlag",
                "category": "explainability",
                "expected_type": "visualization",
                "difficulty": "hard"
            },

            # 📈 Survival & Risk Analysis - 5 questions
            {
                "id": 26,
                "question": "Kaplan-Meier survival curve for customer churn using TenureMonths + ChurnFlag",
                "category": "survival_analysis",
                "expected_type": "visualization",
                "difficulty": "hard"
            },
            {
                "id": 27,
                "question": "Cox Proportional Hazards model for churn risk with Age, Income, EngagementScore",
                "category": "survival_analysis",
                "expected_type": "model",
                "difficulty": "hard"
            },
            {
                "id": 28,
                "question": "Survival probability comparison by MarketingChannel",
                "category": "survival_analysis",
                "expected_type": "analysis",
                "difficulty": "hard"
            },
            {
                "id": 29,
                "question": "Hazard function plot for high vs low Income groups",
                "category": "survival_analysis",
                "expected_type": "visualization",
                "difficulty": "hard"
            },
            {
                "id": 30,
                "question": "Retention curves split by Region",
                "category": "survival_analysis",
                "expected_type": "visualization",
                "difficulty": "hard"
            },

            # ⚡ Anomaly & Risk Detection - 5 questions
            {
                "id": 31,
                "question": "Detect anomalies in CustomerLifetimeValue using Isolation Forest → visualize anomalies in scatter plot",
                "category": "anomaly_detection",
                "expected_type": "analysis",
                "difficulty": "hard"
            },
            {
                "id": 32,
                "question": "Autoencoder-based anomaly detection on Income and AvgOrderValue",
                "category": "anomaly_detection",
                "expected_type": "model",
                "difficulty": "hard"
            },
            {
                "id": 33,
                "question": "Local Outlier Factor (LOF) for spotting abnormal churners",
                "category": "anomaly_detection",
                "expected_type": "analysis",
                "difficulty": "hard"
            },
            {
                "id": 34,
                "question": "Highlight outliers in SupportTickets across Region",
                "category": "anomaly_detection",
                "expected_type": "visualization",
                "difficulty": "medium"
            },
            {
                "id": 35,
                "question": "Show anomaly scores over time for AvgOrderValue",
                "category": "anomaly_detection",
                "expected_type": "visualization",
                "difficulty": "hard"
            },

            # 📊 Business Insights & Advanced Metrics - 5 questions
            {
                "id": 36,
                "question": "RFM segmentation (Recency = LastPurchaseDate, Frequency = PurchaseFrequency, Monetary = AvgOrderValue) → segment customers",
                "category": "business_insights",
                "expected_type": "analysis",
                "difficulty": "hard"
            },
            {
                "id": 37,
                "question": "CLV vs Churn: Compare CustomerLifetimeValue distributions for churned (ChurnFlag=1) vs retained (0)",
                "category": "business_insights",
                "expected_type": "analysis",
                "difficulty": "medium"
            },
            {
                "id": 38,
                "question": "Loyalty analysis: relationship between TenureMonths and ReferralCount",
                "category": "business_insights",
                "expected_type": "analysis",
                "difficulty": "medium"
            },
            {
                "id": 39,
                "question": "ROI analysis: compare AvgOrderValue by DiscountRate buckets",
                "category": "business_insights",
                "expected_type": "analysis",
                "difficulty": "medium"
            },
            {
                "id": 40,
                "question": "Support efficiency: plot correlation between SupportTickets and SatisfactionScore",
                "category": "business_insights",
                "expected_type": "visualization",
                "difficulty": "medium"
            },

            # 🤯 Deep Dive ML + Viz - 5 questions
            {
                "id": 41,
                "question": "Gradient boosting model for churn → visualize SHAP dependence plot (EngagementScore vs churn probability)",
                "category": "deep_ml",
                "expected_type": "model",
                "difficulty": "hard"
            },
            {
                "id": 42,
                "question": "Counterfactual analysis: how much must Income change to flip churn prediction",
                "category": "deep_ml",
                "expected_type": "analysis",
                "difficulty": "hard"
            },
            {
                "id": 43,
                "question": "Fairness check: churn model performance across Region",
                "category": "deep_ml",
                "expected_type": "analysis",
                "difficulty": "hard"
            },
            {
                "id": 44,
                "question": "Explainability heatmap: SHAP feature impact per MarketingChannel",
                "category": "deep_ml",
                "expected_type": "visualization",
                "difficulty": "hard"
            },
            {
                "id": 45,
                "question": "Tree-based surrogate model explaining black-box churn classifier",
                "category": "deep_ml",
                "expected_type": "model",
                "difficulty": "hard"
            },

            # 🔮 Cutting-Edge Visualization - 5 questions
            {
                "id": 46,
                "question": "3D scatter of Income, AvgOrderValue, CustomerLifetimeValue colored by ChurnFlag",
                "category": "cutting_edge_viz",
                "expected_type": "visualization",
                "difficulty": "hard"
            },
            {
                "id": 47,
                "question": "Sankey diagram of MarketingChannel → Region → ChurnFlag",
                "category": "cutting_edge_viz",
                "expected_type": "visualization",
                "difficulty": "hard"
            },
            {
                "id": 48,
                "question": "Network graph of customer similarity (based on Income, Age, PurchaseFrequency)",
                "category": "cutting_edge_viz",
                "expected_type": "visualization",
                "difficulty": "hard"
            },
            {
                "id": 49,
                "question": "Animated time-series of AvgOrderValue by Region",
                "category": "cutting_edge_viz",
                "expected_type": "visualization",
                "difficulty": "hard"
            },
            {
                "id": 50,
                "question": "Customer journey funnel: from MarketingChannel → EngagementScore → ChurnFlag",
                "category": "cutting_edge_viz",
                "expected_type": "visualization",
                "difficulty": "hard"
            }
        ]
    
    def get_questions_by_category(self, category: str) -> List[Dict]:
        """Get all questions from a specific category."""
        return [q for q in self.questions if q["category"] == category]
    
    def get_questions_by_difficulty(self, difficulty: str) -> List[Dict]:
        """Get all questions of a specific difficulty."""
        return [q for q in self.questions if q["difficulty"] == difficulty]
    
    def get_all_questions(self) -> List[Dict]:
        """Get all test questions."""
        return self.questions
    
    def get_benchmark_categories(self) -> Dict[str, List[Dict]]:
        """Get questions organized by benchmark category."""
        return {
            "Predictive Modeling": self.get_questions_by_category("predictive_modeling"),
            "Advanced ML": self.get_questions_by_category("advanced_ml"),
            "Clustering & Dimensionality": self.get_questions_by_category("clustering"),
            "Advanced Visualizations": self.get_questions_by_category("advanced_visualization"),
            "Explainability (XAI)": self.get_questions_by_category("explainability"),
            "Survival & Risk Analysis": self.get_questions_by_category("survival_analysis"),
            "Anomaly Detection": self.get_questions_by_category("anomaly_detection"),
            "Business Insights": self.get_questions_by_category("business_insights"),
            "Deep ML + Viz": self.get_questions_by_category("deep_ml"),
            "Cutting-Edge Viz": self.get_questions_by_category("cutting_edge_viz")
        }
    
    def save_to_file(self, filename: str):
        """Save questions to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.questions, f, indent=2)
    
    def load_from_file(self, filename: str):
        """Load questions from a JSON file."""
        with open(filename, 'r') as f:
            self.questions = json.load(f)

if __name__ == "__main__":
    # Create and save the test question bank
    bank = TestQuestionBank()
    bank.save_to_file("advanced_test_questions.json")
    print(f"Generated {len(bank.questions)} advanced test questions")
    
    # Print categories and counts
    categories = bank.get_benchmark_categories()
    
    print("\n🔥 Advanced Benchmark Categories:")
    for cat, questions in categories.items():
        print(f"  {cat}: {len(questions)} questions")