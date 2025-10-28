# Project-002: Progress graphs

## Problem

The current Jira API Extractor provides valuable sprint-level analytics, now we want to provide some out-of-the-box progress graphs to help users visualize their work.

## Solution

We will add 1 sheet to the output Excel file, called "Progress". This sheet will contain the following charts:

1. Sprint progress in percentage
This will be hozizontal bar chart, based on the "sprint" sheet. There should be 1 bar for each sprint from the input. 

The chart should have the following data:

- 1 bar for each epic
- In the x axis, the percentage of completition
- In the y axis, the epic name (on the left, one for each bar)
- The bar value should be the percentage of completed story points (done / total). Use the "status category" to calculate the amount of "done" points.

2. Sprint progress in story points
This will be hozizontal bar chart, based on the "sprint" sheet. There should be 1 bar for each sprint from the input. 

The chart should have the following data:

- 1 bar for each epic
- In the x axis, story points
- In the y axis, the epic name (on the left, one for each bar)
- The bar must be divided in 3 sections. The first section should be the amount of "done" points. The second section should be the amount of "in progress" points. The third section should be the amount of "to do" points. Use the "status category" to calculate the amount of points on each section. The total length of the bar should be the sum of all story points of the epic.

3. Sprint composition
This will be a pie chart, based on the "sprint" sheet. There should be 1 pie for each sprint from the input. 

The chart should have the following data:

- The total will be the sum of all story points in the sprint
- There must be a slice for each epic
- The slice value should be the percentage of story points of the epic (done / total). Use the "status category" to calculate the amount of "done" points.

4. Epic progress in percentage
This will be hozizontal bar chart, based on the "epics with label" sheet.

The chart should have the following data:

- 1 bar for each epic
- In the x axis, the percentage of completition
- In the y axis, the epic name (on the left, one for each bar)
- The bar value should be the percentage of completed story points (done / total). Use the "status category" to calculate the amount of "done" points.

5. Epic progress in story points
This will be hozizontal bar chart, based on the "epics with label" sheet.

The chart should have the following data:

- 1 bar for each epic
- In the x axis, story points
- In the y axis, the epic name (on the left, one for each bar)
- The bar must be divided in 3 sections. The first section should be the amount of "done" points. The second section should be the amount of "in progress" points. The third section should be the amount of "to do" points. Use the "status category" to calculate the amount of points on each section. The total length of the bar should be the sum of all story points of the epic.

4. Open Epic progress in percentage
This will be hozizontal bar chart, based on the "Open epics" sheet.

The chart should have the following data:

- 1 bar for each epic
- In the x axis, the percentage of completition
- In the y axis, the epic name (on the left, one for each bar)
- The bar value should be the percentage of completed story points (done / total). Use the "status category" to calculate the amount of "done" points.

5. Open Epic progress in story points
This will be hozizontal bar chart, based on the "Open epics" sheet.

The chart should have the following data:

- 1 bar for each epic
- In the x axis, story points
- In the y axis, the epic name (on the left, one for each bar)
- The bar must be divided in 3 sections. The first section should be the amount of "done" points. The second section should be the amount of "in progress" points. The third section should be the amount of "to do" points. Use the "status category" to calculate the amount of points on each section. The total length of the bar should be the sum of all story points of the epic.

