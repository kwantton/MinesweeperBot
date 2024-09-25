1. Tehty tällä viikolla:
- `class Minesweeper` on nyt olemassa `mapGenerator.py`:ssä. Tämä on ihmisten (hiirellä) JA BOTIN (`simple_solver`-osan ja halutessaan lisäksi `CSP_solver`:in) pelattava versio
    - visuaalista käyttöliittymää käytetään näppäimillä, jotka on lueteltu itse käyttöliittymän alaosassa
        - bottia käytetään b-näppäimellä; jos miinaharavapeli käynnistettiin esim. `Minesweeper(beginner[0], beginner[1], beginner[2], csp_on=True)`-komennolla, tällöin botin älyllä kyseisessä beginner-mapissa on käytössään myös `CSP_solver`-luokka. Jos `csp_on=False`, tällöin on käytössä vain `simple_solver()`-funktio (`bot_act()`-metodin `brain`-funktiossa). 
        - UPDATE 15.9: `CSP_solver`-luokka toimii, eikä enää merkkaa väärin miinoja (ongelma ratkaistu eräässä commitissa). Sitä voi nyt hyvin käyttää, ja näkee sen ratkaisemat ruudut, kun painaa `c`-näppäintä
        - `space` aloittaa uuden pelin
        - `q` lopettaa
        - `m` näyttää kaikkien miinojen todelliset sijainnit (tiedon, jota automaattisesti pelaajalla tai botilla ei ole ilman päättelyä (ja tuuria))
        - `f` näyttää `self.front`:in (`self.front` on `set()` johon joka b-painalluksella päivittyvät etulinjan ruudut eli ne ruudut joista on päättelyssä hyötyä; kun `csp_on=False`, tämä `front`:in päivittäminen toimii täysin oikein, kun taas jos `csp_on=True` eli jos `CSP_solver` on käytössä, frontin vanhojen osien poistaminen ei täysin toimi 1. b-painalluksen jälkeen (to-do).
    - [ ] frontin päivitys CSP:tä käytettäessä ei siis täysin toimi (vanhojen frontin jäsenten poistaminen on puutteellista);
    - [x]  pelkkää `simple_solver()`:ia käytettäessä frontin päivitys joka b-painalluksen jälkeen toimii täysin oikein ja halutusti

Luokassa toimii
- [x] mapin generointi (mielivaltainen koko, miinoja korkeintaan korkeus $\cdot$ leveys - 1) ensimmäisen klikkauksen jälkeen
- [x] häviön ja voiton tunnistaminen
- [x] miinalaskuri
- [x] chordaus, joka on käytettävissä myös botin pelatessa (chordaus tarkoittaa sitä, että kun hiiren vasemmalla klikataan toisen kerran avattua ruutua, jonka ympärille on merkitty sama määrä lippuja kuin mikä ruudun arvo on, niin kaikki liputtamattomat ympäröivät ruudut avautuvat)
- [x] 0-ruutujen ja näitä ympäröivien tiilien automaattinen ketjuuntuva avautuminen 0-ruudun avaamisen jälkeen, kuten oikeassakin miinaharavassa
- [x] `Minesweeper(width,height,mines,csp_on=False)` aloittaa `simple_solver()`:iin rajoittuvan pelimuodon, jossa botilla pelatessa (kun painaa `b`, yksi liike per b-painallus) käytetään pelkkää `simple_solver()`:in logiikkaa
- [x] puolestaan `Minesweeper(width,height,mines,csp_on=True)` aloittaa pelimuodon, jossa botilla pelatessa (kun painaa 'b' näppäimistöltä toistuvasti, yksi liike per b-painallus) on käytössä myös `CSP_solver()`-luokka, ja tämän lisäksi pohjalla `simple_solver()`:in logiikka. 
HUOM! En takaa toteutuksessani minimi-3x3:n alkuavausta toisin kuin alkuperäisessä miinaharavassa taataan, vaan teen kuten 'minesweeper.online'-sivulla, eli ilman alkuavauksen takaamista. Tämän voi helposti muuttaa myöhemmin jos haluaa vertailla esim. Becerran kandityön prosenttiosuuksiin voitoista eri pelimuodoissa.
- [x] esimerkkikuva lineaariyhtälöryppäästä, jossa sekä ilman CSP:tä (ilman tietoa siitä että joka ruudulle $r$ pätee $r \in \set{0,1}$ missä 0 ja 1 ovat miinojen lukumäärä kyseisessä ruudussa) saadaan pääteltyä turvallinen ruutu
- [x] `python-constraint` toimii näköjään hyvin näiden CSP-yhtälöryhmien ratkaisussa. Voisin käyttää tätä testaamisessa sen varmistamiseen, että oma CSP_solver-luokkani toimii kaikissa tapauksissa

Kesken:
- [ ] vanhan frontin poistaminen CSP:tä käytettäessä on jostain syystä lähes olematonta. Ainoa varsinainen tästä seuraava ongelma on turha laskenta näitä vanhoja front-ruutuja koskien.
- [ ] vilkuiltu Becerran kandityötä, pitää lukea lisää
2. Miten edistynyt: melko erinomaisesti, yllä asiat
    - `Minesweeper`-luokka on tehty, ja hahmottelin lineaariyhtälöitä CSP:llä ja ilman (tiedosto `/Esim_evil_1.png`).
    - `CSP_solver`-luokka
        - [x] kuusi yksikkötestiä löytyy (kuusi yhtälörypästä miinaharavan kontekstissa, eli CSP-rajoitteella että jokainen solu (eli muuttuja) on joko 0 tai 1)
3. Mitä opin:
- [x] Tein esimerkkitilanteen (no guessing evil-peli) jossa sekä CSP:llä että ilman saatiin ratkaisu käyttäen yhtälöryhmiä
- [x] opin siitä että ainakin joskus monimutkaisissakin tilanteissa on mahdollista saada ratkaisu sekä CSP:llä että ilman
- [x] Opin että `python-constraint` on olemassa, ja jos sen kaikissa tuloksissa on jokin muuttuja 0, kyseinen ruutu on miinaton, ja jos taas aina 1, niin siinä on miina
- [x] Kahden luokan tekeminen
- [x] CSP-solverin väsäystä
- [x] `botGame.py`:n Minesweeper-luokka on melko hyvin jaettu funktioihin, ja esim. käyttöliittymään toiminnallisuuksien lisääminen on hyvin suoraviivaista.

4. Epäselvää: ei sinänsä mikään; pitää jatkaa `CSP_solver`-luokan tekemistä (korjaamista) ja selkiyttää sen koodia niin paljon kuin mahdollista. Huom. olen käyttänyt tähän vasta 7 päivää, sikäli hyvin etenee.
5. Seuraavaksi: jatkan `CSP_solver`-luokan tekemistä (korjaamista) ja selkiytän sen koodia niin paljon kuin mahdollista. Jos saan `CSP_solver`:in nähtävästi toimimaan, keskityn seuraavaksi testien tekemiseen, jotta voidaan selvittää, toimiiko solver oikeasti _kaikissa_ tapauksissa.
