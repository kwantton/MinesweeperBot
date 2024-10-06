## Tehty tällä viikolla

UPDATE 6.10.2024 ~19.30: MINECOUNT TOIMII NYT KAIKISSA TILANTEISSA.
- Kaikki mahdollinen logiikka toimii tällä hetkellä ja kaikki nykyiset testit menevät läpi! Olen testannut muutaman kymmentä expert-peliä ja beginner-peliä, eikä ongelmia ole.
- seuraavaksi testejä, siivoamista jne
- allaoleva on siis tältä osin tällä hetkellä vanhentunutta tietoa

- `CSP_solver`:in kaksi isoa bugia korjattu:
  - väärä sisennys `handle_possible_whole_solutions()`:issa
  - `traverse()`:ssä käytetty `.copy()` jottei lapsi-`traverse()` päivitä virheellisesti vanhempien `traverse()`:jen arvoja. En todellakaan muistanut että Python toimii tällä tavalla, ja debuggausta varten piti piirtää excelissä tilakaavio, josta huomasin lopulta, että rekursiossa vanhempaan paluussa vanhemman arvot olivat muuttuneet tilanteesta, jossa lapsi-`traverse()`:ja oli kutsuttu. Oli hankala huomata! 
- `botGame.py`:ssä huomioidaan tilanne, jossa viimeiset avaamattomat ruudut jäävät boksiin lippujen taakse, eli `self_front`:in näkymättömiin; nyt jos miinoja on jäljellä nolla, kaikki avaamattomat ruudut avataan, eli tämäkin tilanne ratkeaa. Ei ollut aiemmin tullut vastaan, joten en ollut tajunnut huomioida tätä mahdollisuutta `botGame.py`:ssä
- minecount-tilanteen testi tehty `CSP_solver`:issa, ja tämä testi menee läpi
- nopeutettu `CSP_solver`:ia tekemällä `find_equation_groups()`, joka jakaa yhtälöt joukkoihin suoraan tai epäsuorasti yhteisten muuttujien perusteella -> `chain_link_equations()` ja seuraava `join_comp_groups_into_solutions()` jossa tarkastetaan `map`:ien avulla rakennetut alt-ratkaisupuut ovat nopeampia tämän ansiosta
- minecount-tilanteiden pikkuversio (hidas, raskas) on valmis; minecount-tilanteet, joissa miinoja mapissa on jäljellä enää 10 tai vähemmän, ratkeavat nyt `CSP_solver`:issa. Tämä on sen ansiota, että jos muuten jäädään jumiin (jos kaksi botin rundia peräkkäin ei saada enää uusia miinoja liputettua) lisätään mukaan yhtälö, jossa kaikki jäljelläolevat ruudut = jäljelläoleva miinamäärä. Tämän ansiosta tällä lisätiedolla ratkeavat tilanteet ratkeavat. Ongelmana on se, että jos mapissa on vaikka 30 avaamatonta ruutua jäljellä, ja 10 miinaa, niin ruvetaan väsäämään $\{30 \choose 10\}$-kombinaatioita kyseiselle yhtälölle. Ei kiva.
- KAIKKI TESTIT MENEVÄT LÄPI. Mukaanlukien 4 uutta testiä, jotka ovat joko ratkaisemattomissa olevia tilanteita (siis ilman arvauksia!) tai minecount-tilanteita


## Miten edistynyt

Erittäin hyvin. Fiksumpi, koon mukaan rajoittumaton minecount on tekemättä. Kun se on tehty, niin solver osaa ratkaista kaikki miinaharavan logiikkatapaukset.
  - tilanteesta 4/8 testiä läpi tilanteeseen 8/8, 9/9, 10/12, lopuksi 12/12
  - minecountin järkevämpi versio (vähemmän brut) tulossa
  - nopeampi `CSP_solver`, joka osaa jakaa yhtälöt erillisiin joukkoihin ja ratkaista ne ominaan. Tämä rajoittaa huomattavasti alt-ratkaisupuiden maksimikokoa, mikä on ollut (melko varmasti) nopeudessa pullonkaulana isoimmissa tilanteissa tähän mennessä

## Mitä opin:

- Pythonin rekursiossa lapsifunktio muuttaa myös vanhempien arvoja (kun ne ovat parametreina). Pelottavaa! En muistanut ollenkaan. Pitää kerrata lisää, että varmasti osaan oikein jatkossa. Oli hankalaa debuggata rekursiota `traverse()`:ssa.
- Osaan nyt näköjään tehdä puita `map`:illa. Helpommalla olisi varmaan päässyt kun olisi käyttänyt varsinaisia puuluokkia ja Node-luokkaa, mutta tulipahan kokeiltua!

## Epäselvää

ei tule mieleen, pitää tehdä fiksumpi minecount-tilanteiden ratkaisija ja väsätä sitten rutkasti testejä seuraavaksi.

## Seuraavaksi
- fiksumpi minecount (eli tilanteet, joissa jäljellä olevan mapin ratkaisemiseen tarvitaan tieto jäljellä olevien miinojen lukumäärästä: esim. jos 3 miinaa jäljellä, joista kaikkia `self.front` ei näe, niin loput ruudut = jäljellä olevat miinat). Nykyinen on liian brut, ja rajoittunut siksi pieniin tilanteisiin.
- jos ehtii, niin arvailuja. Jos ei fiksumpaa ehdi, niin random-arvaukset. Tällä hetkellä jos 2 botin rundia putkeen on sama jäljelläolevien miinojen lkm, niin minecount-logiikka aktivoituu. Arvauksia varten tehtäneen siis niin, että jos 3 rundia putkeen (eli minecount ei auttanut), niin arvataan.
- testejä
