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

Päädyin tekemään ratkaisijan `CSP_solver` pitkälti uudestaan niin, että

<ol>
  <li>
    Jaetaan kaikki yhtälöt (eli kaikki joukon <code>self.unique_equations</code> jäsenet) joukkoihin yhteisten muuttujien perusteella; siis esim. a+b=1, b+c+d=1, ja c+e+f=2 olisivat samassa joukossa, koska ne kaikki voidaan yhteisten muuttujien kautta linkittää suoraan tai toistensa kautta toisiinsa, kun taas yhtälö g+h=1 jäisi näistä kolmesta (edellisestä joukosta) erilleen, sillä se ei jaa muuttujia edellisen joukon kanssa. Tämä tehdään, koska se mahdollistaa saman joukon yhtälöille tehokkaamman keskinäisen mahdottomia ratkaisuja pois karsivan alt-ratkaisujen linkittämisen toisiinsa seuraavassa vaiheessa, ja mahdollistaa pienempien ratkaisupuiden rakentamisen sitä seuraavassa vaiheessa. On hyvin suoraviivaista ja laskennallisesti kevyttä rakentaa erilliset joukot yhtälöistä, joten tämä vähentää tarpeetonta laskentaa edellämainituissa seuraavassa kahdessa vaiheessa.
  </li>
  <li> Kunkin edellisessä vaiheessa rakennetun joukon kullekin yksittäiselle yhtälölle haetaan kaikki mahdolliset ratkaisukombinaatiot (esim. $a+b=1 \Leftrightarrow (a,b) \in \{(0,1),(1,0)\}$ koska jokainen muuttuja on 0 tai 1). Kukin yksittäinen yhtälö on peräisin yhdestä miinaharavamapin avatusta numeroruudusta, joka kertoo, montako miinaa avatun ruudun ympäriltä yhteensä löytyy (tekninen yksityiskohta: miinus jo laitetut liput, joita ei myöskään ole siis muuttujina). Kukin yksittäinen muuttuja on miinojen lukumäärä kyseisessä ruudussa (eli jokainen muuttuja on 0 tai 1). Tämä alt-ratkaisujen rakentaminen per yhtälö tehdään <code>itertools.combinations()</code>:illä, eli valitaan ykköset kombinaatioita käyttämällä (n-yli-k:n).
  Näiden alt-ratkaisujen lukumäärä per yhtälö on ${n \choose k}$ missä $n$ on avattua numeroruutua ympäröivien avaamattomien ja liputtamattomien ruutujen lukumäärä ja $k$ on tämän avatun numeroruudun numero miinus jo laitetut liput; esim. jos on avattu ruutu 2, jonka ympärillä on siis 2 miinaa, eikä ympärillä ole lippuja, niin jos tämän kakkosen ympärillä on vaikka 4 avaamatonta ruutua jäljellä, niin mahdollisia ratkaisukombinaatioita on tällöin ${4 \choose 2}=6$ kappaletta.
  </li>
  <li>
    Nyt on siis saatu kaikki mahdolliset ratkaisut jokaiselle alkuperäiselle miinaharavamapin yhtälölle (kussakin erillisessä joukossa). Kutsun kutakin vaihtoehtoista ratkaisua per yhtälö 'alt':iksi tai alt-ratkaisuksi (alt = alternative = vaihtoehtoinen; kukin rinnakkainen alt-ratkaisu per yhtälö on muut saman yhtälön alt-ratkaisut poissulkeva). Kunkin yhtälön alttien joukkoa kutsutaan nyt ryhmäksi. Seuraavaksi valitaan täysin umpimähkään aloitusryhmä (eli MINKÄ TAHANSA mapin yhtälön kaikki mahdolliset alt-ratkaisut), ja tämän aloitusryhmän kaikille alteille valitaan (samasta 1. kohdassa rakennetusta joukosta kuin mistä aloitusryhmäkin valittiin) yhteinen toinen ryhmä umpimähkään, kutsuttakoon sitä kakkosryhmäksi. Kukin aloitusryhmän alt paritetaan yhden, mielivaltaisen kakkosryhmän jokaisen altin kanssa, JOS nämä altit ovat yhteensopivia eli jos niissä ei ole suoraan keskenään ristiriitaisia arvoja (eli jos esim. aloitusryhmän altissa x ei ole a=1, kun taas kakkosryhmän altissa y a=0; ei haluta ristiriitoja). Tässä saadaan siis jokaisessa ryhmäparissa karsittua pois ne keskinäiset altit, jotka eivät ole keskenään sopivia: esim. a=1, b=0 ja b=0, c=1 ovat yhteensopiva alt-pari yhtälöistä a+b=1 ja b+c=1, kun taas a=1, b=0 ja b=1, c=0 eivät ole yhteensopiva alt-pari kahden eri ryhmän (yhtälön) välillä.
  </li>
  <li> Tätä parittamista jatketaan (kussakin 1. kohdassa rakennetussa joukossa sisäisesti) toisesta ryhmästä kolmanteen ryhmään (jälleen kerran kaikki yhteensopivat altit kaikkien yhteensopivien kanssa), sitten kolmannesta neljänteen, jne. Lopulta on käytössä ketju ryhmiä, joka alkaa aloitusryhmästä ja päättyy johonkin lopetusryhmään; kyseessä on joukko puita, joiden jokainen vaihtoehtoinen juuri on eräs aloitusryhmän yhtälön alt-ratkaisu (esim. ryhmän, jonka yhtälö on a+b=1, kaksi juurta olisivat a=1, b=0 ja toinen a=0, b=1, PAITSI jos jompikumpi näistä juurista olisi yhteensopiva kaikkien kakkosryhmän alttien kanssa, missä tapauksessa olisi vain yksi juuri, ja itseasiassa tämä tarkoittaa silloin sitä, että ainoa mahdollinen tämän ryhmän ratkaisu on ainoa ryhmän jäljelle jäävä alt).</li>
  <li> Parittamisten jälkeen on niin monta vaihtoehtoista ratkaisupuuta, kuin montako alttia oli aloitusryhmässä. Jos esim. aloitusryhmä oli a+b=1, niin on 2 ratkaisupuuta. Kunkin puun juurena on siis aloitusryhmän alt, jonka lapsina ovat kaikki siihen yhteensopivat 2. ryhmän altit, jonka lapsina ovat kaikki 3. ryhmän 2. ryhmään yhteensopivat altit, jne. Nämä puut on toteutettu Pythonin <code>map</code>:illa. </li>
  <li> Kutakin puuta käydään läpi niin, että pidetään kustakin kussakin puussa syntyvästä ratkaisusta kirjaa (siis mahdollisesti monta mahdollista ratkaisua per kukin vaihtoehtoinen puu). Heti jos huomataan, että esim. aloitusryhmän altissa on a=1, mutta esim. jo 3. ryhmässä onkin a=0 eli ristiriita, niin koko haara hylätään eikä sitä enää käsitellä pitemmälle. </li>
  <li> Lopulta on saatu kaikkiaan joku joukko mahdollisia ratkaisuja, jotka toteuttavat samaan aikaan kaikki alkuperäiset yhtälöt, eli joissa yksikään alt (yksi per ryhmä per ratkaisu) ei ole ristiriidassa keskenään. Jos näitä on vaikka 5 mahdollista, käydään kustakin 5 ratkaisuehdotuksesta läpi jokainen muuttuja. Jos jokin muuttuja, esim. a, on aina 1 kaikissa 5 vaihtoehtoisessa mahdollisessa ratkaisussa, on sen oltava 5 (koska mitään muuta mahdollista ratkaisua ei ole, joka kykenee toteuttamaan täsmälleen yhden vaihtoehtoisen altin kustakin ryhmästä). Tämä perustuu tietysti siihen, että on käyty läpi kaikki mahdolliset ratkaisut, ja että tiedetään että kaikki yhtälöt toteuttava ratkaisu todellakin on olemassa, koska miinat todellakin on jollakin lailla sijoitettu mappiin niin, ettei yksikään näkyvä numeroruutu valehtele. </li>
</ol>


## to-do: syötteet
## to-do: O-aikavaativuusanalyysit
## to-do: vertailu tunnettuihin miinaharava-algoritmeihin
## to-do: viitteet: 

Becerra, David J. 2015. Algorithmic Approaches to Playing Minesweeper. Bachelor's thesis,
Harvard College (permalink: http://nrs.harvard.edu/urn-3:HUL.InstRepos:14398552).
