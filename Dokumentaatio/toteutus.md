- [ ] to-do: Ohjelman yleisrakenne

<h2> Ohjelman yleisrakenne </h2>

Graafinen käyttöliittymä on toteutettu `pygame`:ä käyttäen.

Botti aloittaa vasemmasta yläkulmasta, ja etenee `self.front`:ia, jota se tällä hetkellä (5.10.24) onnistuneesti ylläpitää (poistaa `self.front`:ista joka kierroksen jälkeen ruudut, jotka eivät tarjoa enää informaatiota jota voidaan hyödyntää ratkaisun kannalta, ja lisää `self.front`:iin sellaiset avatut ruudut, jotka tarjoavat informaatiota. Tämän 'hyödyllisyyden' määritelmä on yksinkertaisesti se, onko kyseisen avatun ruudun ympärillä enää avaamattomia ruutuja vai ei; jos on, ruutu on `self.front`:issa)

Tällä hetkellä CSP:tä hyödyntävä botti osaa ratkaista kaikki tapaukset paitsi ne minecount-tilanteet, joissa miinoja on jäljellä mapissa 11 tai enemmän (koska nykyinen minecount-ratkaisija on hidas ja raskas)

- [ ] to-do: Saavutetut aika- ja tilavaativuudet (esim. O-analyysit pseudokoodista)
- [ ] to-do: Suorituskyky- ja O-analyysivertailu (mikäli sopii työn aiheeseen)

<h2>Työn mahdolliset puutteet ja parannusehdotukset</h2>

Päädyin tekemään ratkaisijan `CSP_solver` pitkälti uudestaan seuraavasti:

Ensin haetaan kaikki mahdolliset ratkaisukombinaatiot kullekin yksittäiselle yhtälölle (esim. a+b=1; a=1 ja b=0 tai a=0 ja b=1). Kukin yhtälö on miinaharavamapin avattu numeroruutu, joka kertoo, montako miinaa ympäriltä yhteensä löytyy. Kukin muuttuja on miinojen lukumäärä kyseisessä ruudussa (eli 0 tai 1 jokaiselle muuttujalle). Tämä tehdään `itertools.combinations()`:illä. Näiden lukumäärä on ( n k ) missä n on avattua numeroruutua ympäröivien avaamattomien ruutujen lukumäärä ja k on tämän avatun numeroruudun numero; esim. jos on avattu ruutu 2, jonka ympärillä on siis 2 miinaa, niin jos tämän kakkosen ympärillä on vaikka 4 avaamatonta ruutua jäljellä, niin mahdollisia ratkaisukombinaatioita on tällöin ( 4 2 ) = 6 kappaletta.
    
Nyt on siis saatu kaikki mahdolliset ratkaisut jokaiselle alkuperäiselle miinaharavamapin yhtälölle. Kutsun kutakin vaihtoehtoista ratkaisua per yhtälö 'alt':iksi (alt = alternative = vaihtoehtoinen). Kunkin yhtälön alttien joukkoa kutsutaan nyt ryhmäksi. Seuraavaksi valitaan mielivaltainen aloitusryhmä (eli mapin yhtälön mahdolliset alt-ratkaisut), ja tämän aloitusryhmän kukin alt paritetaan yhden, mielivaltaisen toisen ryhmän jokaisen altin kanssa, JOS ne ovat yhteensopivia eli jos niissä ei ole eri arvoja (toisessa 1, toisessa 0) samalle muuttujalle. Tässä saadaan siis parissa karsittua pois ne, jotka eivät ole keskenään sopivia: esim. a=1, b=0 ja b=0, c=1 ovat yhteensopiva alt-pari yhtälöistä a+b=1 ja b+c=1, kun taas a=1, b=0 ja b=1, c=0 eivät ole yhteensopiva pari.

Tätä parittamista jatketaan toisesta ryhmästä kolmanteen ryhmään (jälleen kerran kaikki yhteensopivat altit kaikkien yhteensopivien kanssa), sitten kolmannesta neljänteen, jne.
    
Parittamisten jälkeen on niin monta vaihtoehtoista ratkaisupuuta, kuin montako alttia oli aloitusryhmässä. Jos esim. aloitusryhmä oli a+b=1, niin on 2 ratkaisupuuta. Sen juurena on aloitusryhmän alt, jonka lapsina ovat kaikki siihen yhteensopivat 2. ryhmän altit, jonka lapsina ovat kaikki 3. ryhmän 2. ryhmään yhteensopivat altit, jne.

Tätä puuta käydään läpi niin, että pidetään syntyvästä ratkaisusta kirjaa. Heti jos huomataan, että esim. aloitusryhmän altissa on a=1, mutta esim. jo 3. ryhmässä onkin a=0, niin koko haara hylätään eikä sitä enää käsitellä.

Lopulta on joku rypäs mahdollisia ratkaisuja, jotka toteuttavat samaan aikaan kaikki yhtälöt. Jos näitä on vaikka 5 mahdollista, käydään kustakin 5 ratkaisuehdotuksesta läpi jokainen muuttuja. Jos muuttuja, esim. a, on aina 1 kaikissa 5 vaihtoehtoisessa mahdollisessa ratkaisussa, on sen oltava 5 (koska mitään muuta mahdollista ratkaisua ei ole, joka kykenee toteuttamaan täsmälleen yhden vaihtoehtoisen altin kustakin ryhmästä)

<h2> Laajojen kielimallien (ChatGPT yms.) käyttö. </h2>
<em>Mainitse mitä mallia on käytetty ja miten. Mainitse myös mikäli et ole käyttänyt. Tämä on tärkeää! </em>

- Itse botin kehityksessä en ole kertaakaan käyttänyt tekoälyä.
- `botGame.py`:ssä eli miinaharavassa (johon botti on integroituna) kysyin ChatGPT:ltä
  - miten saadaan alfa-arvo highlighteihin, ja
  - kysyin mapin yllä olevan infoboksin lisäämisen jälkeen debuggaukseen y-koordinaattien suhteen apua ChatGPT:ltä, josta sain `cell_y = (mouse_y - self.infobar_height) // self.cell_size              # Like explained in the above comment. Implementation here: adjust for the infobar by 'raising' the click by infobar height, then get the row number by division by self.scale. Asked from ChatGPT when trying to find the problem with the y-location` -ratkaisun. Nämä eivät liity siis bottiin, vaan itse miinaharavapelin toteutukseen.

<h2>aiempia huomautuksia</h2>

- etenkin harvamiinaisissa kentissä (mapeissa) monesti riittää pelkkä ympäröivän 8 ruudun tarkastelu, mutta joskus taas ei - tällöin otetaan käyttöön tietoa ympäröivien ruutujen miinaluvuista, ja tämä voi mennä hyvinkin monimutkaiseksi, kuten voi itselleen todistaa täällä https://minesweeper.online/game/3720717509 (no guessing mode, mappi 'evil')
- optimaalisia arvauksia käsitellään JOS päästään siihen vaiheeseen tämän algoritmin kehittämisessä, että kaikki mahdollinen logiikka (mukaanlukien minecount kaikissa mahdollisissa tapauksissa, koosta riippumatta kunhan koko on realistinen (expert yläarajana)) on ratkaistu ja voidaan seuraavaksi alkaa tehdä myös fiksuja arvauksia pakon osuessa (mieluiten käyttäen ehdollisia todennäköisyyksiä), eli JOS ollaan jo tehokkaasti ratkaistu kaikki 'pelkällä logiikalla' ratkaistavissa olevat tilanteet, mukaan lukien käyttäen tietoa jäljelläolevien miinojen lukumääristä ja viereisten ruutujen lukuarvoista.


<h2>Viitteet</h2>
to-do: Becerran kandityö
