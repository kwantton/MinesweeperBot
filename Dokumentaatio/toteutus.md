- [ ] to-do: Ohjelman yleisrakenne

<h2> Ohjelman yleisrakenne </h2>

Graafinen käyttöliittymä on toteutettu `pygame`:ä käyttäen.

Botti aloittaa vasemmasta yläkulmasta, ja etenee `self.front`:ia, jota se tällä hetkellä (24.9.24) onnistuneesti ylläpitää (poistaa `self.front`:ista joka kierroksen jälkeen ruudut, jotka eivät tarjoa enää informaatiota jota voidaan hyödyntää ratkaisun kannalta, ja lisää `self.front`:iin sellaiset avatut ruudut, jotka tarjoavat informaatiota. Tämän 'hyödyllisyyden' määritelmä on yksinkertaisesti se, onko kyseisen avatun ruudun ympärillä enää avaamattomia ruutuja vai ei; jos on, ruutu on `self.front`:issa)

Tällä hetkellä CSP:tä hyödyntävä botti osaa ratkaista suurimman osan tapauksista. Minulla on nyt kaksi vaihtoehtoa:

(a) lisätä CSP:tä hyödyntävää logiikkaa tapaus kerrallaan (mitkä tapaukset? minulla ei ole matemaattista todistusta siitä, minkälainen rajallinen joukko tapauksia riittää; siis minkälaisiin tapauksiin loppujen lopuksi tiettyjä operaatioita hyödyntämällä voidaan redusoida kaikki muut tapaukset)
(b) koska `self.front`:in kirjanpito toimii, käyttää kussakin yhtälöryppäässä, jotka jakavat yhteisen muuttujan, brute-force-tyyppistä ratkaisua (joka ei ole paha, koska yhtälöitä voi olla korkeintaan 8 per muuttuja ja jokainen muuttuja on 0 tai 1 - ei ole paljoa kokeiltavaa) selvittämään, onko kaikissa mahdollisissa ratkaisussa jokin muuttuja 1 tai 0 - jos on, niin se on ainoa mahdollinen ratkaisu.

- [ ] to-do: Saavutetut aika- ja tilavaativuudet (esim. O-analyysit pseudokoodista)
- [ ] to-do: Suorituskyky- ja O-analyysivertailu (mikäli sopii työn aiheeseen)

<h2>Työn mahdolliset puutteet ja parannusehdotukset</h2>

HUOM! Parannusehdotus itselleni: mahdollisesti, nyt kun olen saanut `self.front`:in `botGame.py`:ssä päivittymään aina oikein (sekä CSP:tä käytettäessä että ilman), teen seuraavaksi merkittävän yksinkertaistuksen niin, että rupean `self.variable_to_equations`:ia hyväksi käyttäen `CSP_solver.py`:ssä brute-forcaamaan ratkaisuehdotuksia ryppäässä yhtälöitä, jonka kaikki yhtälöt jakavat yhteisen muuttujan (kyseisen muuttujan sisältävät yhtälöt kun siis saadaan `self.variable_to_equations`-sanakirjasta tehokkaasti ja kätevästi, sen avaimina kun ovat muuttujat itse ja arvoina tämän muuttujan sisältävät yhtälöt)
<h2> Laajojen kielimallien (ChatGPT yms.) käyttö. </h2>
<em>Mainitse mitä mallia on käytetty ja miten. Mainitse myös mikäli et ole käyttänyt. Tämä on tärkeää! </em>

- Itse botin kehityksessä en ole kertaakaan käyttänyt tekoälyä.
- `botGame.py`:ssä eli miinaharavassa (johon botti on integroituna) kysyin ChatGPT:ltä
  - miten saadaan alfa-arvo highlighteihin, ja
  - kysyin mapin yllä olevan infoboksin lisäämisen jälkeen debuggaukseen y-koordinaattien suhteen apua ChatGPT:ltä, josta sain `cell_y = (mouse_y - self.infobar_height) // self.cell_size              # Like explained in the above comment. Implementation here: adjust for the infobar by 'raising' the click by infobar height, then get the row number by division by self.scale. Asked from ChatGPT when trying to find the problem with the y-location` -ratkaisun. Nämä eivät liity siis bottiin, vaan itse miinaharavapelin toteutukseen.

<h2>aiempia huomautuksia</h2>

huom.0: monesti riittää pelkkä ympäröivän 8 ruudun tarkastelu, mutta joskus taas ei - tällöin otetaan käyttöön tietoa ympäröivien ruutujen miinaluvuista, ja tämä voi mennä hyvinkin monimutkaiseksi, kuten voi itselleen todistaa täällä https://minesweeper.online/game/3720717509 (no guessing mode, mappi 'evil')
huom.1: jos botti ei ole siis osunut miinaan, JOS päästään siihen vaiheeseen tämän algoritmin kehittämisessä, että kaikki mahdollinen logiikka on ratkaistu ja voidaan seuraavaksi alkaa tehdä myös fiksuja arvauksia pakon osuessa (mieluiten käyttäen ehdollisia todennäköisyyksiä), eli JOS ehditään siihen vaiheeseen tässä projektissa, että ollaan jo tehokkaasti ratkaistu kaikki 'pelkällä logiikalla' ratkaistavissa olevat tilanteet, mukaan lukien käyttäen tietoa jäljelläolevien miinojen lukumääristä ja viereisten ruutujen lukuarvoista.


<h2>Viitteet</h2>
to-do: Becerran kandityö
