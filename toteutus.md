- [ ] to-do: Ohjelman yleisrakenne
<h2> Ohjelman yleisrakenne </h2>
Ensinnäkin, tehdään graafinen käyttis esim. PyGameä käyttäen, jotta nähdään mitä botti tekee. Ennen kutakin siirtoa, 

1. merkataan "turvalliset ruudut" (eli ruudut joista voidaan päätellä että niissä varmasti ei ole miinaa) vihreällä, 
2. merkataan miinat lipulla kuten oikeassakin miinaharavassa voidaan tehdä. (Jos lähdetään saivartelemaan, voidaan todeta, että optimaalisessa pelityylissä miinaharavassa merkataan vain osa lipuista ja chordataan; kaikkien
3. avataan turvalliset ruudut RIIPPUMATTA SIITÄ, olisiko tämä oikeassa pelissä chordaus vai ei (pelityylin tehokkuudesta voidaan ruveta murehtimaan, jos saadaan varsinainen logiikka ensin toimimaan todistetusti eli hyvin testatusti kaikissa tapauksissa )
4. siirrytään seuraavaan ruutuun, jossa ei ole oltu vielä
5. jos on käyty läpi ruudut, eikä pelkillä ruudun itsensä näyttämällä numerolla voida päätellä viereisistä ruuduista mitään, siirrytään monimutkaisempaan logiikkaan, jossa merkataan, montako miinaa kussakin ympäröivässä blokissa on (esim. 3 ruutua, joista tiedetään, että niistä kahdessa on pakko olla, jne). TÄMÄ ON VAIKEIN OSUUS KOKO BOTISSA.

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

