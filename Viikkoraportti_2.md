(WIP viikko 2: tulee päivittymään vielä ennen lauantaita)

1. viime viikolla tehdyn lisäksi:
- `class Minesweeper` on nyt olemassa mapGenerator.py:ssä. Tämä on ihmisten pelattava versio, mutta iso osa sen toiminnallisuuksista tulee hyötykäyttöön myös botin testaamisessa.
Luokassa toimii
[x] mapin generointi (mielivaltainen koko, miinoja korkeintaan korkeys$\cdot$leveys - 1) ensimmäisen klikkauksen jälkeen
[x] häviön ja voiton tunnistaminen
[x] miinalaskuri
[x] chordaus (sikäli turhahko botin kannalta, mutta oli hauska tehdä)
[x] 0-ruutujen ja näitä ympäröivien tiilien automaattinen ketjuuntuva avautuminen 0:aa klikatessa, kuten oikeassakin miinaharavassa
HUOM! En takaa toteutuksessani minimi-3x3:n alkuavausta toisin kuin alkuperäisessä miinaharavassa taataan, vaan teen kuten 'minesweeper.online'-sivulla, eli ilman alkuavauksen takaamista. Tämän voi helposti muuttaa myöhemmin jos haluaa vertailla esim. Becerran kandityön prosenttiosuuksiin voitoista eri pelimuodoissa.
[x] esimerkkikuva lineaariyhtälöryppäästä, jossa sekä ilman CSP:tä (ilman tietoa siitä että joka ruudulle $r$ pätee $r \in \set{0,1}$ missä 0 ja 1 ovat miinojen lukumäärä kyseisessä ruudussa) saadaan pääteltyä turvallinen ruutu
[x] `python-constraint` toimii näköjään hyvin näiden CSP-yhtälöryhmien ratkaisussa. On otettava selvää, kuinka tehokkaita nämä ratkaisut ovat - voi olla, etteivät tarpeeksi tehokkaita.
[ ] vilkuiltu Becerran kandityötä, pitää lukea lisää
2. `Minesweeper`-luokka on tehty, ja hahmottelin lineaariyhtälöitä CSP:llä ja ilman (tiedosto '/Esim_evil_1.png').
3. Mitä opin:
[x] Tein esimerkkitilanteen (no guessing evil-peli) jossa sekä CSP:llä että ilman saatiin ratkaisu käyttäen yhtälöryhmiä
[x] opin siis että ainakin joskus monimutkaisissakin tilanteissa on mahdollista saada ratkaisu sekä CSP:llä että ilman
[x] Opin että `python-constraint` on olemassa, ja jos sen kaikissa tuloksissa on jokin muuttuja 0, kyseinen ruutu on miinaton, ja jos taas aina 1, niin siinä on miina

4. Epäselvää: kuinka tehokas `python-constraint` on, kokeilenko testimielessä aluksi käyttää sitä ja korvaan sen myöhemmin omalla toteutuksellani `python-constraint`:ista vai pläräänkö esim. ainoastaan Becerran työtä
5. Seuraavaksi: luen Becerran kandityötä, ja rupean ytimen koodaamiseen (coupled subsets CSP; käyttäen `python-constraintia` vai ei?)
