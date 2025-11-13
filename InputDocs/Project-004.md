#Project-004: Add JQL and fix Story Points

## Problem
Problem 1: 
The Story Points are not always being extracted from the correct field. Jira has 2 fields for Story Points: "Story Points" and "Story Points Estimate", the current implementation is only bringing one of them but some projects use the other one.

Problem 2: 
Some projects organize their issues in separate boards to identify sub-projects or threads in the same project, currently we do not offer a way to filter this.

## Solution
Solution to Problem 1: The "Story Points" field should be populated with the value of the "Story Points" or "Story Points Estimate" field, whichever is not null. If both are null then place a cero. If both are not null then place the value of the "Story Points" field.

Solution to Problem 2: 
Add a new input field called "JQL" to the input form. This field should be used to filter the issues based on the JQL query provided by the user. 
This filter applies to:
- Issues extracted for the given sprint
- Issue extracted for all open epics

It does NOT apply to the:
- Comments sheet
- worklogs sheet

