<h2>Miten ohjelma suoritetaan</h2>

**botGame.py**:
Täällä asuu itse miinaharavapeli, ja siihen integroidun bottilogiikan tapahtumaketju `bot_execute()` jossa siis määritellään, mitä botti tekee ja missä järjestyksessä.

Tämän **botGame.py**:n ajaminen aloittaa miinaharavapelin, jonka alalaidassa on ohjeet, mitä tässä avatussa pelissä voi tehdä (btw: voit myös klikata, eli pelata kuten ihan oikeaa miinaharavaa!)
Tiedoston **botGame.py** alalaidassa voit valita, minkälaisen mapin haluat: expert, beginner, intermediate, jne jne.. Valmiina on siis kirjoitettu pelimuotojen `beginner`, `intermediate` ja `expert` leveydet, korkeudet, ja miinat.

Esim.

```python
Minesweeper(expert, classic=True, csp_on=True,
    minecount_demo_number=None, logic_testing_on=False, unnecessary_guesses=False)
```
on ihan 'tavallinen' tapa ajaa kyseinen peli: tällöin alkaa expert-mappi, ja ohjeet näkyvät sen alalaidassa.

Tässä voit painaa `b`-näppäintä botin ajamiseksi; tähän `botGame.py`:hyn on siis integroitu <i>valinnaisena</i> osiona botti `CSP_solver.py`:n luokasta `CSP_solver` (eli integroituna peliin on halutessaan käytettävissä oleva "tekoäly" jos sitä siksi haluaa perinteisesti nimittää; huom! Tässä työssä kuitenkaan <b>ei</b> käytetä mitään adaptiivista koneoppimista, neuroverkkoja tai sen sellaista, eli <b>ei</b> käytetä oikeaa tekoälyä; botti tasan 'oppii' mitä se kussakin mapissa näkee, ja unohtaa kaiken oppimansa uuden pelin aloittaessa; se siis pelaa samoin kun ihminenkin (paitsi että toisinaan vähän puutteellisesti tällä hetkellä ainakin))

`CSP_solver.py`

Tämän ajaminen ajaa `CSP_solver`-luokkaa testaavat 'yksikkötestit', jotka kaikki koostuvat seuraavasta: (1) syötetään yhtälöitä luotuun `CSP_solver`-luokkaan, (2) yritetään ratkaista niin paljon kuin voidaan, joko yhdellä tai useammalla rundilla, (3) tarkistetaan ja tulostetaan tulokset; mukaan lukien, mitä odotettiin, ja mitä saatiin, ja menikö testi läpi.

<h2> Miten eri toiminnallisuuksia käytetään </h2>

**botGame.py**:

Vaihda pelimoodia tämän tiedoston alalaidasta (`if __name__ == __main__`-osasto). Käynnistä peli ajamalla itse koodi (joka siis on alaosassa osiossa `if __name__ == __main__`)

- jos painat `x`- tai `n`-näppäintä, pelaat botilla, eli käytät sitä algoritmistoa, joka tämän algoritmikurssin varsinainen aihe oli
- mapin loppuun asti automaattisesti pelaaminen: paina 'a' (automatic). Jos haluat keskeyttää, paina `a`; tämä suorittaa nykyisen komennon loppuun ja sitten EI jatka eteenpäin botin logiikassa.
- loputon pelaaminen: paina `i` (infinite) ja `a` (automatic). Kun haluat lopettaa, paina uudestaan `i`
- jos painat `v`, niin togglaat `a`:sta x fps-version päälle, eli hitaamman, jonka nopeutta rajoittaa (alarajan kunkin `bot_execute()`-kierroksen kestolle asettaa) käytössä oleva fps, jota voi muuttaa **botGame.py**:ssä ctrl-f:äämällä 'tick(' (joka tällä hetkellä taitaa olla 200, eli 200 fps/sekunti)
- hiiren vasemmalla avataan ruutu
- hiiren oikealla merkataan lippu
- jos ruudun $x$, esim. olkoon tämä $x=2$ eli ruutu jossa näkyy vihreä numero 2, ympärille olet laittanut 2 lippua (tasan 2), niin vasemmalla klikatessasi tätä kakkosta, avaat kaikki kakkosen ympärillä olevat ruudut, oli niissä sitten miinaa/miinoja tai ei. Tätä kutsutaan englanniksi nimellä `chording`, ja nimen alkuperä on se, että siinä avataan monta yhdellä painalluksella, ikään kuin muka soittaisi soinnun jollain instrumentilla, tsiisus khraist mikä nimi... eli monta yhdellä, 'chord', sointu. Tämä sitten vissiin olisi se 'harava' joka osuu miinaan ja antaa luvan kävellä sen välittömässä ympäristössä (tämä ei välttämättä päde oikeassa elämässä oikealla miinakentällä)
- `space` aloitaa uuden pelin
- `f` näyttää `self.front`:in keltaisena. Kannattaa kokeilla! Oli todella hyödyllinen tätä tehdessä, mukaan lukien (etenkin) debuggatessa
- `c` highlightaa kaikki `CSP_solver`:in ratkaisemat ruudut; vihreällä ne, joissa tämän solverin laskujen mukaan ei ole miinaa, ja punaisella ne, joissa on miinat
- `m` näyttää todelliset, ihka oikeat miinojen sijainnit, eli ne, jotka kenttään arvottiin ekan klikkauksen/b-painalluksen jälkeen. Tätä tietoa tietenkään EI ole oikeassa miinaharavassa pelaajan käytössä
- `g` näyttää arvatut ruudut: viimeisin arvaus on kultaisen värinen, muut ovat sinisiä. Hyvin kätsää!
- `h` näyttää kaikki minecount-logiikan ratkaisemat ruudut; vihreitä (ei miina) ja/tai punaisia (miina)
- peli (`botGame.py`) muistaa valintasi ennen kuin resettaat poistumalla (painamalla `q`-näppäintä tai ruksia oikeassa yläkulmassa); siis highlighttaukset ja miinojen sijainnit, eli ei tarvitse painaa joka kerta uudestaan esim. `f`:ää, jos haluaa useamman peräkkäisen pelin aikana seurata `self.front`:in edistymistä pelatessa botilla (`b-näppäimellä`)

Kun ajat koodin `botGame.py`:ssä, niin peli alkaa. Ohjeet ovat pelin alapalkissa (q lopettaa, b pelaa botilla (joka käyttää `simple_solver()`:ia ja `CSP_solver`-luokkaa))

<h3>"botin" käyttäminen: Mitä x-, n- tai a-painallus siis tekee</h3>

x- tai n-painallus ajaa <b>yhden</b> rundin `simple_solver()`:ia, ja jos `csp_on == True` niinkuin se defaulttina on, niin samalla yhden rundin `csp_solve()`:a
  
  - jos siis haluat ajaa <b>monta</b> rundia tekoälyä, paina toistuvasti peräkkäin x- tai n-näppäintä! Ja jos haluat automaattisen pelimuodon, niin a tai i + a tai v + a tai v + i + a
  - kaikkea voi kokeilla, mistään ei pitäisi aiheutua kaatumisia. Fingers crossed

Tämä `x`-tai `n`-painallus aloittaa ensin pelin vasemmasta ylänurkasta - siis 'klikkaa' vasenta ylänurkkaa ihan normaalisti. Miinaharava, siis myöskin tekemäni `botGame.py` (joka edelleenkin ajetaan ajamalla kyseinen python-tiedosto `botGame.py`), toimii niin, että ensimmäinen klikkaus ei koskaan osu miinaan; itseasiassa vasta tämän ensimmäisen klikkauksen (tai ensimmäisen x- tai n-painalluksen) jälkeen miinat sijoitellaan sattumanvaraisesti (`random.sample()`) kenttään mihin tahansa muualle kuin sinne, minne klikattiin. Tämä on ollut käytössä vuodesta 2007 (ja tätä aiemmin taas miina siirrettiin, jos olisi sattunut muuten osumaan miinaan ekalla klikkauksella)

- `space` aloittaa uuden pelin
- `q` lopettaa

<h2> miinaharavasta ja botista; mitä ihmettä tässä edes pitäisi katsoa tai tietää? </h2>

Ensinnäkin, onko taattua, että mappi (kenttä, eli se joka arvottiin ekan klikkauksen/b-painalluksen jälkeen) on ratkaistavissa logiikalla? **EI**. Ei siis ole mitenkään taattua, edes `beginner`-muodossa, että sinä, tai botti, pystyvät ratkaisemaan mappia puhtaalla logiikalla. Joskus on siis pakko arvata!

Miten päätellään: <a>https://minesweeper.online/help/patterns<a/>

Miten voit varmistaa, että itse peli toimii? Alussa arvotut miinat ovat kiveen kirjoitettu (siis ekan klikkauksen/ekan b-painalluksen jälkeen). Kun painat `m`-näppäintä, saat juuri nämä näkyviin, eli kaikki TODELLISET miinojen sijainnit näkyvät punaisella. Tämä on helppo tapa todistaa, että ne säilyvät alusta loppuun asti samoissa ruuduissa, eikä outouksia tapahdu, ja että numerot ovat, mitä odottaisitkin.

Huom! Jos osut miinaan ja painat `b`-näppäintä, botti ei osaa tulkita tätä häviön jälkeen jatkamista oikein, vaan rupeaa laskeskelemaan omiaan (johtuu laskutavasta, joka ei ota huomioon häviön jälkeisiä asioita oikein). Älä siis luota siihen, mitä tapahtuu häviön jälkeen, jos käytät bottia (eli jos pelaat b-näppäintä rämpyttämällä)!

Koko pelin idea on, että ainoastaan tarkastelemalla avattujen ruutujen numeroita, jotka siis kertovat, montako miinaa yhteensä ympäriltä löytyy (yleensä siis ympäröivästä 8 ruudusta, keskellä, 3 ruudusta nurkissa, 5 ruudusta muualla) voidaan useimmissa tapauksissa päätellä, missä miinoja on (laita lippu) tai ei ole (klikkaa vasemmalla).

HUOM! Aloitus on yleensä riskialttein. Tekemäni toteutus ei takaa 'alkupläjäytystä' eli sitä että alkuklikkausta ympäröivissä ruuduissa ei ole miinoja. Tämä alkupläjäytys on olemassa alkuperäisessä miinaharavassa (ja toisaalta puuttuu esim. minesweeper.online:sta), ja jätin sen itse toteuttamatta, koska olen tottunut minesweeper.onlineen.

Paras strategia on klikata aluksi kulmaa, koska tässä on suurin todennäköisyys siihen, että kaikki naapurit ovat nollia, mikä aiheuttaa juurikin kuvatunlaisen 'alkupläjäytyksen', joka on ratkaisemisen kannalta alussa positiivista.

Jos pelaat `expert`-pelimuotoa (se on defaulttina menossa; esim. vaihda pelimuoto `beginner`:iksi `botGame.py`:n alalaidasta vaihtamalla kaikki `expert`-sanat `Minesweeper(...)`:ssä `beginner`-sanoiksi; se selittää itsensä ihan hyvin kyllä runsaiden kommenttieni ansiosta siellä c:), niin todennäköisin aloitus nurkasta on se, että saat näkyviin sinisen numeron "1". Voiko tästä päätellä mitään? Ei. Paras jatko tälle on kokeilla toista nurkkaa (kokeile nurkkia niin kauan kuin riittää, jos et pysty päättelemään missä miinat ovat).


<h2>Minkä muotoisia syötteitä ohjelma hyväksyy</h2>

Esimerkit näkyvät tiedostojen `botGame.py` ja `CSP_solver.py` alalaidoissa, `if __name__ == __main__`-osioissa. Ja kuten huomaat, selittäviä kommentteja löytyy!
