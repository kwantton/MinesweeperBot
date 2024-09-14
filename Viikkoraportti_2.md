(WIP viikko 2: tulee päivittymään vielä ennen lauantaita)

1. viime viikolla tehdyn lisäksi:
- `class Minesweeper` on nyt olemassa mapGenerator.py:ssä. Tämä on ihmisten (hiirellä) JA BOTIN (simple solver, ja halutessaan lisäksi CSP_solver) pelattava versio
    - visuaalista käyttöliittymää käytetään näppäimillä, jotka on lueteltu itse käyttöliittymän alaosassa
        - bottia käytetään b-näppäimellä; jos miinaharavapeli käynnistettiin esim. 'Minesweeper(beginner[0], beginner[1], beginner[2], csp_on=True)'-komennolla, tällöin botin älyllä on käytössään myös 'CSP_solver'-luokka. Jos csp_on=False, tällöin on käytössä vain 'simple_solver()'-funktio bot_act().metodin brain-funktiossa. 
        - HUOM! CSP_solver-luokka tai sen keskustelu botGame.py:n kanssa (?) on osin rikki vielä. Sitä voi kuitenkin käyttää, ja näkee mielenkiintoisia bugeja sitä käyttäessään, kun painaa c-näppäintä
        - space aloittaa uuden pelin
        - q lopettaa
        - f näyttää frontin; tämä toimii täysin oikein, jos csp_on=False, mutta on vielä rikki jos cap_on=False
    - frontin päivitys CSP:tä käytettäessä ei toimi; ainoastaan pelkkää simple_solver():ia käytettäessä frontin päivitys joka b-painalluksen jälkeen toimii oikein
Luokassa toimii
- [x] mapin generointi (mielivaltainen koko, miinoja korkeintaan korkeys$\cdot$leveys - 1) ensimmäisen klikkauksen jälkeen
- [x] häviön ja voiton tunnistaminen
- [x] miinalaskuri
- [x] chordaus (sikäli turhahko botin kannalta, mutta oli hauska tehdä)
- [x] 0-ruutujen ja näitä ympäröivien tiilien automaattinen ketjuuntuva avautuminen 0:aa klikatessa, kuten oikeassakin 
- [x] Minesweeper(width,height,mines,csp_on=False) aloittaa 'simple_solver()':iin rajoittuvan pelimuodon, jossa botilla pelatessa (kun painaa 'b' näppäimistöltä, yksi liike per b-painallus) käytetään pelkkää 'simple_solver()':in logiikkaa
- [x] puolestaan Minesweeper(width,height,mines,csp_on=True) aloittaa pelimuodon, jossa botilla pelatessa (kun painaa 'b' näppäimistöltä toistuvasti, yksi liike per b-painallus) on käytössä myös 'CSP_solver()'-luokka, ja tämän lisäksi pohjalla 'simple_solver()':in logiikka. 
- [ ] CSP_solver toisinaan aiheuttaa ruutujen identifioimisen väärin, eli on osittain rikki vielä
miinaharavassa
HUOM! En takaa toteutuksessani minimi-3x3:n alkuavausta toisin kuin alkuperäisessä miinaharavassa taataan, vaan teen kuten 'minesweeper.online'-sivulla, eli ilman alkuavauksen takaamista. Tämän voi helposti muuttaa myöhemmin jos haluaa vertailla esim. Becerran kandityön prosenttiosuuksiin voitoista eri pelimuodoissa.
- [x] esimerkkikuva lineaariyhtälöryppäästä, jossa sekä ilman CSP:tä (ilman tietoa siitä että joka ruudulle $r$ pätee $r \in \set{0,1}$ missä 0 ja 1 ovat miinojen lukumäärä kyseisessä ruudussa) saadaan pääteltyä turvallinen ruutu
- [x] `python-constraint` toimii näköjään hyvin näiden CSP-yhtälöryhmien ratkaisussa. Voisin käyttää tätä testaamisessa sen varmistamiseen, että oma CSP_solver-luokkani toimii kaikissa tapauksissa
[ ] vilkuiltu Becerran kandityötä, pitää lukea lisää
2. Tehty: 
    - `Minesweeper`-luokka on tehty, ja hahmottelin lineaariyhtälöitä CSP:llä ja ilman (tiedosto '/Esim_evil_1.png').
    - `CSP_solver`-luokka
3. Mitä opin:
- [x] Tein esimerkkitilanteen (no guessing evil-peli) jossa sekä CSP:llä että ilman saatiin ratkaisu käyttäen yhtälöryhmiä
- [x] opin siitä että ainakin joskus monimutkaisissakin tilanteissa on mahdollista saada ratkaisu sekä CSP:llä että ilman
- [x] Opin että `python-constraint` on olemassa, ja jos sen kaikissa tuloksissa on jokin muuttuja 0, kyseinen ruutu on miinaton, ja jos taas aina 1, niin siinä on miina

4. Epäselvää: ei sinänsä mikään; pitää jatkaa CSP_solver-luokan tekemistä (korjaamista) ja selkiyttää sen koodia niin paljon kuin mahdollista. Huom. olen käyttänyt tähän vasta 7 päivää, sikäli hyvin etenee.
5. Seuraavaksi: jatkan CSP_solver-luokan tekemistä (korjaamista) ja selkiyttää sen koodia niin paljon kuin mahdollista
