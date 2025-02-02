# Team: BeatBytes
### Contributors:
* Anthony Hill
* Liam Anthian

Tetress game demo found here - https://comp30024.pages.gitlab.unimelb.edu.au/2024s1/project-playground/

---
# Due Dates
### Part B: 13th of May, 11pm

Pits two `Agent` class implementations against each other and plays out a match between the two via the Unimelb 
implemented `referee` module. Different `Agent` implementations can be found in the 'agent' directory with the prefix "a_".

Our code can be ran in one of two manners. Firstly - clone whole directory, then do one of the two below:
* Via referee directly:  &nbsp;&nbsp;&nbsp;&nbsp;  python -m referee [agent_folder] [agent_folder]
  &nbsp;&nbsp;&nbsp;&nbsp;
  e.g.:
  * python -m referee agent.a_current agent.a_current
  * python -m referee agent.a_rdm agent.a_greedy
* Via `handler.py`:  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  python handler.py
  &nbsp;&nbsp;&nbsp;&nbsp; (adjust handler.py code to perform matchup requested)
