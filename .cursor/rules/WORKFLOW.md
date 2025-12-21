# 🔴 CRITICAL WORKFLOW RULES

## The Golden Rule: Architect → SE → Tester → Review

**NEVER skip steps. NEVER mix roles. ALWAYS follow this sequence.**

---

## Step-by-Step Workflow

### 1. Team Lead: Assign Architect
- User requests a feature
- Team Lead breaks down the task
- Team Lead assigns Architect ONLY
- Update `TEAM_STATUS.md` with Architect assignment

### 2. Architect: Create Design
- Read `TEAM_STATUS.md` for assignment
- Use `BRAINSTORM.md` for ideation
- Create design document in `docs/architecture/*.md` or `design-specs.md`
- Include:
  - Overview and requirements
  - Architecture and data models
  - Algorithm design
  - Edge cases
  - Implementation steps (for SE)
  - Testing considerations (for Tester)
- Clean `BRAINSTORM.md`
- Notify Team Lead: "Design complete"

### 3. Team Lead: Review Design & Assign SE
- Review Architect's design document
- Verify design is complete
- Assign SE to implement
- Update `TEAM_STATUS.md` with SE assignment

### 4. SE: Implement Code
- Read `TEAM_STATUS.md` for assignment
- Read Architect's design document (MANDATORY)
- Use `BRAINSTORM.md` for implementation notes
- Write production code in `scraper/` or `mortgage_return_scenario_calculator/`
- **DO NOT write any test code**
- **DO NOT write test assertions in production modules**
- Follow Architect's design exactly
- Clean `BRAINSTORM.md`
- Notify Team Lead: "Implementation complete"

### 5. Team Lead: Review Implementation & Assign Tester
- Review SE's implementation
- Verify code follows design
- Assign Tester to write tests
- Update `TEAM_STATUS.md` with Tester assignment

### 6. Tester: Write Tests
- Read `TEAM_STATUS.md` for assignment
- Read Architect's design document
- Read SE's implementation code
- Use `BRAINSTORM.md` for test case planning
- **Write ALL tests in `tests/` directory ONLY**
- **NEVER write tests in production modules**
- Write comprehensive test suite covering:
  - Happy paths
  - Edge cases from design
  - Error cases
  - Integration scenarios
- Run tests to verify they pass
- Clean `BRAINSTORM.md`
- Report results to Team Lead: "Tests complete"

### 7. Team Lead: Final Review & Approval
- Review all work:
  - Architect's design ✅
  - SE's implementation ✅
  - Tester's tests ✅
- **CRITICAL CHECK:** Verify tests are in `tests/` directory, NOT in modules
- Summarize for user
- Request user approval

---

## 🔴 CRITICAL RULES

### Test Location Enforcement
- ✅ **ALL tests MUST be in `tests/` directory**
- ❌ **NO test code in `scraper/` or `mortgage_return_scenario_calculator/`**
- ❌ **NO test assertions in production `.py` files**
- ❌ **NO `if __name__ == "__main__"` blocks with test logic**
- ✅ **Example/demo code is OK, but NO assertions**

### Role Separation
- **Architect:** Plans only, no code, no tests
- **SE:** Codes only, no plans, no tests
- **Tester:** Tests only, no code, no plans
- **Team Lead:** Orchestrates only, no code, no tests, no plans

### Sequence Enforcement
- **NEVER skip Architect step** - Always design first
- **NEVER skip SE step** - Always implement after design
- **NEVER skip Tester step** - Always test after implementation
- **NEVER mix roles** - Each agent does ONLY their job

### File Locations
- **Designs:** `docs/architecture/*.md` or `design-specs.md`
- **Production Code:** `scraper/` or `mortgage_return_scenario_calculator/`
- **Tests:** `tests/` directory ONLY
- **Temporary Scripts:** `temp_scripts/`
- **Documentation:** `MISSION.md`, `ROADMAP.md`, `TEAM_STATUS.md`, `BRAINSTORM.md`

---

## Violation Handling

If you see a violation:
1. **Stop immediately**
2. **Report to Team Lead**
3. **Do NOT fix it yourself** (unless you're the Team Lead)
4. **Wait for proper assignment**

---

## Example: Adding Tax Integration

1. **Team Lead:** "Architect, design tax integration into ScenarioResult"
2. **Architect:** Creates `docs/architecture/tax_integration_design.md`
3. **Team Lead:** "SE, implement tax integration per design"
4. **SE:** Implements in `calculator.py` and `models.py`
5. **Team Lead:** "Tester, write tests for tax integration"
6. **Tester:** Writes `tests/test_mortgage_calculator/test_tax_integration.py`
7. **Team Lead:** Reviews all, requests user approval

---

**Remember: The workflow is sacred. Follow it strictly.**

