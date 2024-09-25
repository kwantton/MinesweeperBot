<b>Aiheen ydin: miinaharavabotin tekoäly, joka pystyy ratkaisemaan kaikki mahdolliset tilanteet (eli kaikki mahdolliset *ratkaistavissa olevat* tapaukset)</b>
- generoidaan miinaharavamappeja (pelejä, joissa miinajakaumat ovat erilaisia): mapissa rivejä on $r$, sarakkeita $s$, miinoja $m$, ja mapit voidaan Pythonissa esittää esim. listana listoja (lista rivejä); arvotaan $m$ miinaa koordinaateilla $(x,y)$. Mappien generoinnissa toistettavuutta varten testeissä voitaisiin käyttää seed-arvoa satunnaislukugeneraattorille, MUTTA on jo tehty kiinteitä (muuttumattomia) testejä `CSP_solver.py`-luokan `if __name__ == __main__`-osiossa.
- testausta varten voitaisiin generoida kahta luokkaa (toistaiseksi ei tehty, koska työn tekijä on todella harjaantunut tunnistamaan kummatkin tapaukset. Todistusaineisto : <a>https://minesweeper.online/player/2600486</a>):
  (1) mappeja, jotka ovat ratkaistavissa (ratkaistavissa kun aloitetaan klikkaamalla tiettyä kohtaa mappia)
  (2) mappeja, jotka eivät ole ratkaistavissa ilman arvauksia

Opinto-ohjelma: TKT-kandi

Samassa järjestyksessä kuin täällä https://algolabra-hy.github.io/dokumentaatio:
- Käytän Pythonia
- vertaisarvioinnit: osaan
  - C++:aa vähän (olen tehnyt 13 tehtävää _algoritmit ongelmanratkaisussa_ -kurssilla),
  - <b>JavaScriptiä</b> hyvin, ja
  - Haskellia melko vähän (ei kiitos Haskellille - tein _Functional Programming_ -kurssin arvosanalla 3/5)
  - kävin Data Analysis with Python -kurssin, 4/5, ja _Building AI_ -kurssit, MUTTA en ole käynyt _Lineaarialgebra ja matriisilaskenta_ -kursseja vielä
- [ ] to-do: mitä algoritmeja käytän: coupled subsets CSP (Becerran kandityö)
- teen miinaharavabotin
- [ ] to-do: syötteet
- [ ] to-do: O-aikavaativuusanalyysit
- [ ] to-do: vertailu tunnettuihin miinaharava-algoritmeihin
- [ ] to-do: viitteet: Becerra, David J. 2015. Algorithmic Approaches to Playing Minesweeper. Bachelor's thesis,
Harvard College (permalink: http://nrs.harvard.edu/urn-3:HUL.InstRepos:14398552).
