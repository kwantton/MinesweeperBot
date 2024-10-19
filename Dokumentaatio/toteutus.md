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

Tällä hetkellä CSP:tä hyödyntävä botti osaa ratkaista kaikki tapaukset. Pahimmissa peleissä (0.04% expert-peleistä tähän mennessä) ohjelma tapetaan automaattisesti, todennäköisesti siksi että erästä `traverse()`-funktiota kutsutaan miljoonia kertoja pahimmissa tapauksissa.

Ratkaisussa on 6 vaihetta, joissa arvaus voi tapahtua joko viimeisenä, tai aiemmin, jolloin myöskään loppuosaa (minecount) ei suoriteta.

(1-5) definitive solutions for variables using logic, and if that doesn't help, then (6) guess: 
 
1. Group equations to sets (1.1 and 1.2); all the members of one such equation set share variables directly or indirectly with each other (indirectly means, via other equations in that set) 
2. `find_and_group_possible_answers_per_single_equation()`: find all alt combinations of 1s PER EACH EQUATION (in each set, which doesn't matter at this step) that MUST be satisfied (i.e. each number cell on the minesweeper map). There are not too many, since the max lenght of an equation is 8, and the max sum is 8. Almost always these equations are a+b=1, or a+b+c=2, or the like. 
3. Chain link equations: each separated equation set is next fed through this process (reminder: the reason they were separated is that all the equations in one set share variables with each other at least via other equations if not directly). For each separated equation set, find compatible alt solutions in a chain of equations, filtering out those alt solutions that are not compatible with one or more other equations' any alt answer. So from all of the alternative combinations of 1s and 0s that DO satisfy the CURRENT equation (group of alt answers), filter out those alternatives that are incompatible with all possible alt answers from any other (random) equation that is in the same equation set (shares variables directly or indirectly with other members of that equation set), pairing one group's all possible alts with compatible alts of ONE other group (i.e. "groups", i.e. incompatible with ALL the alternative solutions of at least one other group)

Sharing common variables for equation pairs is ensured by (1) performing chain linking for each separated eq set in turn (ensuring that there are common variables in each set), (2) sorting the equations within each equation set before linking, then linking in the sorting order -> usually max number of variables are shared this way, as each eqation's variables are already sorted (for example a+b+c=1), so for example a+b+c=1, a+d+e=2, b+d+f=1, etc. sorting ensures that variables are usually shared between each equation pair.

4. From the remaining alt equations per group (i.e. PER original equation), find columns where a variable is always 0 or 1 -> it HAS to be 0 or 1 ALWAYS. Then see these new solutions, inspect the remaining equations for untrue alternatives now that we've solved a new variable (or many new variables), and keep repeating the whole loop (1),(2),(3) as long as new solutions keep coming. Stop iteration when there are no longer new solutions produced by the whole loop. 
5. If no definitive variable solutions were found, check the need for minecount (it's quite simple at this point). If minecount can provide solutions (= if max number of mines in `self.front` ≥ remaining minecount), use alt solution mine number counting to check, if there are more restrictions posed by this. If there are, there might be more answers found at this point by this 'minecount logic'.
6. If nothing else above helps, if `self.solved_new_vars_during_this_round = False` at this point, then guess.



<h2> Saavutetut aika- ja tilavaativuudet (esim. O-analyysit pseudokoodista) </h2>
to-do

<h2> Suorituskyky- ja O-analyysivertailu (mikäli sopii työn aiheeseen) </h2>

'win_percentages_and_average_time_per_game.pdf' kansiossa '/Testaus'
19.10.2024 mennessä 15407 peliä, joista 38.40% voitettu, keskimäärin 0.61 sekuntia/peli (mukaanlukien pahimmat tapaukset, poislukien ne joissa 'killed' eli prosessi tapettiin automaattisesti).
Tyypillinen expert peli kestää: (pelasin muutaman tätä listaa varten): 

- 86 ms (voitettu, 8 arvausta),
- 202 ms (hävitty, 3 arvausta),
- 42 ms (hävitty, 2 arvausta),
- 23 ms (voitettu, 1 arvaus),
- 97 ms (hävitty, 6 arvausta),
- 25 ms (voitettu, 2 arvausta),
- 75 ms (voitettu, 2 arvausta),
- 293 ms (hävitty, 5 arvausta),
- 35 ms (voitettu, 1 arvaus)
- 2.3 ms (hävitty, 1 arvaus)
- 3 ms (hävitty, 1 arvaus)
- 42 ms (hävitty, 4 arvausta)
- 38 ms (voitettu, 2 arvausta)
... jne

Becerran kandityössä (Becerra, David J. 2015. Algorithmic Approaches to Playing Minesweeper. Bachelor's thesis, Harvard College.) paras expert-voittoprosentti oli 32.90 % CSCSP:tä käyttäen (coupled subsets CSP, CSP = constraint satisfaction problem (solver, tässä tapauksessa)).


<h2>Työn mahdolliset puutteet ja parannusehdotukset</h2>
Lukee 'README.md':ssä.
- jos ratkaisulogiikkaa ei nopeuttaisi, tapa ratkaista pisimmät pelit olisi käyttää timeria, jonka umpeutuessa arvataan mahd. fiksusti sen sijaan että yritetään ratkaista puhtaasti/selvittää paras mahdollinen arvaus
- automaattitestejä
- jne, 'README.md'

<h2> Laajojen kielimallien (ChatGPT yms.) käyttö. </h2>
<em>Mainitse mitä mallia on käytetty ja miten. Mainitse myös mikäli et ole käyttänyt. Tämä on tärkeää! </em>

- Itse ratkaisijan (`CSP_solver`, enkä `simple_solver()`:in minkään osan) kehityksessä en ole kertaakaan käyttänyt tekoälyä. Samoin, arvausten tekemisessä en ole käyttänyt tekoälyä.
- `botGame.py`:ssä eli miinaharavapelissä (johon botti on integroituna) kysyin ChatGPT:ltä
  - miten saadaan alfa-arvo highlighteihin, ja
  - kysyin mapin yllä olevan infoboksin lisäämisen jälkeen debuggaukseen y-koordinaattien suhteen apua ChatGPT:ltä, josta sain `cell_y = (mouse_y - self.infobar_height) // self.cell_size              # Like explained in the above comment. Implementation here: adjust for the infobar by 'raising' the click by infobar height, then get the row number by division by self.scale. Asked from ChatGPT when trying to find the problem with the y-location` -ratkaisun. Nämä eivät liity siis bottiin, vaan itse miinaharavapelin toteutukseen.

<h2>aiempia huomautuksia</h2>

- etenkin harvamiinaisissa kentissä (mapeissa) monesti riittää pelkkä ympäröivän 8 ruudun tarkastelu, mutta joskus taas ei - tällöin otetaan käyttöön tietoa ympäröivien ruutujen miinaluvuista, ja tämä voi mennä hyvinkin monimutkaiseksi, kuten voi itselleen todistaa täällä https://minesweeper.online/game/3720717509 (no guessing mode, mappi 'evil')
- optimaalisia arvauksia käsitellään JOS päästään siihen vaiheeseen tämän algoritmin kehittämisessä, että kaikki mahdollinen logiikka (mukaanlukien minecount kaikissa mahdollisissa tapauksissa, koosta riippumatta kunhan koko on realistinen (expert yläarajana)) on ratkaistu ja voidaan seuraavaksi alkaa tehdä myös fiksuja arvauksia pakon osuessa (mieluiten käyttäen ehdollisia todennäköisyyksiä), eli JOS ollaan jo tehokkaasti ratkaistu kaikki 'pelkällä logiikalla' ratkaistavissa olevat tilanteet, mukaan lukien käyttäen tietoa jäljelläolevien miinojen lukumääristä ja viereisten ruutujen lukuarvoista.


<h2>Viitteet</h2>
Becerra, David J. 2015. Algorithmic Approaches to Playing Minesweeper. Bachelor's thesis, Harvard College.
