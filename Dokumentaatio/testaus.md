## Mitä on testattu, miten tämä tehtiin?

- [Logic validity testing report](../Testing/Logic_validity_testing/Logic_validity_testing.pdf)
- [Logic validity testing report for classic game mode](../Testing/Logic_validity_testing/Logic_validity_testing_CLASSIC.pdf)
- [Voittoprosentit klassisella pelimuodolla, jossa aloitusruutu ∈ [0,8]](../Testing/Win_percentages_and_average_time_per_game_only_classic.pdf)
- [Voittoprosentit moderneilla pelimuodolla, jossa aloitusruutu = 0](../Testing/Win_percentages_and_average_time_per_game.pdf)
- [Testing manual](../Testing/Logic_validity_testing/Testing_manual.pdf)

- `CSP_solver.py`:ssä on 15 testiä eri yhtälöryhmistä, suurin osa miinaharavan tilanteista. Näissä rajoitteena on, että jokainen muuttuja on 0 tai 1, koska jokainen muuttuja kertoo kyseisen muuttujan (miinaharavamapin ruudun) miinojen lukumäärän (0 tai 1). 'CSP' eli 'constraint satisfaction problem' tarkoittaa tässä juurikin sitä rajoitetta ('constraint'), että jokainen muuttuja on 0 tai 1.

- Itse `simple_solver()`:in toiminta on helppo testata `botGame.py`:ssä niin, että laittaa alalaidassa `csp_on=False`. Tämän jälkeen jäljelle jäävät vain kaikkein yksinkertaisimpien tapausten ratkaisut ((1) kaikki naapurit liputetaan, kun naapurien lukumäärä = avatun ruudun numero; (2) chordaus kun mahdollista). Tällä pystyy ratkaisemaan noin yli 50% beginner-peleistä, muttei juurikaan muuta.

- `CSP_solver`:in ja sitä edeltävien simppelimpien ratkaisijoiden validiteettitestaus tapahtuu tiedostossa **constraint_problem_solver_for_testing.py**. Tämä käyttää Problem.constraint-kirjastoa brute-forcaamaan kaikki mahdolliset ratkaisut siihen syötetyille yhtälöille. Sitten käyn kaikista ratkaisuista läpi, onko jokin muuttuja aina 0 tai 1. Jos on, eikä tätä ollut siis löydetty hävityssä pelissä, virhelaskuri nousisi. Kertaakaan tätä ei ole tapahtunut vielä, eli nämä testit ovat menneet läpi (tulos-pdf yllä kuvaa tuloksia viimeisimpien muutosten jälkeen, tätä aiemmin on myös testattu kymmeniä tuhansia hävittyjä pelejä)
  - tämä testaus EI ota minecount:ia huomioon, koska kyseinen yhtälö olisi liian iso (järjestön määrä ratkaisuja, laskentakapasiteetti eikä muisti riitä)
  - tämän ongelman epäsuoraan ratkaisemiseen käy empiirisesti (tilastollisesti), muttei sinänsä matemaattisesti, seuraava kohta:

- kaikista pelatuista expert-peleistä 5.1% voitetaan ilman yhtäkään arvausta. Tämä on sama tulos kuin https://github.com/DavidNHill/JSMinesweeper#readme (nimimerkki 'Shuffler' Minesweeper Community -Discordissa), joka on pelannut miljoonia expert-pelejä ja saa ratkaistua 41% kaikista klassisista Expert-peleistä (itse saan 33.4%!). Koska arvauksia tehdään kummassakin tapauksessa VAIN JOS logiikalla ei saada ratkaistua muuttujia, tämä on melko vahva todiste (itselläni n = 100 000 Expert-peliä) siitä, että (joko kummaltakin puuttuu logiikkaa tai) kummallakin on käytössä kaikki käytettävissä oleva logiikka. Tämä 41% on korkein lukema, johon olen missään törmännyt (eräs artikkeli käyttää _modernia_ expertiä, eli sitä missä alkupläjäys (0) on taattu, ja saa 45% tällöin läpi; itse sain 40% modernissa versiossa, joten 45% vastannee ~35:tä prosenttia klassisessa pelimuodossa)
- lähde sille, että 5.1% kertoo logiikan olevan kunnossa: (Discord: käyttäjänimen 'Shuffler' viestit 28.10.2024 https://discord.com/channels/814801005195558953/1231515135491969045 in https://discord.gg/BdhKNQju4U) (JS version: https://github.com/DavidNHill/JSMinesweeper#readme)

## Minkälaisilla syötteillä testaus tehtiin?

- `CSP_solver.py`:ssä on 15 testiä eri yhtälöryhmistä, suurin osa miinaharavan tilanteista. Näissä rajoitteena on, että jokainen muuttuja on 0 tai 1, koska jokainen muuttuja kertoo kyseisen muuttujan (miinaharavamapin ruudun) miinojen lukumäärän (0 tai 1). 'CSP' eli 'constraint satisfaction problem' tarkoittaa tässä juurikin sitä rajoitetta ('constraint'), että jokainen muuttuja on 0 tai 1.

- logiikkavalidiustestaus tapahtui enimmäkseen Intermediate-peleissä, koska siihen $\approx$brute-force-tarkastajan paukut riittävät, mutta jossa kuitenkin on sinänsä sama logiikka käytössä kuin Expertissäkin. Myös expert-pelejä tarkastettiin, mutta se on todella hidasta. Samoin beginnerin käyttö tähän tarkoitukseen on epäkätevää, sillä kestää julmetun kauan hävitä suurta määrää beginner-pelejä

- itse ratkaisuprosenttia ja muita arvoja (aika/peli, arvaukset/peli, voitetut pelit ilman arvauksia, minecount-tilanteiden ratkaisut per peli) on testattu kaikilla kolmella pelimuodolla, viimeisimpien muutosten jälkeen ainakin 100 000 kertaa kutakin pelimuotoa

## Miten testit voidaan toistaa?
Ajamalla kuten kuvattu [testing manualissa](../Testing/Logic_validity_testing/Testing_manual.pdf)

`CSP_solver.py`:n testit **tests_for_CSP_solver.py**-tiedostossa ovat kiinteitä samoin kuin `CSP_solver_old`:in testit tiedostossa **tests_for_CSP_solver_old.py**. 

Joukkojen iteraatiojärjestyksiä lukuunottamatta `CSP_solver_old`:in tapauksessa testit tuottavat joka kerta saman tuloksen. HUOM! **tests_for_CSP_solver_old.py**:n viimeinen testi joskus tuottaa kaikki ratkaistut muuttujat, joskus osan, joskus ei mitään - joukkojen iteraatiojärjestys voi vaihdella. Kuitenkin ulos tuotetut ratkaisut ovat aina samat.

Huomaa, että peliä pelatessa konsoliin tulostuu, mistä ratkaisu kulloinkin tulee PAITSI jos ratkaisu tulee `simple_solver()`:ista, jolloin ei tulostu mitään (koska muuten konsoli olisi käyttökelvoton lukea, koko ajan sama rivi siitä että simple solver ratkaisi jotain - sitä käytetään ylivoimaisesti eniten kaikissa pelimuodoissa)

## Ohjelman toiminnan mahdollisen empiirisen testauksen tulosten esittäminen graafisessa muodossa. (Mikäli sopii aiheeseen)

- [Logic validity testing report](../Testing/Logic_validity_testing/Logic_validity_testing.pdf)
- [Logic validity testing report for classic game mode](../Testing/Logic_validity_testing/Logic_validity_testing_CLASSIC.pdf)
- [Voittoprosentit klassisella pelimuodolla, jossa aloitusruutu ∈ [0,8]](../Testing/Win_percentages_and_average_time_per_game_only_classic.pdf)
- [Voittoprosentit moderneilla pelimuodolla, jossa aloitusruutu = 0](../Testing/Win_percentages_and_average_time_per_game.pdf)
