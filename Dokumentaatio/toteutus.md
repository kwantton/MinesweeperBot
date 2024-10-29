<h2> Ohjelman yleisrakenne </h2>

Graafinen käyttöliittymä on toteutettu `pygame`:ä käyttäen.

Itse miinaharavapeli on tiedostossa `botGame.py`. Kaikki kenttien (tai boolen yhtälöryhmien) ratkomiseen liittyvä logiikka on tiedostossa `CSP_solver.py`, PAITSI `simple_solver()`-funktio, joka osaa tehdä seuraavat kaksi asiaa:

- jos numeroruudun ympärillä olevien lippujen lukumäärä = ruudun numero, avaa kaikki muut kuin liputetut ruudut ympäriltä
- jos numeroruudun ympärillä olevien liputettujen + liputtamattomien ('unclicked cell') ruutujen summa = ruudun numero, liputa kaikki liputettavissa olevat ympäröivät ruudut

Ylläoleva on niin äärimmäisen yksinkertainen tapaus, että se oli paljon simppelimpää tehdä luupin aikana 'botGame.py':ssä kuin siirtää kaikki tieto kaikista ruuduista vain ja ainoastaan tätä tarkoitusta varten `CSP_solver`:ille. Toisin muotoiltuna: botGame.py:stä siirtyy ainoastaan `CSP_solver`:ille yhtälöitä ja luku joka vastaa miinaharavan oikean ylänurkan lukua (eli koko mapin alkuperäinen miinamäärä - lippujen määrä), sekä minecountia varten tieto, montako klikkaamatonta ruutua on ylipäätään kentässä jäljellä:

```python
self.solver.absolut_brut(minecount = self.minecount,                # the right top of normal minesweeper shows this number
    all_unclicked = all_unclicked_cells,                            # all unclicked cells (excludes flagged ones)
    unclicked_unseen_cells = unclicked_unseen_cells,                # unclicked cells that are not neighbours of 'self.front'
    number_of_unclicked_unseen_cells = n_unclicked_unseen_cells)    # the number of the cells above
                    
```
Ylläoleva kutsuu `CSP_solver`:ia, ja antaa sille tietoja, mitä käyttää. Kuitenkaan ylläoleva ei anna itse yhtälöitä, sen tekee funktio `feed_csp_solver()`, joka on vähän turhan pitkä tänne laitettavaksi.

Botti aloittaa vasemmasta yläkulmasta (huom. voit aloittaa klikkaamalla mistä vain, ja antaa botin pelata sen jälkeen, jos niin haluaa), ja etenee `self.front`:ia, jota se tällä hetkellä (5.10.24) onnistuneesti ylläpitää (poistaa `self.front`:ista joka kierroksen jälkeen ruudut, jotka eivät tarjoa enää informaatiota jota voidaan hyödyntää ratkaisun kannalta, ja lisää `self.front`:iin sellaiset avatut ruudut, jotka tarjoavat informaatiota. Tämän 'hyödyllisyyden' määritelmä on yksinkertaisesti se, onko kyseisen avatun ruudun ympärillä enää avaamattomia ruutuja vai ei; jos on, ruutu on `self.front`:issa)

Tällä hetkellä CSP:tä hyödyntävä botti osaa ratkaista kaikki tapaukset.

Ratkaisu (arvaukset mukaanlukien) on kahdeksanvaiheinen (19.10.2024):
1. `simple_solver()` (in 'botGame.py') solves the simplest of cases, solving all cases of number-cell-number-equals-to-surrounding-unclicked-cells and all cases of number-cell-number-equals-to-surrounding-flags before ever moving on to call `CSP_solver`, thus limiting work done later in `CSP_solver` (which practically always is needed many times per game in case of Expert maps)
2. `CSP_solver_old` jos 1. ei tuottanut ratkaisuja. Jos tämäkään ei, niin seuraava:
3. Moving to `CSP_solver`: grouping equations to separated equation sets where sets do not share variables with other sets. This significantly limits the size of the problems solved by the machinery below.
4. finding solution combinations per one equation (equation is, for example, a+b=1, where a and b are cells (cell=ruutu)). So at this point, each equation set has all possible answers per every equation
5. for each equation set, chain link equations. The order of the chain: the equations in each separated equation set are first sorted, ensuring that in almost all cases, linking between each equation pair is done so that some alternative answers per each equation can be discarded due to incompatibility with the equation before and/or after (a chain has 2 ends, that's why 'and/or' was written).
6. after chain linking, in the same order as in the previous step, traverse through all possible chains, which always start from the same starting equation, called the 'starting group' per each equation set. There's bookkeeping for variables so conflicts are found, and if conflicts are found, backtracking happens, discarding the whole branch so far. Essentially, there are as many 'alt tree roots' per equation group as there are alternative answers to the first equation (i.e. the 'starting group'). Thanks to this and the previous step, all the impossible answers are quite effieciently backtracked, and thanks to keeping equation sets separate when possible, the size of the trees is severely limited in most cases.
7. for each equation set's possible whole answers received in the previous step, check if one or more variables were always 1 or always 0 in all possible alternative answers. If such variables were found, they are absolute answers for that variable (i.e. other answers are impossible). If not, the numbers of 1 vs 0 for each variable have now been recorded, and a guess can be taken, UNLESS the next step evaluates to true
8. check for need for minecount: if the sum of max numbers of mines in all the combined (separated) fronts is less than the remaining minecount, this always evaluates to false. If the max sum equals to remaining minecount, then all unclicked unseen cells are 0 (no mine) and only the max mine count alt solutions can be viable, and if only the min sum equals to remaining minecount, then all unclicked unseen cells are 0 and only the min mine count solutions can be viable, and if something between max and min, another round of discarding minecount-invalid alt solutions must be done. There is no simpler way to describe this, I'm sorry. The alternative would be to add another equation to the mix, the one that has ALL remaining variables (all unclicked cells) and the total minecount, but you probably see the problem with this: it's far more inefficient, and with large variable numbers, the number of combinations from this can go to over $10^100$ possible answers in worst cases - not doable by backtracking and/or brute forcing alone! My solution is very good regarding this.
9. if the previous step didn't produce answers, guess using the minecount situation -derived minecounts. Like the previous possibility for guessing (if minecount was not even needed), this chooses the cell with lowest chance of being a mine, comparing front cells to unseen unclicked cells. If unseen unclicked cells have the lowest chance of being a mine, a corner is opened (4 corners exist per map) if they are still available, and if all corners have already been used, then a front cell's neighbouring unclicked unseen cells is guessed.

Toteutuksessani halusin väsätä kaiken 'itse'. Saatan käyttää coupled subsets CSP:tä (CSCSP:tä, kuten Becerra 2015), mutta en ole lukenut työtä kunnolla, ja esim. yhtälöiden ketjuttamisen keksin itse (se siis nimenomaan on ketju eikä verkko, ja vaati ymmärryksen siitä, että kaikkien settien kaikkien yhtälöiden globaalit ratkaisut koostuvat niistä alteista, jotka myös joka ikinen yhtälöpari jakaa keskenään, eli ketjuttamisjärjestyksellä ei ole väliä, kaikki globaalit ratkaisut löydetään järjestyksestä riippumatta). 

<h2> Saavutetut aika- ja tilavaativuudet (esim. O-analyysit pseudokoodista) </h2>
Kuten määrittelydokumentissa (https://github.com/kwantton/MinesweeperBot/blob/improved_time_complexity/Dokumentaatio/m%C3%A4%C3%A4rittely.md), pahimmassa tapauksessa aikavaativuus on syötteen koon (yhtälöiden määrän) suhteen eksponentiaalinen.

Nämä 'pahimmat tapaukset' ovat README.md:ssä kuvattujen kikkojen ansiosta tosin hyvin harvinaisia, sillä keskimääräinen expert-ratkaisuaika on minulla [tällä hetkellä](../Testing/Win_percentages_and_average_time_per_game_only_classic.pdf) 77 ms (n = 204 817).

Ratkaisuajat vaihtelevat nopeasti hävitystä pelistä (noin 5 ms) pahimpiin tapauksiin joissa ensin normilogiikalla ei saada, ja todetaan että minecountia tarvitaan, ja todetaan että sieltä löytyy ratkaisu (41 minuuttia on pisin yllä linkatussa dokumentissa).

<h2> Suorituskyky- ja O-analyysivertailu (mikäli sopii työn aiheeseen) </h2>

Lukee 'määrittely'-dokumentissa (https://github.com/kwantton/MinesweeperBot/blob/improved_time_complexity/Dokumentaatio/m%C3%A4%C3%A4rittely.md), ja [README.md](/README.md):n results-osastossa

<h2>Työn mahdolliset puutteet ja parannusehdotukset</h2>
Lukee 'README.md':ssä.
- automaattitestejä. EN OLE käynyt kurssia 'ohjelmistotuotanto' enkä ole koskaan automaattitestannut mitään, ja melkein aika meni itse solverin väsäämiseen (kotikutoisesti, mallikoodia mistään katsomatta!) ja testausmittariston rakentamiseen ja testaamiseen pelejä ratkaisemalla ja tarkastamalla hävittyjä pelejä käyttäen **constraint_problem_solver_for_testing.py**-tiedoston `check_if_solutions_were_missed_in_lost_game()`-funktiota
- arvailua todellakin voisi parantaa, mutta se on jo todella vaikea ongelma
- `join_comp_groups_into_solutions()` on edelleen pullonkaula aikavaativuudessa. Tähän tuli HUOMATTAVA parannus kun väsäsin paremmat overlapit muuttujille metodilla `CSP_solver.better_overlap_order_eqs_of_disjoint_eq_set()`. Edelleen kuitenkin JOS harvinaisen paha Expert-tilanne jää laskemaan kymmeniksi minuuteiksi, se jää juuri tähän jumiin (kuten voi konsolista katsomalla todeta). Kuitenkin, pystyn ajamaan 100 000 Expert-peliä keskimääräisessä ratkaisuajassa 80 ms/peli läpi putkeen tästä huolimatta. Melkein ikinä minecount filtering ei ole ongelma, koska olin ovela ja kerään sen aikana listaa siitä, onko kukin muuttuja ollut vähintään kerran 0 ja 1 jossain viaabelissa ratkaisuehdokkaassa. Siinä vaiheessa kun vastaus tähän on 'kyllä', tiedetään että muuttujia ei saada ratkaistua 100% varmuudella, ja voidaan lopettaa ratkaisujen hakeminen siihen! Valitettavasti tätä ei voi tehdä vielä `join_comp_groups_into_solutions()`:ssa, koska tällöin EI vielä tiedetä, voisiko minecount tarjota jotain hyödyllistä lisää! Tätä voisi osissa tapauksissa ratkaista kyllä (vastata suoraan "ei" selvissä tilanteissa), mutta en ole ehtinyt tällaista tehdä

<h2> Laajojen kielimallien (ChatGPT yms.) käyttö. </h2>
<em>Mainitse mitä mallia on käytetty ja miten. Mainitse myös mikäli et ole käyttänyt. Tämä on tärkeää! </em>

- Itse ratkaisijan (`CSP_solver`, enkä `simple_solver()`:in minkään osan) kehityksessä en ole kertaakaan käyttänyt tekoälyä. Samoin, arvausten tekemisessä en ole käyttänyt tekoälyä.
- `botGame.py`:ssä eli miinaharavapelissä (johon botti on integroituna) kysyin ChatGPT:ltä
  - miten saadaan alfa-arvo highlighteihin, ja
  - kysyin mapin yllä olevan infoboksin lisäämisen jälkeen debuggaukseen y-koordinaattien suhteen apua ChatGPT:ltä, josta sain `cell_y = (mouse_y - self.infobar_height) // self.cell_size              # Like explained in the above comment. Implementation here: adjust for the infobar by 'raising' the click by infobar height, then get the row number by division by self.scale. Asked from ChatGPT when trying to find the problem with the y-location` -ratkaisun. Nämä eivät liity siis bottiin, vaan itse miinaharavapelin toteutukseen
- siitä, miten otan käyttöön `constraint.Problem`:in tarkastaakseni hävittyjä pelejä (eli miten tämä kirjasto toimii), kysyin ChatGPT:ltä. Itse hävittyjen pelien tallentamisen ja siirtämisen tälle tarkastajalle väsäsin itse, samoin kuin tulostusten ulkomuodon, ja samoin `logic_testing=True`, ja `unnecessary_guesses=False` tai True testatakseni testaajaa (eli testaajan testaamisen väsäsin ihan itse)

<h2>aiempia huomautuksia</h2>

- etenkin harvamiinaisissa kentissä (mapeissa) monesti riittää pelkkä ympäröivän 8 ruudun tarkastelu, mutta joskus taas ei - tällöin otetaan käyttöön tietoa ympäröivien ruutujen miinaluvuista, ja tämä voi mennä hyvinkin monimutkaiseksi, kuten voi itselleen todistaa täällä https://minesweeper.online/game/3720717509 (no guessing mode, mappi 'evil')
- optimaalisia arvauksia käsitellään JOS päästään siihen vaiheeseen tämän algoritmin kehittämisessä, että kaikki mahdollinen logiikka (mukaanlukien minecount kaikissa mahdollisissa tapauksissa, koosta riippumatta kunhan koko on realistinen (expert yläarajana)) on ratkaistu ja voidaan seuraavaksi alkaa tehdä myös fiksuja arvauksia pakon osuessa (mieluiten käyttäen ehdollisia todennäköisyyksiä), eli JOS ollaan jo tehokkaasti ratkaistu kaikki 'pelkällä logiikalla' ratkaistavissa olevat tilanteet, mukaan lukien käyttäen tietoa jäljelläolevien miinojen lukumääristä ja viereisten ruutujen lukuarvoista.

<h2>Viitteet</h2>
- Becerra, David J. 2015. Algorithmic Approaches to Playing Minesweeper. Bachelor's thesis,
Harvard College (permalink: http://nrs.harvard.edu/urn-3:HUL.InstRepos:14398552).
- Paras tulos, johon olen törmännyt, on 41% voitettuja klassisia Expert-kenttiä (https://github.com/DavidNHill/JSMinesweeper#readme). 
- Toiseksi paras on päälle 39% (Tu, Li, Chen et al., 2017, AAAI-17 Workshop on What's Next for AI in Games?).
