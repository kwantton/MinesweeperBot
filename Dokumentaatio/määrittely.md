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

## Mitä algoritmeja käytän
coupled subsets CSP (Becerran kandityö)
Päädyin tekemään ratkaisijan CSP_solver pitkälti uudestaan niin, että

Ensin haetaan kaikki mahdolliset ratkaisukombinaatiot kullekin yksittäiselle yhtälölle (esim. a+b=1; a=1 ja b=0 tai a=0 ja b=1). Kukin yhtälö on miinaharavamapin avattu numeroruutu, joka kertoo, montako miinaa ympäriltä yhteensä löytyy. Kukin muuttuja on miinojen lukumäärä kyseisessä ruudussa (eli 0 tai 1 jokaiselle muuttujalle). Tämä tehdään `itertools.combinations()`:illä. Näiden lukumäärä on ( n k ) missä n on avattua numeroruutua ympäröivien avaamattomien ruutujen lukumäärä ja k on tämän avatun numeroruudun numero; esim. jos on avattu ruutu 2, jonka ympärillä on siis 2 miinaa, niin jos tämän kakkosen ympärillä on vaikka 4 avaamatonta ruutua jäljellä, niin mahdollisia ratkaisukombinaatioita on tällöin ( 4 2 ) = 6 kappaletta.
    Nyt on siis saatu kaikki mahdolliset ratkaisut jokaiselle alkuperäiselle miinaharavamapin yhtälölle. Kutsun kutakin vaihtoehtoista ratkaisua per yhtälö 'alt':iksi (alt = alternative = vaihtoehtoinen). Kunkin yhtälön alttien joukkoa kutsutaan nyt ryhmäksi. Seuraavaksi valitaan mielivaltainen aloitusryhmä (eli mapin yhtälön mahdolliset alt-ratkaisut), ja tämän aloitusryhmän kukin alt paritetaan yhden, mielivaltaisen toisen ryhmän jokaisen altin kanssa, JOS ne ovat yhteensopivia eli jos niissä ei ole eri arvoja (toisessa 1, toisessa 0) samalle muuttujalle. Tässä saadaan siis parissa karsittua pois ne, jotka eivät ole keskenään sopivia: esim. a=1, b=0 ja b=0, c=1 ovat yhteensopiva alt-pari yhtälöistä a+b=1 ja b+c=1, kun taas a=1, b=0 ja b=1, c=0 eivät ole yhteensopiva pari.
    Tätä parittamista jatketaan toisesta ryhmästä kolmanteen ryhmään (jälleen kerran kaikki yhteensopivat altit kaikkien yhteensopivien kanssa), sitten kolmannesta neljänteen, jne.
    Parittamisten jälkeen on niin monta vaihtoehtoista ratkaisupuuta, kuin montako alttia oli aloitusryhmässä. Jos esim. aloitusryhmä oli a+b=1, niin on 2 ratkaisupuuta. Sen juurena on aloitusryhmän alt, jonka lapsina ovat kaikki siihen yhteensopivat 2. ryhmän altit, jonka lapsina ovat kaikki 3. ryhmän 2. ryhmään yhteensopivat altit, jne.
    Tätä puuta käydään läpi niin, että pidetään syntyvästä ratkaisusta kirjaa. Heti jos huomataan, että esim. aloitusryhmän altissa on a=1, mutta esim. jo 3. ryhmässä onkin a=0, niin koko haara hylätään eikä sitä enää käsitellä.
    lopulta on joku rypäs mahdollisia ratkaisuja, jotka toteuttavat samaan aikaan kaikki yhtälöt. Jos näitä on vaikka 5 mahdollista, käydään kustakin 5 ratkaisuehdotuksesta läpi jokainen muuttuja. Jos muuttuja, esim. a, on aina 1 kaikissa 5 vaihtoehtoisessa mahdollisessa ratkaisussa, on sen oltava 5 (koska mitään muuta mahdollista ratkaisua ei ole, joka kykenee toteuttamaan täsmälleen yhden vaihtoehtoisen altin kustakin ryhmästä)

## to-do: syötteet
## to-do: O-aikavaativuusanalyysit
## to-do: vertailu tunnettuihin miinaharava-algoritmeihin
## to-do: viitteet: 

Becerra, David J. 2015. Algorithmic Approaches to Playing Minesweeper. Bachelor's thesis,
Harvard College (permalink: http://nrs.harvard.edu/urn-3:HUL.InstRepos:14398552).
