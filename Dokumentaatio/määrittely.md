# Aihe: miinaharavabotti, joka pystyy ratkaisemaan kaikki mahdolliset logiikalla ratkaistavissa olevat miinaharavan tilanteet 

- Tiedostossa `botGame.py` voi generoida kenttiä (eli "mappeja" eli yksittäisiä pelejä, joissa miinajakaumat ovat halutun laisia): mapissa rivejä on $r$, sarakkeita $s$, miinoja $m < rs-9^{(huom.1)}$ (esim. expertissä on 16 riviä, 30 saraketta ja 99 miinaa), ja mapit esitetään Pythonissa listana listoja (lista rivejä, joista jokaisen alkion arvo on 0 jos ruudussa ei ole miinaa, ja 1, jos on miina); arvotaan $m$ miinaa koordinaateilla $(x,y)$ jotka ovat mitä tahansa muuta kuin ruutu, johon aluksi klikattiin (josta aloitettiin pelaaminen). Kiinteitä (muuttumattomia) testejä on tehty `CSP_solver`-luokan testaamista varten **tests_for_CSP_solver.py**-tiedostossa, ja vanhempaa `CSP_solver_old`-luokkaa varten **tests_for_CSP_solver_old.py**-tiedostossa.
- ratkaisulogiikan testaus: **constraint_problem_solver_for_testing.py**. Lisää validiteettitestauksesta tiedostossa [../Testing/Logic_validity_testing](../Testing/Logic_validity_testing/Testing_manual.pdf)
- Tiedostossa `CSP_solver.py` voidaan luoda luokan `CSP_solver` olio, jolle syötetään yhtälöitä, joissa jokaisen muuttujan tulee olla 0 tai 1. Tässä mielessä kyseessä on pikemminkin Boolen totuustaulukoija kuin "CSP-solver", eli kyseessä on ainoastaan sellaisten yhtälöiden ratkaisija, joissa jokainen muuttuja on edellämainitusti 0 tai 1. Tässä kontekstissa 0 tarkoittaa, että kyseisessä muuttujassa eli miinaharavamapin ruudussa ei ole miinaa, ja 1 tarkoittaa, että kyseisessä ruudussa on miina. Tätä luokkaa käytetään `botGame.py`:ssä ja se integroidaan `Minesweeper`-olioon niin, että pelin aloittaessa ajamalla `botGame.py`:n main-osion koodin voidaan pelata botilla painamalla b-näppäintä. Botti osaa ratkaista kaikki tilanteet paitsi ne, joissa tulisi ottaa huomioon koko mapissa jäljelläolevien miinojen lukumäärä eli 'minecount'.

Opinto-ohjelma: TKT-kandi

Samassa järjestyksessä kuin täällä https://algolabra-hy.github.io/dokumentaatio:
- Käytän Pythonia
- vertaisarvioinnit: osaan
  - C++:aa vähän (olen tehnyt 13 tehtävää _algoritmit ongelmanratkaisussa_ -kurssilla),
  - <b>JavaScriptiä</b> hyvin, ja
  - Haskellia melko vähän (ei kiitos Haskellille - tein _Functional Programming_ -kurssin arvosanalla 3/5)
  - kävin Data Analysis with Python -kurssin, 4/5, ja _Building AI_ -kurssit, MUTTA en ole käynyt _Lineaarialgebra ja matriisilaskenta_ -kursseja vielä

## Mitä algoritmeja käytän
Ratkaisu (arvaukset mukaanlukien) on kahdeksanvaiheinen (19.10.2024):
1. `simple_solver()` (in 'botGame.py') solves the simplest of cases, solving all cases of number-cell-number-equals-to-surrounding-unclicked-cells and all cases of number-cell-number-equals-to-surrounding-flags before ever moving on to call `CSP_solver`, thus limiting work done later in `CSP_solver` (which practically always is needed many times per game in case of Expert maps)
2. If 1. didn't produce answers, use `CSP_solver_old` which is fast, but cannot solve all cases. This utilizes the class that I was originally developing for this course.
3. If 2. didn't produce answers, move on to `CSP_solver`: grouping equations to separated equation sets where sets do not share variables with other sets. This significantly limits the size of the problems solved by the machinery below.
4. finding solution combinations per one equation (equation is, for example, a+b=1, where a and b are cells (cell=ruutu)). So at this point, each equation set has all possible answers per every equation
5. for each equation set, chain link equations. The order of the chain: the equations in each separated equation set are first sorted, ensuring that in almost all cases, linking between each equation pair is done so that some alternative answers per each equation can be discarded due to incompatibility with the equation before and/or after (a chain has 2 ends, that's why 'and/or' was written).
6. after chain linking, in the same order as in the previous step, traverse through all possible chains, which always start from the same starting equation, called the 'starting group' per each equation set. There's bookkeeping for variables so conflicts are found, and if conflicts are found, backtracking happens, discarding the whole branch so far. Essentially, there are as many 'alt tree roots' per equation group as there are alternative answers to the first equation (i.e. the 'starting group'). Thanks to this and the previous step, all the impossible answers are quite effieciently backtracked, and thanks to keeping equation sets separate when possible, the size of the trees is severely limited in most cases.
7. for each equation set's possible whole answers received in the previous step, check if one or more variables were always 1 or always 0 in all possible alternative answers. If such variables were found, they are absolute answers for that variable (i.e. other answers are impossible). If not, the numbers of 1 vs 0 for each variable have now been recorded, and a guess can be taken, UNLESS the next step evaluates to true
8. check for need for minecount: if the sum of max numbers of mines in all the combined (separated) fronts is less than the remaining minecount, this always evaluates to false. If the max sum equals to remaining minecount, then all unclicked unseen cells are 0 (no mine) and only the max mine count alt solutions can be viable, and if only the min sum equals to remaining minecount, then all unclicked unseen cells are 0 and only the min mine count solutions can be viable, and if something between max and min, another round of discarding minecount-invalid alt solutions must be done. There is no simpler way to describe this, I'm sorry. The alternative would be to add another equation to the mix, the one that has ALL remaining variables (all unclicked cells) and the total minecount, but you probably see the problem with this: it's far more inefficient, and with large variable numbers, the number of combinations from this can go to over $10^100$ possible answers in worst cases - not doable by backtracking and/or brute forcing alone! My solution is very good regarding this.
9. if the previous step didn't produce answers, guess using the minecount situation -derived minecounts. Like the previous possibility for guessing (if minecount was not even needed), this chooses the cell with lowest chance of being a mine, comparing front cells to unseen unclicked cells. If unseen unclicked cells have the lowest chance of being a mine, a corner is opened (4 corners exist per map) if they are still available, and if all corners have already been used, then a front cell's neighbouring unclicked unseen cells is guessed.

Toteutuksessani halusin väsätä kaiken 'itse'. Saatan käyttää coupled subsets CSP:tä (CSCSP:tä, kuten Becerra 2015), mutta en ole lukenut työtä kunnolla, ja esim. yhtälöiden ketjuttamisen keksin itse (se siis nimenomaan on ketju eikä verkko, ja vaati ymmärryksen siitä, että kaikkien settien kaikkien yhtälöiden globaalit ratkaisut koostuvat niistä alteista, jotka myös joka ikinen yhtälöpari jakaa keskenään, eli ketjuttamisjärjestyksellä ei ole väliä, kaikki globaalit ratkaisut löydetään järjestyksestä riippumatta). 

Ainoa lähteeni on Becerra, 2015. Becerran työssä ei tietääkseni puhuta minecount-tilanteista, mutta päästään lähes identtisiin tuloksiin kuin mihin itse pääsen (ks. "vertailu tunnettuihin miinaharava-algoritmeihin"-otsikko).

Päädyin kolmannella viikolla tekemään ratkaisijan `CSP_solver` pitkälti uudestaan niin, että (voi olla osittain vanhentunutta)

<ol>
  <li>
    Jaetaan kaikki yhtälöt (eli kaikki joukon <code>self.unique_equations</code> jäsenet) joukkoihin yhteisten muuttujien perusteella; siis esim. $a+b=1$, $b+c+d=1$, ja $c+e+f=2$ olisivat samassa joukossa, koska ne kaikki voidaan yhteisten muuttujien kautta linkittää suoraan tai toistensa kautta toisiinsa, kun taas yhtälö $g+h=1$ jäisi näistä kolmesta (edellisestä joukosta) erilleen, sillä se ei jaa muuttujia edellisen joukon kanssa. Tämä tehdään, koska se mahdollistaa saman joukon yhtälöille tehokkaamman keskinäisen mahdottomia ratkaisuja pois karsivan alt-ratkaisujen linkittämisen toisiinsa seuraavassa vaiheessa, ja mahdollistaa pienempien ratkaisupuiden rakentamisen sitä seuraavassa vaiheessa. On hyvin suoraviivaista ja laskennallisesti kevyttä rakentaa erilliset joukot yhtälöistä, joten tämä vähentää tarpeetonta laskentaa edellämainituissa seuraavassa kahdessa vaiheessa.
  </li>
  <li> Kunkin edellisessä vaiheessa rakennetun joukon kullekin yksittäiselle yhtälölle haetaan kaikki mahdolliset ratkaisukombinaatiot (esim. $a+b=1 \Leftrightarrow (a,b) \in \{(0,1),(1,0)\}$ koska jokainen muuttuja on 0 tai 1). Kukin yksittäinen yhtälö on peräisin yhdestä miinaharavamapin avatusta numeroruudusta, joka kertoo, montako miinaa avatun ruudun ympäriltä yhteensä löytyy (tekninen yksityiskohta: miinus jo laitetut liput, joita ei myöskään ole siis muuttujina). Kukin yksittäinen muuttuja on miinojen lukumäärä kyseisessä ruudussa (eli jokainen muuttuja on 0 tai 1). Tämä alt-ratkaisujen rakentaminen per yhtälö tehdään <code>itertools.combinations()</code>:illä, eli valitaan ykköset kombinaatioita käyttämällä (n-yli-k:n).

Näiden alt-ratkaisujen lukumäärä per yhtälö on ${n \choose k}$ missä $n$ on avattua numeroruutua ympäröivien avaamattomien ja liputtamattomien ruutujen lukumäärä ja $k$ on tämän avatun numeroruudun numero miinus jo laitetut liput; esim. jos on avattu ruutu 2, jonka ympärillä on siis 2 miinaa, eikä ympärillä ole lippuja, niin jos tämän kakkosen ympärillä on vaikka 4 avaamatonta ruutua jäljellä, niin mahdollisia ratkaisukombinaatioita on tällöin ${4 \choose 2}=6$ kappaletta.
  
Koska yhtälöt ovat tyypillisesti $a+b=1$ tai $b+c+d=2$ tai esim. $a+b+c+d+e+f=2$, korkeintaan 8 muuttujaa, ratkaisumahdollisuuksien määrä per yhtälö on yleensä 2...10, pahimmillaan esim. ${8 \choose 4}=70$ tilanteessa, jossa arvauksen seurauksena frontin naapurin naapuriksi paljastui numeroruutu 4, jonka ympäriltä yhtäkään ruutua ei ole vielä avattu. Joka tapauksessa, näiden määrää rajoitetaan jatkossa vahvasti, jotta ei päädytä tilanteeseen, jossa esim. on 40 näkyvää numeroruutua (eli 40 yhtälöä), joiden mahdollisten ratkaisujen lukumäärä on vaikka $2\cdot10\cdot56\cdot6\cdot...$ joka voisi olla vaikka karkeasti $3^40=1.2\cdot10^19$ jossain realistisessa esimerkkitapauksessa, jos karsimista ei tehtäisi.

(Kahdeksan muuttujan yhtälö voi tulla vastaan, jos arvataan kuvaannollisesti keskelle ei-mitään (eikä reunan viereen, koska reunan vierusruuduilla on vain 5 naapuria, kun taas nurkkaruuduilla on 3 naapuria), ja jos tällä arvatulla ruudulla ei ole liputettuja naapureita. Tällainen arvaus tehdään, jos ei-näkyvien ruutujen suurin mahdollinen todennäköisyys olla miina on pienempi kuin näkyvien ruutujen pienin mahdollinen todennäköisyys olla miina, ja kyseessä on frontin näkemän naapurin naapuri 'keskellä ei mitään' mutta frontin naapurin vieressä).

  </li>
  <li>
    Nyt on siis saatu kaikki mahdolliset ratkaisut jokaiselle alkuperäiselle miinaharavamapin yhtälölle (kussakin erillisessä joukossa). Kutsun kutakin vaihtoehtoista ratkaisua per yhtälö 'alt':iksi tai alt-ratkaisuksi (alt = alternative = vaihtoehtoinen; kukin rinnakkainen alt-ratkaisu per yhtälö on muut saman yhtälön alt-ratkaisut poissulkeva). Kunkin yhtälön alttien joukkoa kutsutaan nyt ryhmäksi. Seuraavaksi valitaan täysin umpimähkään aloitusryhmä (eli kyseisen mapin MINKÄ TAHANSA yhtälön kaikki mahdolliset alt-ratkaisut), ja tämän aloitusryhmän kaikille alteille valitaan (samasta 1. kohdassa rakennetusta joukosta kuin mistä aloitusryhmäkin valittiin) yhteinen toinen ryhmä umpimähkään, kutsuttakoon sitä kakkosryhmäksi. Kukin aloitusryhmän alt paritetaan yhden, mielivaltaisen kakkosryhmän jokaisen altin kanssa, JOS nämä altit ovat yhteensopivia eli jos niissä ei ole suoraan keskenään ristiriitaisia arvoja (eli jos esim. aloitusryhmän altissa $x$ ei ole $a=1$, kun taas kakkosryhmän altissa $y$ on $a=0$; ei haluta ristiriitoja). Tässä saadaan siis jokaisessa ryhmäparissa karsittua pois ne keskinäiset altit, jotka eivät ole keskenään sopivia: esim. $a=1, b=0$ ja $b=0, c=1$ ovat yhteensopiva alt-pari yhtälöistä $a+b=1,\ b+c=1$, kun taas $a=1,\ b=0$ ja $b=1,\ c=0$ eivät ole yhteensopiva alt-pari kahden eri ryhmän (yhtälön) välillä.
  </li>
  <li> Tätä parittamista jatketaan (kussakin 1. kohdassa rakennetussa joukossa sisäisesti) toisesta ryhmästä kolmanteen ryhmään (jälleen kerran kaikki yhteensopivat altit kaikkien yhteensopivien kanssa), sitten kolmannesta neljänteen, jne. Lopulta on käytössä ketju ryhmiä, joka alkaa aloitusryhmästä ja päättyy johonkin lopetusryhmään; kyseessä on joukko puita, joiden jokainen vaihtoehtoinen juuri on eräs aloitusryhmän yhtälön alt-ratkaisu (esim. ryhmän, jonka yhtälö on $a+b=1$, kaksi juurta olisivat $a=1, b=0$ ja toinen $a=0, b=1$, PAITSI jos jompikumpi näistä juurista olisi yhteensopiva kaikkien kakkosryhmän alttien kanssa, missä tapauksessa olisi vain yksi juuri, ja itseasiassa tämä tarkoittaa silloin sitä, että ainoa mahdollinen tämän ryhmän ratkaisu on ainoa ryhmän jäljelle jäävä alt).</li>
  <li> Parittamisten jälkeen on niin monta vaihtoehtoista ratkaisupuuta, kuin montako alttia oli aloitusryhmässä. Jos esim. aloitusryhmä oli $a+b=1$, niin on 2 ratkaisupuuta. Kunkin puun juurena on siis aloitusryhmän alt, jonka lapsina ovat kaikki siihen yhteensopivat 2. ryhmän altit, jonka lapsina ovat kaikki 3. ryhmän 2. ryhmään yhteensopivat altit, jne. Nämä puut on toteutettu Pythonin <code>map</code>:illa. </li>
  <li> Kutakin puuta käydään läpi niin, että pidetään kustakin kussakin puussa syntyvästä ratkaisusta kirjaa (siis mahdollisesti monta mahdollista ratkaisua per kukin vaihtoehtoinen puu). Heti jos huomataan, että esim. aloitusryhmän altissa on $a=1$, mutta esim. jo 3. ryhmässä onkin $a=0$ eli ristiriita, niin koko haara hylätään eikä sitä enää käsitellä pitemmälle. </li>
  <li> Lopulta on saatu kaikkiaan joku joukko mahdollisia ratkaisuja, jotka toteuttavat samaan aikaan kaikki alkuperäiset yhtälöt, eli joissa yksikään alt (yksi per ryhmä per ratkaisu) ei ole ristiriidassa keskenään. Jos näitä on vaikka 5 mahdollista, käydään kustakin 5 ratkaisuehdotuksesta läpi jokainen muuttuja. Jos jokin muuttuja, esim. $a$, on aina 1 kaikissa 5 vaihtoehtoisessa mahdollisessa ratkaisussa, on sen oltava 1 (koska mitään muuta mahdollista ratkaisua ei ole, joka kykenee toteuttamaan täsmälleen yhden vaihtoehtoisen altin kustakin ryhmästä). Tämä perustuu tietysti siihen, että on käyty läpi kaikki mahdolliset ratkaisut, ja että tiedetään että kaikki yhtälöt toteuttava ratkaisu todellakin on olemassa, koska miinat todellakin on jollakin lailla sijoitettu mappiin niin, ettei yksikään näkyvä numeroruutu valehtele. </li>
</ol>


## Syötteet
### (1) Luokka `CSP_solver`, CSP_solver.py

Luokka `CSP_solver`: luokkaa voi käyttää näin:

```python
# Test name = 'test 1a: letters. a0, b1, c1, d0, e1 expected'

eq1 = [0, 1, ('a', 'b'), 1]        # [equation origin x-coordinate, equation origin y-coordinate, (var1, var2), sum of the variables (var1 + var2 = 0, 1 or 2)]. The eq origin coordinates are needed in the input, but do not affect the results in any way
eq2 = [1, 1, ('a', 'c', 'd'), 1]
eq3 = [2, 1, ('c', 'd', 'e'), 2]
eq4 = [3, 1, ('d', 'e'), 1]

csp = CSP_solver()
csp.handle_incoming_equations([eq1, eq2, eq3, eq4])
csp.absolut_brut()
for solved_variable in csp.solved_variables:
  print(solved_variable)
'''prints the following:
('a', 0)
('b', 1)
('c', 1)
('d', 0)
('e', 1)
'''
```
Ylläolevassa esimerkissä (`CSP_solver.py`:stä `if __name__=='__main__'`-osiosta ensimmäinen testitapaus vähän muokattuna) luodaan luokan `CSP_solver` olio. Luokan konstruktori ei syö mitään parametreja, vaan jokaisen olion spesifioivat ne yhtälöt, joita sille syötetään. Ylläolevassa esimerkissä syötetään yhtälöt `eq1, eq2, eq3` ja `eq4`.

### (2) Luokka `Minesweeper`, botGame.py

Itsensä hyvin selittää seuraava:

```python
if __name__ == '__main__':
    dense_beg = 9,9,70
    beginner = 9,9,10
    intermediate = 16,16,40
    expert = 30,16,99

    ''' ↓↓↓ STARTS A NEW MINESWEEPER with the ability to play the bot by pressing b ↓↓↓ (instructions in the game) '''
    # Minesweeper(beginner[0], beginner[1], beginner[2], csp_on=False) # IF YOU WANT ONLY simple_solver(), which WORKS at the moment, then use this. It can only solve simple maps where during each turn, it flags all the neighbours if the number of neighbours equals to its label, AND can chord if label = number of surrounding mines.
    Minesweeper(expert[0], expert[1], expert[2], csp_on=True) # this one utilizes also csp-solver, which is partially broken at the moment, causing mislabeling of things
    #           width       height      mines
```

## O-aikavaativuusanalyysit
Miinaharava on co-NP-täydellinen ongelma, eli päätösongelman komplementti on NP-täydellinen. Miinaharavan $CONSISTENCY$ (jonka tulos on aina 'tosi') voidaan palauttaa $SAT$:iksi, ja toinen NP-ongelma eli se, voidaanko jotain muuttujia ratkaista tuloksella 'miina' tai 'ei miinaa' on nimeltään $INFERENCE$. Erittäin huomionarvoista on se, että edes näissä NP-ongelmissa ei ollenkaan oteta huomioon 'arvauksia' (sanon 'arvauksia' lainausmerkeissä, koska kyse on erittäin monimutkaisesta todennäköisyyslaskennasta, jos halutaan parhaisiin mahdollisiin tuloksiin: esim. nimimerkki 'Shuffler' Minesweeper Community-Discordissa on tehnyt solverin, joka voittaa hieman yli 41% (!) klassisista (1. ruutu 0-8) Expert-peleistä, ja joka esimerkkinä muun muassa loppupelien arvauksien tapauksessa käy kaikki mahdolliset loppupelit läpi brute-forcella, ja laskee näistä jokaisesta koko loppupelin voiton todennäköisyydet)

Käytössäni on monta jippoa, joilla nopeutan sekä ratkaisemista että todennäköisyyslaskentaa. Nämä on lueteltu **README.md**-tiedostossa otsikon "ideas" alla (kaikki missä lukee "implemented" on myös toteutettu, kuten arvata saattaa).

Pahimmissa tapauksissa muuttujien lukumäärän suhteen aikavaativuuteni on eksponentiaalinen, koska jos backtracking ei karsi ratkaisuja pois, niin jos kullekin yhtälölle olisi vaikka keskimäärin 3 mahdollista ratkaisua, silloin kokonaisia ratkaisuja on $3\cdot3\cdot3\cdot....$ sen mukaan, kuinka monta yhtälöä ryppäässä on.

Tätä tilannetta _yleensä_ parantaa merkittävästi se, että hajotan yhtälöt erillisiin joukkoihin yhtälöitä niin, että yhdelläkään erillisellä joukolla ei ole yhteisiä muuttujia yhdenkään muun joukon minkään yhtälön kanssa. Tässä voi kuitenkin käydä niin, että koko 'rintama' onkin yhtenäinen, jolloin tätä hajotusta ei voida tehdä. Joskus myös miinojen laskennalle ('minecount') voi olla tarvetta, ja tästä aiheutuu toinen yhtä suuri urakka kuin varsinainen aiempi (ilman miinojen lukumäärän huomioon ottamista) ratkaisuyritys oli.

## vertailu tunnettuihin miinaharava-algoritmeihin

Alkuperäinen lähteeni on Becerra, 2015. Becerran työssä todennäköisesti käytetään 'classical minesweeperiä' eli sitä, jossa 1. ruutu on 0-8 (eikä modern, jossa 1. klikkaus on 0). 
Becerran tulokset ovat: Expert, 32.90% voitettu, 4.73 arvausta/peli; Int, 75.94% voitettu, 2.39 arvausta/peli; Beg, 91.25% voitettu, 1.70 arvausta/peli.
Omat tulokseni ovat: Expert, 33.41% voitettu, 3.07 arvausta/peli; Int, 75.94% voitettu, 1.28 arvausta/peli; Beg, 91.28% voitettu, 0.68 arvausta/peli.
Syy voi olla seuraava: en yhdistä eriytettyjen rintamien ('disjoint subsets') todennäköisyyksiä todennäköisyyslaskentaa varten, vaan kohtelen eriytettyjä rintamia kuten ne eivät vaikuttaisi toisiinsa (tosiasiassa niiden miinamäärät vaikuttavat toisiensa miinamäärien todennäköisyyksiin), ja/tai voi olla, että Becerra ei käytä minecountia hyväksi (? ei mainita hänen kandityössään). Tämä on kuitenkin spekulaatiota. On kuitenkin perin hämmentävää, miten näin erilaisilla arvausten määrillä voi päästä lähes identtisiin lopputuloksiin.

Erinomainen lähde tälle asialle lienee käyttäjänimi 'Shuffler' Minesweeper Community -Discord-kanavalla (https://github.com/DavidNHill/JSMinesweeper#readme). Hän on tehnyt ratkaisijan+arvaajan, joka voittaa hieman yli 41% (mikä on ällistyttävän hyvä) klassisista (1. ruutu 0-8) Expert-kentistä, ja on tietääkseni vastuussa siitä, että minesweeper.online-sivuston 'win rate' -prosentit ovat sitä mitä ovat (esim. kentälle 30x16|99, eli expert, win rate on 40.1%, joka on täydellinen logiikka + täydelliset arvaukset MIINUS jonkin suuruinen inhimillisen virheen vara, joka on sitä isompi, mitä isompi ja vaikeampi kenttä on kyseessä; tämä on tapa, jolla nämä lukuarvot sivustolla on saatu, lähteenäni kyseisen sivuston chat). Tämä on parempi kuin paras löytämäni tieteellisen artikkelin saavuttama ratkaisuprosentti, joka on 39.62% (Tu, Li, Chen et.al. 2017, AAAI-17 Workshop on What's Next for AI in Games?).

Niin omassa työssäni kuin ei Becerran työssäkään tarkastella, mitä tapahtuu arvauksen jälkeen; siis arvaukset ovat 'naiiveja' sen suhteen, mitä arvauksen jälkeen tapahtuu - vaikka kussakin pelitilanteessa löydetäänkin kyseisellä hetkellä turvallisin arvaus, tämä ei takaa sitä, että tämä 'turvallisin' arvaus olisi oikeasti paras koko loppumapin ratkaisemisen kannalta. On esimerkiksi tilanteita, joissa arvaus, vaikka ei osuisikaan miinaan, ei kerro mitään loppujen miinojen sijainneista, eli voi tosiasiassa olla kaikkein huonoin arvaus, vaikka olisikin akuutisti 'turvallisin'. Toisin on nimimerkin 'Shuffler' ratkaisijan tapauksessa, joka saa 41% klassisista Expert-kentistä voitettua.

## to-do: viitteet: 

Becerra, David J. 2015. Algorithmic Approaches to Playing Minesweeper. Bachelor's thesis,
Harvard College (permalink: http://nrs.harvard.edu/urn-3:HUL.InstRepos:14398552).

## huomioita
(1) Kirjoitin, että $r$ rivillä ja $s$ sarakkeella miinoja $m$ voi olla $m < rs-9$. "Klassisessa" miinaharavassa siten kuin se yleensä ymmärretään, ja kuten esim. minesweeper.online toimii (Vista, 2007, mappi generoidaan 1. klikkauksen jälkeen, 1. klikkaus on 0-8), jonka itsekin toteutin, taataan aina että ensimmäinen klikattu ruutu on 0-8. Koska on mahdollista klikata muualle kuin reunaan/kulmaan, on siis maksimimäärä miinoja, joita mappiin mahtuu, $rs-8$. Tämä on ihan mukavaa pelaajalle, ja mukavampaa testaamisen ja demoamisen kannalta myös (ettei joka ikisellä expert-pelillä aloiteta tilanteessa, jossa nurkassa on "1" tai "2" -> pakko arvata seuraavaksi).
Jos miinoja antaa olla $rs-8$ (eikä $m<rs-9$), niin jokainen aloitettu peli päättyy automaattiseen voittoon, jos aloitetaan muualta kuin minkä tahansa reunan vierestä (mukaan lukien nurkasta). Vähän hölmöä, joten siksi päätin, että $m < rs-9$ eikä $m \leq rs-8$.
