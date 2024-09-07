- [ ] to-do: Ohjelman yleisrakenne
<h2> Ohjelman yleisrakenne </h2>
Ensinnäkin, tehdään graafinen käyttis esim. PyGameä käyttäen, jotta nähdään mitä botti kussakin ratkaisuvaiheessa tekee. 

Visuaaleissa, kuten itse koodissakin, botti etenee mappia ruutu kerrallaan ja katsoo kulloinkin ympärillä olevaa kahdeksaa (8) ruutua (*alahuomautus 0). 

Botin ollessa kussakin ruudussa (*alahuomautus 1) 

1. merkataan nykyistä ruutua ympäröivistä kahdeksasta ruudusta "turvalliset ruudut" (eli ruudut joista voidaan päätellä että niissä varmasti ei ole miinaa) vihreällä visualisoinnin vuoksi, 
2. merkataan miinat (ne ympäröivät ruudut joissa voidaan päätellä olevan miina) lipulla kuten oikeassakin miinaharavassa *voidaan* tehdä. (*alahuomautus 2) 
3. avataan turvalliset ruudut, eli ne vihreäksi merkatut (pelityylin tehokkuudesta tässä vaiheessa voidaan ruveta murehtimaan, jos saadaan varsinainen logiikka ensin toimimaan todistetusti eli hyvin testatusti kaikissa tapauksissa). Tässä vaiheessa 0-putki aukeaa automaattisesti kuten oikeassakin miinaharavassa, eli jos klikataan 0-ruutua, niin ympäröivät 0t aukeavat automaattisesti.
4.
  - a) siirrytään seuraavaan ruutuun, jossa ei ole oltu vielä TAI
  - b) jos on käyty läpi ruudut pelkällä yhden ruudun logiikalla eikä tämä riittänyt ratkaisemaan tietä eteenpäin, käydään seuraavaksi etulinjan ruutuja läpi monimutkaisemmalla logiikalla käyttäen tietoa viereisten etulinjan ruutujen lukuarvoista (0-8): mm. merkataan, montako miinaa kussakin ympäröivässä blokissa on (esim. 3 ruutua, joista tiedetään, että niistä kahdessa on pakko olla, jne). TÄMÄ ON YLIVOIMAISESTI VAIKEIN OSUUS KOKO ALGORITMISSA, ja vaatii oman osuutensa.

<ol> 
  <li>
    Generoidaan mappi, $r$ riviä ja $s$ saraketta jossa $m$ miinaa. Tämä on siis 'matriisi' jossa jokaisen solun arvo on miina, tai lukumäärä ympäröivässä 8 ruudussa olevien miinojen lukumäärästä.
    <ul>
      <li> mappeja, jotka ovat ratkaistavissa ilman arvauksia (tuuria), jos aloitetaan tietystä ruudusta </li>
        - tässä mallina käteviä ovat https://minesweeper.online/game/3720671312 täältä löytyvät No guessing mode - Easy -pelit; ainakin aluksi pitäydytään beginner-kokoisissa mapeissa
      <li> mappeja, jotka eivät ole ratkaistavissa ilman arvauksia, jos aloitetaan tietystä ruudusta </li>
    </ul>
  </li>
  <li>
    laitetaan botti ratkaisemaan kyseinen mappi
    <ul> 
      <li> jos botti osaa ratkaista, tästä selkeä viesti (visuaalinen interface) </li>
    </ul>
  </li>
</ol>

- [ ] to-do: Saavutetut aika- ja tilavaativuudet (esim. O-analyysit pseudokoodista)
- [ ] to-do: Suorituskyky- ja O-analyysivertailu (mikäli sopii työn aiheeseen)
- [ ] to-do: Työn mahdolliset puutteet ja parannusehdotukset
- [ ] to-do: Laajojen kielimallien (ChatGPT yms.) käyttö. Mainitse mitä mallia on käytetty ja miten. Mainitse myös mikäli et ole käyttänyt. Tämä on tärkeää!
- [ ] to-do: Viitteet

huom.0: monesti riittää pelkkä ympäröivän 8 ruudun tarkastelu, mutta joskus taas ei - tällöin otetaan käyttöön tietoa ympäröivien ruutujen miinaluvuista, ja tämä voi mennä hyvinkin monimutkaiseksi, kuten voi itselleen todistaa täällä https://minesweeper.online/game/3720717509 (no guessing mode, mappi 'evil')
huom.1: jos botti ei ole siis osunut miinaan, JOS päästään siihen vaiheeseen tämän algoritmin kehittämisessä, että kaikki mahdollinen logiikka on ratkaistu ja voidaan seuraavaksi alkaa tehdä myös fiksuja arvauksia pakon osuessa (mieluiten käyttäen ehdollisia todennäköisyyksiä), eli JOS ehditään siihen vaiheeseen tässä projektissa, että ollaan jo tehokkaasti ratkaistu kaikki 'pelkällä logiikalla' ratkaistavissa olevat tilanteet, mukaan lukien käyttäen tietoa jäljelläolevien miinojen lukumääristä ja viereisten ruutujen lukuarvoista.
huom.2: pilkunviilaajien kunniaksi todetaan tässä, että optimaalisessa pelityylissä miinaharavassa merkataan vain osa lipuista ja chordataan (useiten 1:tä klikkaamalla, joskus myös 2:ta, ja hyvin harvoin isompia); kaikkien miinojen liputtaminen ei ole optimaalista nopeuden ja/tai 'eficciencyn' (kokonaisklikkausten minimoimisen) kannalta, koska chordaus on olemassa ja mahdollistaa yli "100%" tehokkuuden verrattuna minimiklikkausmäärään (jolloin efficiency on 100%) liputta pelatessa JOS tiedetään etukäteen, missä miinat ovat (100%:n tehokkuuden saavuttaminen ilman etukäteistietoa joka ikisen lipun tarkasta sijainnista on hyvin epätodennäköistä etenkin isommilla mapeilla))
