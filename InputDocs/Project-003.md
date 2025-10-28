# Project-003: Time Tracking

## Problem
I need an easier way to see time spent on each day by dev.

## Solution
Create one new sheet called "Time Tracking". This sheet will have the following:

1. A Pivot Chart with the following data:
- Data Source: the "worklogs" sheet
- Filter by "Author"
- Row level 1: Date
- Row level 2: Issue Key
- Values: sum of "Time Spent (Hours)"

2. A Pivot Chart with the following data:
- Data Source: the "worklogs" sheet
- Column: "Author"
- Row level 1: Date
- Row level 2: Issue Key
- Values: sum of "Time Spent (Hours)"




