# Syllabi

Pull nieuwe wijzigingen van GitHub, inclusief geüpdatet submodules:

```
git pull --recurse-submodules
```

Voeg een nieuwe module of module-editie toe:

```
git submodule add -b <branch> --name <module>/<branch> https://github.com/qhinf/<module>_syllabus.git syllabi/<module>/<branch>
```

Update alle edities naar de nieuwste versie die op GitHub staat:

```
git submodule update --remote
```
