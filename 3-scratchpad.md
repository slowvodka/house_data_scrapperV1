# 🧪 Scratchpad

> Think here BEFORE coding. Clear after feature complete.

---

## Refactoring: Rename src/ to scraper/

### Goal
Rename `src/` folder to `scraper/` to better reflect that this is the house data scraper module, preparing for a second part/module in the future.

### Changes Required
1. **Folder rename:** `src/` → `scraper/`
2. **Import updates:** All `from src.` → `from scraper.`
3. **Documentation:** Update all references in docs
4. **Scripts:** Update scrape_*.py files
5. **CLI:** Update `python -m src.cli` → `python -m scraper.cli`
6. **Tests:** Verify all tests still pass

### Files to Update
- All Python files with `from src.` imports (45+ occurrences)
- `.cursorrules` (project structure section)
- `1-core.md` (module paths)
- `2-iteration.md` (if references src/)
- `README.md` (usage examples)
- `scrape_*.py` scripts

### Risk Assessment
- **Low risk:** Simple find/replace operation
- **Test coverage:** 117 tests should catch any missed imports
- **Rollback:** Easy git revert if needed

---
