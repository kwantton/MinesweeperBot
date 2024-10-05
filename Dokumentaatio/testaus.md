- [ ] to-do: Yksikkötestauksen kattavuusraportti.

Sit kun kaikki ratkeaa, niin myös riemu ratkeaa. Toistaiseksi kaikki tilanteet eivät ratkea (osa CSP:stä on vajavaista, eikä koko mapissa jäljelläolevaa minecount:ia ole otettu huomioon ollenkaan (tällä ratkeaa vielä hyvin marginaalinen osa tapauksista)).

- [ ] to-do: Mitä on testattu, miten tämä tehtiin?

`CSP_solver.py`:ssä on 12 testiä eri yhtälöryhmistä, suurin osa miinaharavan tilanteista. Näissä rajoitteena on, että jokainen muuttuja on 0 tai 1, koska jokainen muuttuja kertoo kyseisen muuttujan (miinaharavamapin ruudun) miinojen lukumäärän (0 tai 1). 'CSP' eli 'constraint satisfaction problem' tarkoittaa tässä juurikin sitä rajoitetta ('constraint'), että jokainen muuttuja on 0 tai 1.

Itse `simple_solver()`:in toiminta on helppo testata `botGame.py`:ssä niin, että laittaa alalaidassa `csp_on=False`. Tämän jälkeen jäljelle jäävät vain kaikkein yksinkertaisimpien tapausten ratkaisut ((1) kaikki naapurit liputetaan, kun naapurien lukumäärä = avatun ruudun numero; (2) chordaus kun mahdollista). Tällä pystyy ratkaisemaan noin yli 50% beginner-peleistä, muttei juurikaan muuta.

- [ ] to-do: Minkälaisilla syötteillä testaus tehtiin?

`CSP_solver.py`:ssä on 12 testiä eri yhtälöryhmistä, suurin osa miinaharavan tilanteista. Näissä rajoitteena on, että jokainen muuttuja on 0 tai 1, koska jokainen muuttuja kertoo kyseisen muuttujan (miinaharavamapin ruudun) miinojen lukumäärän (0 tai 1). 'CSP' eli 'constraint satisfaction problem' tarkoittaa tässä juurikin sitä rajoitetta ('constraint'), että jokainen muuttuja on 0 tai 1.

- [ ] to-do: Miten testit voidaan toistaa?

`CSP_solver.py`:n testit `if __name__ == __main__`-osiossa ovat kiinteitä. Joukkojen iteraatiojärjestyksiä lukuunottamatta niiden tulisi tuottaa sama tulos joka kerta.

- [ ] to-do: Ohjelman toiminnan mahdollisen empiirisen testauksen tulosten esittäminen graafisessa muodossa. (Mikäli sopii aiheeseen)

Demoan sitten demotilaisuudessa, mitä se osaa ja ei osaa. Onneksi tein kattavan toimivan graafisen käyttiksen.
