```yaml
syllabi:
  module: # Naam van de module, op dezelfde manier als wat in GitHub gebruikt wordt
    repo: https://github.com/qhinf/module_syllabus.git # Link naar de Git repo voor deze syllabus
    revisions: # Dictionary van verschillende versies van de syllabus, bijvoorbeeld:
      2223-2: # Branch of tag voor de versie 22/23 blok 2, geen extra info nodig
  jbcursus:
    repo: https://github.com/eelcodijkstra/jbcursus.git # Extern materiaal, bijvoorbeeld van keuzethema's
      f633f473f59c9216e2a3725f12bba4bedccce5e0: # Commit hash voor een specifieke commit
        alias: v1 # Het alias wordt gebruikt in de UI en in urls ipv de commit hash
        jb_path: . # Pad naar het Jupyter Book als dat niet syllabus/ is
```