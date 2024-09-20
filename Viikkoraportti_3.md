1. Tehty tällä viikolla:
- [x] vanhan frontin poistaminen toimii nyt myös CSP:n kanssa. Ongelma oli 'botGame.py':ssä; kullakin rundilla piti (1) ensin lisätä uudet frontin jäsenet, ja (2) sen jälkeen seuloa näistä pois vanhat, eikä toisinpäin (syy oli siis kunkin yksittäisen rundin kattavissa, rundin päätyttyä poistettavissa kirjanpitorakenteissa - toisin päin tehtäessä, eli (2) (1), lisättiin uudet frontin jäsenet vanhojen poiston jälkeen, mutta osa näistä oli jo käynyt saman rundin aikana vanhoiksi. Järjestyksen vaihtaminen poisti tämän ongelman.)

2. Miten edistynyt: 
3. Mitä opin:


4. Epäselvää
5. Seuraavaksi: jatkan `CSP_solver`-luokan tekemistä (korjaamista) ja selkiytän sen koodia niin paljon kuin mahdollista. Jos saan `CSP_solver`:in nähtävästi toimimaan, keskityn seuraavaksi testien tekemiseen, jotta voidaan selvittää, toimiiko solver oikeasti _kaikissa_ tapauksissa.
