# System Quality Standards

## Domain-Agnosticism & Test Data Leakage

To prevent attention breakdown and test data leakage ("Whack-a-mole" optimization), the system enforces a universal standardization across the entire rule library (Seed Data).

All complex assertions and causality-evaluating atoms MUST include an abstract `contrastive_example` field.
The contrastive examples MUST use universal abstract variables (X, Y, Z) and must NEVER reference any specific domain, test case, or real-world entity.

### Rule: Universal Abstract Variables
- **Acceptable:** "X affects Y via Z"
- **Unacceptable:** "X is associated with Y" (Lacks mechanism/causality)
- **Unacceptable:** "This is the best approach for all situations, as demonstrated by the recent study published in the Journal of Applied Science." (Domain-specific reference causing data leakage)

This structural mandate guarantees that the system remains purely deterministic and universally applicable across all evaluation matrices without overfitting to historical data.
