# Syllabi

## Automatische updates

Goed geconfigureerde *\*_syllabus* repositories sturen updates automatisch door naar deze repo, zie de GitHub Actions configuratie van de [syllabus_template](https://github.com/qhinf/syllabus_template/blob/main/.github/workflows/update.yml). Daarvoor is een authenticatietoken nodig die eens per jaar vervangen moet worden:

1. Maak een nieuwe Personal Access Token [via deze link](https://github.com/settings/personal-access-tokens/new)
   - Kies een logische *Token name*
   - Zet de *Expiration* zo ver mogelijk in de toekomst (via custom kan dat tot één jaar)
   - Kies als *Resource owner* de qhinf organisatie
   - Onder *Repository access* kies de optie *Only select repositories* en kies de *qhinf/syllabi* repo
   - Bij *Permissions*, open de *Repository permissions* en zet de permissies voor *Actions* op *Access: Read and write*
   - Kopieer de token!
2. Bewerk de PAT_SYLLABI_UPDATE secret in de qhinf organisatie [via deze link](https://github.com/organizations/qhinf/settings/secrets/actions/PAT_SYLLABI_UPDATE)
   - Klik op de *enter a new value* link, plak de token uit de vorige stap en *Save changes*

## Handmatige updates

Voor handmatige updates zijn de volgende commando's relevant:

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
