ECCRS Workbenches:

Each folder contains the ECCRS rules learned on that dataset, a stratified
holdout of test instances, and the corresponding ECCRS Most-Specific-Wins
(MSW) predictions. 

Dataset Sources:

| `cancer` | [Wisconsin Breast Cancer](https://archive.ics.uci.edu/dataset/15/breast+cancer+wisconsin+original)
| `bank` | [Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing)
| `mushroom` | [Mushroom](https://archive.ics.uci.edu/dataset/73/mushroom)

Alignment assumptions:

All three workbench rule sets satisfy the assumptions required for the
ECCRS–KLM alignment theorem: strict global exception closure, sanity, and
no total override. See `assumptions.json` in each folder.