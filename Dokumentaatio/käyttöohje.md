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

Tässä voit painaa `x`-tai `n`-näppäintä botin yhden 'kierroksen' ajamiseksi, kuten pelin alaosan ohjeissa lukee; tähän `botGame.py`:hyn on siis integroitu botti **CSP_solver.py**:n luokasta `CSP_solver` (eli integroituna peliin on halutessaan käytettävissä oleva "tekoäly" jos sitä siksi haluaa perinteisesti nimittää. Tässä työssä kuitenkaan <b>ei</b> käytetä mitään adaptiivista koneoppimista, neuroverkkoja tai sen sellaista, eli <b>ei</b> käytetä oikeaa tekoälyä; botti ainoastaan 'näkee' kullakin hetkellä mitä pelaajakin näkee; se siis pelaa samoin kun ihminenkin)

**tests_for_CSP_solver.py**

Tämän ajaminen ajaa `CSP_solver`-luokkaa testaavat 'yksikkötestit', jotka kaikki koostuvat seuraavasta: (1) syötetään yhtälöitä luotuun `CSP_solver`-luokkaan, (2) ratkaistaan niin paljon muuttujia kuin voidaan, (3) tarkistetaan ja tulostetaan tulokset; mukaan lukien, mitä odotettiin, ja mitä saatiin, ja menikö testi läpi, ja kuinka monta testiä meni läpi, ja mitkä testit eivät menneet läpi.

**tests_for_CSP_solver_old.py**

Tämän ajaminen ajaa `CSP_solver`-luokkaa testaavat 'yksikkötestit', jotka kaikki koostuvat seuraavasta: (1) syötetään yhtälöitä luotuun `CSP_solver`-luokkaan, (2) ratkaistaan niin paljon muuttujia kuin saadaan (yhden tai useamman rundin aikana), (3) tarkistetaan ja tulostetaan tulokset; mukaan lukien, mitä odotettiin, ja mitä saatiin, ja menikö testi läpi. Tässä testiluokassa _ei_ ole yhteenvetoa siitä, moniko testeistä meni läpi ja moniko ei, ja kuten sinne on kirjoitettu, viimeinen testi joskus ratkaisee kaikki muuttujat, joskus osan, joskus ei mitään, mikä johtuu joukkojen (`set()`) iteraatiojärjestyksen vaihtelevuudesta. Tämä 'vanha' versio onkin ainoastaan nopea ratkaisuapuri, joka suoritetaan ennen uutta `CSP_solver`:ia, eikä tämän vanhan version ole tarkoituskaan osata kaikkea (huom. olisihan se siis hyvin mukava jos osaisi, mutta ei osaa, toisin kuin uusi `CSP_solver`).

<h2> Miten eri toiminnallisuuksia käytetään </h2>

**botGame.py**:

Voit vaihtaa pelimoodia, laittaa testimoodin päälle, jne, muuttamalla parametreja tiedoston alalaidassa `if __name__ == __main__`-osastossa `Minesweeper()`-komennossa:

- `expert` oletusarvoisesti (30x16, 99 miinaa)
- `classic=True` oletusarvoisesti eli 'klassinen' miinaharava, jossa aloitusruutu on 0....8
- `csp_on=True` oletusarvoisesti eli sekä vanha että uusi `CSP_solver` ovat käytössä, mukaanlukien uuden `CSP_solver`:in sisään leivotut arvauksentunnistussysteemit jotka saavat aikaan arvaukset jos muuttujia ei saada 
- `minecount_demo_number=None` oletusarvoisesti, eli ei demoa 'minecount'-tilanteista (numerot 1-3 demoavat),
ratkaistua - jos tämä on `False`, on käytännössä mahdollista voittaa vain osa beginner-kentistä, koska muuhun logiikka ei riitä
tämän tiedoston alalaidasta (`if __name__ == __main__`-osasto). Peli käynnistetään ajamalla itse koodi (joka siis on alaosassa osiossa `if __name__ == __main__`)
- `logic_testing_on=False` oletusarvoisesti; kun `True`, käytössä on **constraint_problem_solver_for_testing.py**:n `check_if_solutions_were_missed_in_lost_game()`. Katso lisää [testausmanuaalista](../Testing/Logic_validity_testing/Testing_manual.pdf)
- `unnecessary_guesses=False` oletusarvoisesti. Kuten kirjoitan **botGame.py**:ssä: normaalisti arvataan vain, kun ratkaisuja ei tapahdu. Kuitenkin "when 'self.unnecessary_guesses = True', it guesses anyways, 
even if it already found answers in CSP_solver_old or CSP_solver (sidenote: simple_solver will loop as long as it produces solutions, so if it DOES provide solutions, it will return and not go here ever -> no guesses will commence)". Tämän avulla voidaan _testata testaajaa_: kun `unnecessary_guesses=True`, voi nähdä, kuinka laskuri nousee aina, kun peli hävitään turhalla arvauksella

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

Huom! Jos osut miinaan ja painat sen _jälkeen_ `x`-tai `n`-näppäintä, botti ei osaa tulkita tätä häviön jälkeen jatkamista oikein, vaan rupeaa laskeskelemaan omiaan (johtuu laskutavasta, joka ei ota huomioon häviön jälkeisiä asioita oikein, koska miina-identiteetti on mysteeri botille). Älä siis luota siihen, mitä tapahtuu häviön jälkeen, jos käytät bottia (eli jos pelaat `x`-tai `n`-näppäintä rämpyttämällä)!

Koko pelin idea on, että ainoastaan tarkastelemalla avattujen ruutujen numeroita, jotka siis kertovat, montako miinaa yhteensä ympäriltä löytyy (yleensä siis ympäröivästä 8 ruudusta, keskellä, 3 ruudusta nurkissa, 5 ruudusta muualla) voidaan useimmissa tapauksissa päätellä, missä miinoja on (laita lippu) tai ei ole (klikkaa vasemmalla).

HUOM! Aloitus on yleensä riskialttein. Tekemäni toteutus ei takaa 'alkupläjäytystä' eli sitä että alkuklikkausta ympäröivissä ruuduissa ei ole miinoja. Tämä alkupläjäytys on olemassa "modernissa" miinaharavassa (ja toisaalta puuttuu esim. alkuperäisistä miinaharavatoteutuksista ja minesweeper.online:sta). Modernin version saa päälle kun laittaa `classic=False`, joka on defaulttina `True`.

Paras strategia on klikata aluksi kulmaa, koska tässä on suurin todennäköisyys siihen, että kaikki naapurit ovat nollia, mikä aiheuttaa juurikin kuvatunlaisen 'alkupläjäytyksen', joka on ratkaisemisen kannalta alussa positiivista.

Jos pelaat `expert`-pelimuotoa (se on defaulttina menossa; esim. vaihda pelimuoto `beginner`:iksi `botGame.py`:n alalaidasta vaihtamalla kaikki `expert`-sanat `Minesweeper(...)`:ssä `beginner`-sanoiksi; se selittää itsensä ihan hyvin kyllä runsaiden kommenttieni ansiosta siellä c:), niin todennäköisin aloitus nurkasta on se, että saat näkyviin sinisen numeron "1". Voiko tästä päätellä mitään? Ei. Paras jatko tälle on kokeilla toista nurkkaa (kokeile nurkkia niin kauan kuin riittää, jos et pysty päättelemään missä miinat ovat).

<h2>Minkä muotoisia syötteitä ohjelma hyväksyy</h2>

Esimerkit näkyvät tiedostojen **botGame.py**:n `if __name__ == __main__`-osiossa. Selittäviä kommentteja löytyy sen päältä!
