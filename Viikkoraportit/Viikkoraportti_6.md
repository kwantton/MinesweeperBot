## sanasto
- 'minecount'-tilanne: tilanne, jossa ei pystytä ratkaisemaan uusia muuttujia (arvo 0 tai 1 muuttujalle) 100% varmuudella yhdellekään muuttujalle (AINAKAAN) ILMAN, että otetaan huomioon lisäksi se, kuinka monta miinaa kyseisellä hetkellä jäljellä olevassa mapissa vielä on. Tämän 'minecountin' avulla saadaan tapaustarkastelu, joka tehdään `use_minecount()`:issa
- self.front (front=ratkaisemattomuuden rintama tässä kontekstissa): `botGame.py`:ssä etulinjan numeroruudut, sellaiset, jotka kertovat jotain hyödyllistä loppumapin ratkaisun kannalta.
- käytännössä tarkoitan 'front':eilla tämän self.frontin (tai sen erillisten osien) näkemiä klikkaamattomia ruutuja
- erilliset frontit: erilliset yhtälöjoukot. Kussakin erillisessä yhtälöjoukossa jokaisella yhtälöllä on keskenään vähintään yksi muuttuja suoraan tai epäsuorasti muiden kyseisen joukon yhtälöiden kanssa yhteistä. Eli 'eriytä frontit' tarkoittaa: jaa tällä hetkellä minecount-tilanteita varten yhdistetyt frontit taas erilleen, jotta aikavaativuus laskee

## Tehty tällä viikolla

6.10.2024 ~19.30: MINECOUNT TOIMII NYT KAIKISSA TILANTEISSA.
- Kaikki mahdollinen logiikka (logiikka = ei arvaukset, koska täydellisiä arvauksia ei ole edes mahdollista laskea kohtuullisessa ajassa; ei voida tehdä miinaharavamapista shakkimappia ja ottaa huomioon joka ikistä mahdollista tulosta (mitä numeroita missäkin, mitä miinoja missäkin) koko pelin kaikkien mahdollisten lopputulosten loppuun asti) toimii tällä hetkellä ja kaikki nykyiset testit menevät läpi! Olen testannut muutaman sataa (13.10.) expert-peliä ja beginner-peliä, eikä ongelmia ole.
- seuraavaksi testejä, siivoamista jne

13.10.2024
- Arvauksia tehdään; käytetään hyväksi `CSP_solver`:in `handle_possible_whole_solutions()`:ia.
- `n_unclicked` laskenta `botGame.py`:ssä oikein ja sitä mukaa kun peli edistyy; on sekä fiksumpi (mikro-optimointia) että erittäin hyvä debuggaustyökalu (tällä hetkellä toimii; siis `n_unclicked`:in luku on oikein kaikissa tilanteissa)
- commitista muokattu ja päivitetty kuvaus: I had performed `self.handle_opening_a_new_cell()` in `botGame.py` previously for `self.solver.solved_variables` on every round coming back from `csp_solve()`, by accident. I noticed it, now it's `self.probe(x,y)` for every solved variable that's not in `self.solved_variables` in `botGame.py`. So, now there is `self.solved_variables` for BOTH `botGame.py` AND for `CSP_solver`; this reduces unnecessary calculations. Lukeutuu mikro-optimaatioihin mutta on selkeyden ja logiikan kannalta paljon parempi, ja mahdollistaa sen että `self.handle_opening_a_new_cell()` voi todellakin tehdä täsmälleen ja vain ja ainoastaan sen, minkä mukaan tämä funktio on nimetty. Siis paljon parempaa ohjelmointia kaiken kaikkiaan tältä osin
- arvaukset näkyvät kun painaa 'g' (g niinkuin guess) miinaharavapelissä. Arvausten todennäköisyydet näkyvät pelin ruudulla (suurin todennäköisyys frontin viereisistä ruuduista sille, että EI ole miinaa, ja tasajakautunut todennäköisyys kullekin unclicked unseen -ruudulle, että ei ole miinaa). Näkyy siis, miksi arvaus tehtiin sinne minne se tehtiin



## Miten edistynyt
Hyvin. Kriittisintä olisi eriyttää frontit minecount-tilanteita varten, etenkin kun nyt arvaukset tehdään minecount-tilanteiden tarkastelun pohjalta. Tämä siis parantaisi aikavaativuutta hyvin merkittävästi minecount- ja arvaustilanteissa. Tämän toteuttaminen tulee viemään useamman päivän, jotta sekä minecount että arvaukset saadaan muokattua tähän uuteen muotoon niin että ne varmasti toimivat.


## Mitä opin:
Varsinaista uutta mullistavaa 'ideaa' tällä viikolla ei ole tullut, paitsi se, että pitää eriyttää frontit minecount-tilanteita varten. Olin aiemmin tehnyt sen idealla 'no näin sen ainakin saa tehtyä' sen tarkemmin miettimättä, nyt saan sitten kärsiä sen ansiosta c:


## Epäselvää
ei tule mieleen, pitää eriyttää frontit (rintamat) minecount-tilanteita ja näiden pohjalta rakennettavia arvauksia varten ja väsätä sitten rutkasti testejä

## Seuraavaksi
- Ensin yritän siivota arvausosastoa
- Sitten, kriittisin asia aikavaativuuden kannalta (tämä ei ole aina ongelma, mutta toisinaan ylitsepääsemätön ongelma, eli sellainen jonka laskemiseen menee sekunteja...minuutteja...tunteja): eriytä minecount-tilanteet. Tämän saavuttamiseksi (mukaan lukien arvaukset, jotka elävät minecountin pohjalta) pitää muokata noin 200 riviä koodia.
