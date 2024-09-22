<h2>Miten ohjelma suoritetaan</h2>

`CSP_solver.py`:
Tämän ajaminen aloittaa miinaharava-pelin, jonka alalaidassa on ohjeet, mitä tässä avatussa pelissä voi tehdä (btw: voit myös klikata, eli pelata kuten ihan oikeaa miinaharavaa!)
Täällä alalaidassa voit valita, minkälaisen mapin haluat. Valmiina on kirjoitettu pelimuotojen `beginner`, `intermediate` ja `expert` leveydet, korkeudet, ja miinat.

- hiiren vasemmalla avataan ruutu
- hiiren oikealla merkataan lippu
- jos ruudun `x`, esim. olkoon tämä `x` nyt ruutu jossa näkyy vihreä numero 2, ympärille olet laittanut 2 lippua (tasan 2), niin vasemmalla klikatessasi tätä kakkosta, avaat kaikki kakkosen ympärillä olevat ruudut, oli niissä sitten miinaa/miinoja tai ei. Tätä kutsutaan englanniksi nimellä `chording`, ja nimen alkuperä on se, että siinä avataan monta yhdellä painalluksella, ikään kuin muka soittaisi soinnun jollain instrumentilla, tsiisus khraist mikä nimi...
- jos painat `b`-näppäintä, pelaat botilla, eli käytät sitä pikkuohjelmistoa, joka tämän algoritmikurssin varsinainen aihe oli
- `space` aloitaa uuden pelin
- `f` näyttää `self.front`:in keltaisena. Kannattaa kokeilla! Oli todella hyödyllinen tätä tehdessä, mukaan lukien (etenkin) debuggatessa.
- `c` highlightaa kaikki `CSP_solver`:in ratkaisemat ruudut; vihreällä ne, joissa tämän solverin laskujen mukaan ei ole miinaa, ja punaisella ne, joissa on miinat
- `m` näyttää todelliset, ihka oikeat miinojen sijainnit, eli ne, jotka kenttään arvottiin ekan klikkauksen/b-painalluksen jälkeen
- peli (`botGame.py`) muistaa valintasi ennen kuin resettaat poistumalla (painamalla `q`-näppäintä tai ruksia oikeassa yläkulmassa); siis highlighttaukset ja miinojen sijainnit, eli ei tarvitse painaa joka kerta uudestaan esim. `f`:ää, jos haluaa useamman peräkkäisen pelin aikana seurata `self.front`:in edistymistä pelatessa botilla (`b-näppäimellä`)

Kun ajat koodin `botGame.py`:ssä, niin peli alkaa. Ohjeet ovat pelin alapalkissa (q lopettaa, b pelaa botilla (joka käyttää `simple_solver()`:ia ja `CSP_solver`-luokkaa))

<h3>"TEKOÄLYN" käyttäminen: Mitä b-painallus siis tekee?</h3>
b-painallus ajaa <b>yhden</b> rundin `simple_solver()`:ia, ja jos `csp_on == True` niinkuin se defaulttina on, niin samalla yhden rundin `CSP_solver`:ia. 
  
  - jos siis haluat ajaa <b>monta</b> rundia tekoälyä, paina toistuvasti peräkkäin b-näppäintä!

Tämä `b`-painallus aloittaa ensin pelin vasemmasta ylänurkasta - siis 'klikkaa' vasenta ylänurkkaa ihan normaalisti. Miinaharava, siis myöskin tekemäni `botGame.py` (joka edelleenkin ajetaan ajamalla kyseinen python-tiedosto `botGame.py`), toimii niin, että ensimmäinen klikkaus ei koskaan osu miinaan; itseasiassa vasta tämän ensimmäisen klikkauksen (tai ensimmäisen b-painalluksen) jälkeen miinat sijoitellaan sattumanvaraisesti (`random.sample()`) kenttään mihin tahansa muualle kuin sinne, minne klikattiin.

Jos botti jää jumiin, sinulla on kaksi vaihtoehtoa:

  (1) klikkaa itse, eli arvaa
  (2) paina `space`:ä, mikä aloittaa uuden pelin (kuten kentän alalaidassa lukee)
  (3) voit myös painaa `q` ja luovuttaa. Tämä ei kuitenkaan aina toimi oikeassa elämässä.

- [ ] to-do: miten eri toiminnallisuuksia käytetään 
- [ ] to-do: Minkä muotoisia syötteitä ohjelma hyväksyy

<h2> miinaharavasta ja botista; mitä ihmettä tässä edes pitäisi katsoa tai tietää? </h2>

Ensinnäkin, onko taattua, että mappi (kenttä, eli se joka arvottiin ekan klikkauksen/b-painalluksen jälkeen) on ratkaistavissa logiikalla? **EI**. Ei siis ole mitenkään taattua, edes `beginner`-muodossa, että sinä, tai botti, pystyvät ratkaisemaan mappia puhtaalla logiikalla. Joskus on siis pakko arvata!

Miten voit varmistaa, että itse peli toimii? Alussa arvotut miinat ovat kiveen kirjoitettu. Kun painat `m`-näppäintä, kaikki TODELLISET miinojen sijainnit näkyvät punaisella. Tämä on helppo tapa todistaa, että ne säilyvät alusta loppuun asti samoissa ruuduissa, eikä outouksia tapahdu.

Huom! Jos osut miinaan ja painat `b`-näppäintä, botti ei osaa tulkita tätä häviön jälkeen jatkamista oikein, vaan rupeaa laskeskelemaan omiaan. Älä siis luota siihen, mitä tapahtuu häviön jälkeen!

Koko pelin idea on, että ainoastaan tarkastelemalla avattujen ruutujen numeroita, jotka siis kertovat, montako miinaa yhteensä ympäriltä löytyy (yleensä siis ympäröivästä 8 ruudusta, keskellä, 3 ruudusta nurkissa, 5 ruudusta muualla) voidaan useimmissa tapauksissa päätellä, missä miinoja on (laita lippu) tai ei ole (klikkaa vasemmalla).

HUOM! Aloitus on yleensä riskialttein. Tekemäni toteutus ei takaa 'alkupläjäytystä' eli sitä että alkuklikkausta ympäröivissä ruuduissa ei ole miinoja. Tämä alkupläjäytys on olemassa alkuperäisessä miinaharavassa (ja toisaalta puuttuu esim. minesweeper.online:sta), ja jätin sen itse toteuttamatta, koska olen tottunut minesweeper.onlineen.

Paras strategia on klikata aluksi kulmaa, koska tässä on suurin todennäköisyys siihen, että kaikki naapurit ovat nollia, mikä aiheuttaa juurikin kuvatunlaisen 'alkupläjäytyksen', joka on ratkaisemisen kannalta alussa positiivista.
