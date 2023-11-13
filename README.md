# Syllabi

Pull nieuwe wijzigingen van GitHub, inclusief geüpdatet submodules:

```
git pull --recurse-submodules
```

Als er remote een nieuwe submodule is toegevoegd (door iemand anders dus), dan moet die ook nog lokaal geregistreerd worden voordat alle submodule commando's daarop werken. Dit registreert alle submodules die in .gitmodules staan:

```
git submodule init
```

Voeg een nieuwe module of module-editie toe:

```
git submodule add -b <branch> --name <module>/<branch> https://github.com/qhinf/<module>_syllabus.git syllabi/<module>/<branch>
```

Update alle edities naar de nieuwste versie die op GitHub staat:

```
git submodule update --remote
```
