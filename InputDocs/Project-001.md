# Project-001: Enhanced Epic and Sprint Analytics

## Problem

The current Jira API Extractor provides valuable sprint-level analytics, but users need deeper insights into:

1. **Sprint Planning Accuracy**: Story point estimates are not visible in the export, making it difficult to analyze sprint planning effectiveness and velocity trends.

2. **Epic-Level Tracking**: There's no way to track all work related to specific epics across multiple sprints. Users need to filter epics by labels and see all associated tickets regardless of sprint or date range.

3. **Open Work Visibility**: Users cannot easily see all open work across epics, making it hard to understand current commitments and prioritize work.

4. **Issue Hierarchy**: Parent-child relationships between issues are not clearly visible, making it difficult to understand story breakdown and epic composition.

5. **Status Categorization**: The raw status values don't provide a high-level view of work progress (To Do vs In Progress vs Done).

## Appetite

**6 weeks** - This is a medium-sized enhancement that adds significant analytical capabilities without fundamentally changing the core architecture.

## Solution

We'll enhance the Jira API Extractor with three major improvements:

### 1. Enhanced Sprint Sheet
Add critical planning and hierarchy information to make sprint analysis more valuable.

### 2. Epic-Based Filtering
Introduce a new "Epics with Label" sheet that allows users to analyze all work under epics matching a specific label, independent of sprint or date constraints.

### 3. Open Work Dashboard
Create an "Open Epics" sheet that provides a comprehensive view of all in-progress work across the project.

## Breadboarding

### User Flow

```
┌─────────────────────────────────────────────────────────────┐
│ User Input (CLI/GUI)                                        │
├─────────────────────────────────────────────────────────────┤
│ • Project Key (existing)                                    │
│ • Sprint IDs (existing)                                     │
│ • Date Range (existing)                                     │
│ • Epic Label (NEW) ← Optional filter                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Data Extraction                                             │
├─────────────────────────────────────────────────────────────┤
│ 1. Fetch sprint issues (enhanced with story points + parent)│
│ 2. Fetch worklogs (existing)                               │
│ 3. Fetch comments (existing)                               │
│ 4. IF epic_label provided:                                 │
│    → Fetch epics with label                                │
│    → Fetch all issues in those epics                       │
│ 5. Fetch all open epics                                    │
│    → Fetch all issues in open epics                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Excel Export                                                │
├─────────────────────────────────────────────────────────────┤
│ • Sprint Sheets (ENHANCED)                                  │
│   - Story Points column                                     │
│   - Parent Key column                                       │
│   - Status Category column                                  │
│                                                             │
│ • Epics with Label Sheet (NEW - conditional)                │
│   - All columns from Sprint sheet                          │
│   - Epic Status column                                      │
│   - Only if epic_label provided                            │
│                                                             │
│ • Open Epics Sheet (NEW - always)                          │
│   - All columns from Sprint sheet                          │
│   - Epic Status column                                      │
│   - All tickets from non-done epics                        │
│                                                             │
│ • Work Logs (existing)                                      │
│ • Comments (existing)                                       │
│ • Charts (existing + new charts for epic sheets)           │
└─────────────────────────────────────────────────────────────┘
```

### Data Structure

```
Sprint Sheet (Enhanced)
┌──────────────┬─────────────┬──────────┬────────┬────────┬───────────────┬──────────────┬──────────────┬──────────────────┐
│ Issue Key    │ Issue Type  │ Summary  │ Status │ Sprint │ Parent Summary│ Story Points │ Parent Key   │ Status Category  │
│              │             │          │        │        │               │ (NEW)        │ (NEW)        │ (NEW)            │
└──────────────┴─────────────┴──────────┴────────┴────────┴───────────────┴──────────────┴──────────────┴──────────────────┘

Epics with Label Sheet (NEW)
┌──────────────┬─────────────┬──────────┬────────┬────────┬───────────────┬──────────────┬──────────────┬──────────────┬─────────────┐
│ Issue Key    │ Issue Type  │ Summary  │ Status │ Sprint │ Parent Summary│ Story Points │ Parent Key   │ Status Cat.  │ Epic Status │
└──────────────┴─────────────┴──────────┴────────┴────────┴───────────────┴──────────────┴──────────────┴──────────────┴─────────────┘

Open Epics Sheet (NEW)
┌──────────────┬─────────────┬──────────┬────────┬────────┬───────────────┬──────────────┬──────────────┬──────────────┬─────────────┐
│ Issue Key    │ Issue Type  │ Summary  │ Status │ Sprint │ Parent Summary│ Story Points │ Parent Key   │ Status Cat.  │ Epic Status │
└──────────────┴─────────────┴──────────┴────────┴────────┴───────────────┴──────────────┴──────────────┴──────────────┴─────────────┘
```

## Rabbit Holes

### 1. Story Points Field Variation
**Risk**: Different Jira instances use different custom fields for story points.

**Solution**: 
- Check common field names: `customfield_10016`, `customfield_10026`, `Story Points`
- Add configuration option to specify story points field ID
- Gracefully handle missing story points (show "N/A")

### 2. Epic Label vs Epic Link
**Risk**: Confusion between epic labels and epic links in Jira.

**Clarification**: 
- We're filtering epics BY their labels (tags on the epic itself)
- Then fetching all issues that are LINKED to those epics
- Use JQL: `type = Epic AND labels = 'label-name'`
- Then for each epic: `parent = {epic_key}` to get child issues

### 3. Status Category Mapping
**Risk**: Custom workflows might have non-standard status categories.

**Solution**:
- Use Jira's built-in status category API field (`statusCategory.name`)
- Standard categories: "To Do", "In Progress", "Done"
- Don't try to map custom statuses ourselves

### 4. Performance with Large Epics
**Risk**: Epics with hundreds of issues could slow down extraction.

**Solution**:
- Use pagination (already implemented)
- Add progress indicators in GUI
- Consider adding a limit/warning for very large result sets

### 5. Open Epics Definition
**Risk**: What counts as "open"?

**Clarification**:
- Open = Epic status category is NOT "Done"
- Include epics in "To Do" and "In Progress" categories
- Use JQL: `type = Epic AND statusCategory != Done`

## No-Gos

### Out of Scope for This Project

1. **Custom Field Mapping UI**: Users will need to configure story points field in `.env` file, not through GUI
2. **Historical Epic Analysis**: Only current epic state, not historical changes
3. **Epic Burndown Charts**: Just data export, no epic-specific charts yet
4. **Multiple Label Filtering**: Only single label filter, not AND/OR combinations
5. **Recursive Epic Hierarchies**: Only one level (Epic → Story/Task/Bug), not nested epics
6. **Epic Worklog Aggregation**: Not calculating total time per epic in this version

## Technical Approach

### API Endpoints Needed

```python
# New API calls required:

# 1. Get story points (already in issue fetch, just need to include field)
GET /rest/api/3/issue/{issueKey}?fields=customfield_10016

# 2. Get parent issue key (already available in issue fetch)
GET /rest/api/3/issue/{issueKey}?fields=parent

# 3. Get status category (already available in issue fetch)
GET /rest/api/3/issue/{issueKey}?fields=status

# 4. Search epics by label
GET /rest/api/3/search/jql?jql=type=Epic AND labels="{label_name}"

# 5. Get issues in epic (child issues)
GET /rest/api/3/search/jql?jql=parent={epic_key}

# 6. Get all open epics
GET /rest/api/3/search/jql?jql=type=Epic AND statusCategory!=Done
```

### Configuration Changes

Add to `.env` / `JiraExtractor.env`:
```
# Story Points custom field ID (varies by Jira instance)
JIRA_STORY_POINTS_FIELD=customfield_10016
```

### Code Changes Overview

1. **config.py**: Add story points field configuration
2. **jira_api.py**: 
   - Add methods: `get_epics_by_label()`, `get_issues_in_epic()`, `get_open_epics()`
   - Enhance existing issue fetch to include story points, parent key, status category
3. **excel_exporter.py**: 
   - Update sprint sheet columns
   - Add new sheet generation methods: `_write_epics_with_label_sheet()`, `_write_open_epics_sheet()`
4. **main.py**: Add `--epic_label` argument
5. **streamlit_app.py**: Add epic label input field
6. **charts_helper_enhanced.py**: Add charts for new sheets (optional)

## Success Criteria

### Must Have
- ✅ Sprint sheets include Story Points, Parent Key, and Status Category columns
- ✅ Epic label filtering works correctly
- ✅ "Epics with Label" sheet exports all issues from matching epics
- ✅ "Open Epics" sheet exports all issues from open epics
- ✅ Epic status is visible in epic-based sheets
- ✅ Backward compatibility: existing functionality still works
- ✅ CLI and GUI both support new epic label parameter

### Nice to Have
- 📊 Charts for epic-based sheets (status distribution, type distribution)
- 📈 Summary statistics for epic sheets (total issues, total story points)
- 🎨 Color coding for status categories in Excel
- 📝 Epic description in epic-based sheets

### Quality Bars
- No breaking changes to existing exports
- Graceful handling of missing data (story points, parent)
- Clear error messages if epic label not found
- Performance: < 30 seconds for 100 issues per epic
- Documentation updated (README, architecture.md, database.md)

## Open Questions

1. **Story Points Field**: Should we auto-detect the story points field or require configuration?
   - **Recommendation**: Start with configuration, add auto-detection later if needed

2. **Epic Label Input**: Single label or multiple labels?
   - **Decision**: Single label for MVP, can extend later

3. **Sheet Naming**: How to name epic-based sheets?
   - **Proposal**: "Epics with Label [{label_name}]" and "Open Epics"

4. **Empty Results**: What if no epics match the label?
   - **Behavior**: Create empty sheet with headers and show warning message

5. **Charts**: Should epic sheets have their own charts?
   - **Decision**: Add basic charts (status, type distribution) similar to sprint sheets

## Timeline Estimate

### Week 1-2: Sprint Sheet Enhancements
- Add story points field configuration
- Enhance issue fetching to include new fields
- Update sprint sheet export
- Test with various Jira instances

### Week 3-4: Epic Filtering
- Implement epic search by label
- Implement issue fetching for epics
- Create "Epics with Label" sheet export
- Add CLI and GUI parameters

### Week 5: Open Epics Sheet
- Implement open epic search
- Create "Open Epics" sheet export
- Add charts for epic sheets

### Week 6: Testing & Documentation
- Integration testing
- Update documentation
- User acceptance testing
- Bug fixes and polish

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Story points field varies by instance | High | High | Configuration option + common defaults |
| Large epics cause timeouts | Medium | Medium | Pagination + progress indicators |
| Epic label not found | Low | Medium | Clear error message + empty sheet |
| Status category not standard | Medium | Low | Use Jira's built-in category field |
| Performance degradation | Medium | Low | Batch API calls + caching |

## Future Enhancements

After this project, we could consider:

1. **Epic Burndown Data**: Track epic progress over time
2. **Multi-Label Filtering**: AND/OR combinations for epic labels
3. **Epic Hierarchy**: Support nested epics
4. **Custom Field Mapping**: GUI for configuring custom fields
5. **Epic Worklog Totals**: Aggregate time spent per epic
6. **Epic Dependencies**: Show dependencies between epics
7. **Roadmap View**: Timeline visualization of epics
