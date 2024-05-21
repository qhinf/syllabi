# Handleiding code stelen

Je kunt op internet heel veel code vinden die jou helpt om je doel te bereiken, maar mag je die code ook zomaar gebruiken? In sommige modules van het parcours Informatica is het toegestaan om code in meer of mindere mate te kopiëren. **Wil je kopiëren? Check dan altijd even bij de docent van de betreffende module of kopiëren of samenwerken is toegestaan!**.

En dan nu terug naar de code op het internet. *Mag je die code zomaar gebruiken?* Het antwoord is natuurlijk nee, bijna niets mag "zomaar". En op school is afkijken meestal ook niet de bedoeling. In deze module, en in het echte leven, mag je code op internet wel gebruiken, als je aan deze voorwaarden voldoet:

- De code heeft een open source licentie. Dit betekent dat de maker van de code jou expliciet toestemming geeft om hun code te gebruiken, mits je aan de voorwaarden van de licentie voldoet. Bekende licenties zijn bijvoorbeeld de MIT, Apache, GPL en MPL licenties (maar er zijn er nog veel meer). Als er geen licentie is, zit er copyright op de code en mag je die dus niet kopiëren.

  De meeste code op [GitHub](https://github.com) heeft zo’n licentie, maar dat is niet alijd zo. Let dus goed op!

  Een andere site waar je veel korte stukjes code kunt vinden is [StackOverflow](https://stackoverflow.com). De code daar heeft een [CC BY-SA](https://creativecommons.org/licenses/by-sa/4.0/deed.nl) licentie. Dat betekent dat je deze code mag gebruiken, mits je de naam van de maker vermeld.

- Je maakt in je programma duidelijk welke stukken code je waarvandaan hebt gehaald. Als je code van een website hebt, geef dan een link naar die website. Als je het uit een video hebt overgenomen, link dan naar die video. Ook als je de code zelf intypt aan de hand van een tutorial, neem je code van iemand anders over en moet je dus de bron vermelden. Als je dat niet doet, is het plagiaat en wordt je werk niet beoordeeld!

  En ja, ook als je wijzigingen in de code maakt, moet je nog steeds naar het origineel linken. Voor je project is het dan wel een goed idee om in het commentaar ook uit te leggen wat je veranderd hebt.

Naast code van het internet, kun je natuurlijk ook code krijgen van een klasgenoot (of iemand anders) of samen met iemand iets schrijven. Ook in dat geval moet je dat duidelijk vermelden, ook al heb je geen link. Als we in twee projecten dezelfde code tegenkomen zonder bronvermelding, dan gelden beide gevallen als plagiaat en worden beide projecten niet beoordeeld!

Voorbeeld van hoe je in de code een bron kunt vermelden:

```java
// Class Eye via https://processing.org/examples/arctangent.html
// Ik heb de variabelenamen vertaald naar het Nederlands en
// de kleur veranderd in oranje.
class Oog {
  int x, y;
  int grootte;
  float hoek = 0.0;
  
  Oog(int tx, int ty, int ts) {
    x = tx;
    y = ty;
    grootte = ts;
 }

  void update(int mx, int my) {
    angle = atan2(my-y, mx-x);
  }
  
  void display() {
    pushMatrix();
    translate(x, y);
    fill(255);
    ellipse(0, 0, grootte, grootte);
    rotate(hoek);
    fill(240, 153, 0);
    ellipse(grootte/4, 0, grootte/2, grootte/2);
    popMatrix();
  }
}
```
