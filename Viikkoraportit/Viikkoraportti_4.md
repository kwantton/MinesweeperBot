1. Tehty tällä viikolla:
Rakennettu oikeasti universaalia `CSP_solveria` ihan jumalattomasti. Getting there. Alla detaljeja.
Vanhan ratkaisumallin (`CSP_solver`:issa) ongelma oli, ettei minulla ollut mitään todistusta siitä, päädynkö lopulta tilanteeseen, jossa kaikki mahdolliset vastaantulevat tilanteet saadaan käytössä olevilla metodeilla ratkaistua. Siksi tämä uusi malli.

2. Miten edistynyt: Hyvin. Kesken on, maanantaina laskennan mallien tentti, ja todari IIa kesken, muutakin hommaa on valitettavasti.
- kukin mapista peräisin oleva yhtälö on totta; siis jokaiselle niistä on löydyttävä ratkaisu
  1. kunkin yhtälön henk.kohtainen ratkaisukombinaatio (alustava, ei ota muita yhtälöitä huomioon) muodostetaan käyttämällä funktiota `find_and_group_possible_answers_per_single_equation` joka ottaa huomioon kyseisen yhtälön summan ja sen, että joka muuttuja on 0 tai 1. Eli ei paha aikavaativuus. Esim. a+b=1, niin a=0 ja b=1, tai a=1 ja b=0.
  2. kukin mahdollinen ratkaisu per alkuperänen yhtälö koplataan YHTEEN (vain ja ainoastaan yhteen) toiseen ryhmään (ryhmään eli toiseen yhtälöön; tämän toisen yhtälön kaikkiin yhteensopivuun alt-ratkaisuihin, joita on yleensä noin 2-5 kpl) käyttämällä funktiota `restrict_solution_space_as_equation_pairs_with_common_variables`
  3. ylläoleva koplaus tehdään yhteen suuntaan, aloittaen mielivaltaisesta yhtälöstä, eikä koplausta siis koskaan tehdä edestakaisin yhtälöiden välill. Tämä mahdollistaa puun rakentamisen; yksi puu per ALKUPERÄISEN YHTÄLÖN (ei useamman, vaan tasan yhden yhtälön!) yksi alt-ratkaisu, eli yleensä 2-3 puuta yhteensä. Voi olla myös 1, mutta tämä ei muuta laskennan määrää; kaikki vaihtoehdot käydään seuraavaksi läpi:
  4. jokainen näistä puista käydään läpi ja kootaan KELPAAVAT ratkaisut, joissa
       - jokaisesta ryhmästä (eli alkup. yhtälöstä) otetaan TASAN YKSI alt-ratkaisu (alt, eli alternative, eli vaihtoehtoinen, eli toisensa poissulkeva per alkuperänen yhtälö). Esim. jos oli 4 yhtälöä, niin 4 ryhmää, joista kustakin yksi alt-ratkaisu per yksi kokonainen ratkaisukandidaatti.
       - tämä tapahtuu aina samassa järkässä kun kohdassa 2. rakennettiin koplaukset, eli vaihtoehtoja on rajallinen määrä; ei voida käydä ryhmiä läpi kuin tasan yhdessä järkässä
       - esim. jos on 4 yhtälöä, joissa kaikissa 3 mahdollista ratkaisua, niin tulee ABSOLUTE MAX vain 3^4 eli 81 mahdollista vertailua JA jokaisessa niissä lopetetaan jo keskellä jos kyseinen alt ei käy, eli oikeasti vain kourallinen lopullisia ratkaisukandidaatteja
       - kustakin mahdollisesta kokonaisesta ratkaisusta (yht. kourallinen) katsotaan kustakin muuttujasta, onko sen arvo aina 0. Jos on, niin sen ratkaisu on 0. Jos aina 1, niin sen ainoa ratkaisu on 1. Muut jäävät (ainakin toistaiseksi) ratkaisematta, kunnes mappia avataan lisää, ihan normaalisti.
3. Mitä opin:
- `restrict_solution_space_as_equation_pairs_with_common_variables`:issa voin koplata kunkin yksittäisen ryhmän mahdolliset vaihtoehtoiset ratkaisut tasan yhden ('seuraavan') ryhmän mahdollisiin vaihtoehtoisiin ratkaisuihin.
- rakensin alusta asti, ja viimeisimpänä korjasin merkittävästi `join_comp_groups_into_solutions`:in ja siinä etenkin `traverse`:n.
- markdownin numerolistat ovat paskoja koska joka kerta kun vaihdat numeron jälkeen riviä ja kumitat, jos et haluakaan seuraavaa numeroa vaan esim. viivan, kaikki seuraavat numerot ovat edelleen kaikki yhden liian suuria.

4. Epäselvää: ei pitäisi olla mitään. En tiedä kuinka kamalalta koodi näyttää, mutta minulla on oikein hyvä kuva siitä mitä olen tällä hetkellä tekemässä, JA tiedän ettei se ole aikavaativuudeltaan raskasta myöskään:

5. Seuraavaksi:
- `restrict_solution_space_as_equation_pairs_with_common_variables`:n korjaus kesken.
- Maanantaina LAMA:n välitentti. Jee...
