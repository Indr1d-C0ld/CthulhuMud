# Magia e Incantesimi

## Come funziona la magia

### Requisiti per lanciare un incantesimo

Per lanciare un qualsiasi incantesimo servono, contemporaneamente (confermato da *helps/spell_casting.txt*):

1. un rating maggiore di zero nella skill generica **Lancio degli Incantesimi** (`spell_casting`) — senza di essa il personaggio non può lanciare nulla, punto;
2. un rating maggiore di zero nella skill **specifica** dell'incantesimo (quasi sempre chiamata come l'incantesimo stesso: per lanciare Cura Leggera serve la skill "Cura Leggera"; alcune skill però coprono intere famiglie di incantesimi con nomi diversi dal proprio — vedi il riquadro più sotto);
3. mana sufficiente per pagarne il costo.

Non tutti gli incantesimi richiedono un bersaglio: quelli che lo richiedono e non lo trovano (nessun bersaglio indicato e nessun bersaglio di default disponibile) falliscono immediatamente senza consumare nulla. Durante un combattimento, se non si specifica un bersaglio per un incantesimo ostile, il gioco seleziona automaticamente il nemico contro cui si sta già combattendo (`combat_target`) — la fonte stessa consiglia comunque di indicare sempre il bersaglio a mano per essere sicuri di colpire chi si intende colpire. Gli incantesimi non ostili senza bersaglio specificato di default colpiscono il lanciatore stesso.

Alcuni incantesimi (es. Chiaroveggenza, Ventriloquio, Controllo del Tempo, Cambia Taglia, Telecinesi, Creazione Minore/Maggiore) richiedono invece un **testo libero** al posto o in aggiunta al bersaglio (una direzione, un messaggio, un'indicazione MIGLIORI/PEGGIORI, un oggetto da creare): senza di esso il lancio viene rifiutato a monte. **Ventriloquio** è l'unico che vuole entrambi, un bersaglio *e* un messaggio: si scrive `cast ventriloquate <bersaglio> <messaggio>` (la prima parola è il bersaglio, il resto è ciò che sembrerà dire). Prima dell'audit totale questa combinazione non era gestita e l'incantesimo non si poteva lanciare in alcun modo.

Tre incantesimi (Varco Dimensionale, Evocazione, Teletrasporto), più altri aggiunti in tornate successive per la stessa ragione (Evoca Antico, Anima Arma, Agonia, Incognito), cercano il proprio bersaglio in tutto il mondo di gioco e non nella sola stanza del lanciatore, perché la loro stessa natura lo richiede — per tutti gli altri incantesimi con bersaglio, la ricerca resta limitata alla stanza.

### Skill che coprono più incantesimi

La fonte (*helps/spell_casting.txt*) conferma che, se è vero che la maggior parte degli incantesimi condivide il nome con la propria skill, esistono anche skill che ne coprono diversi contemporaneamente. Il porting ha trovato e catalogato tutte queste famiglie condivise: **Controllo del Corpo** (10 incantesimi), **Negromanzia** (10), **Magia Divina** (3), **Magia Onirica** (6), **Magia Mentale** (3), **Via della Natura** (4), **Via del Duellante** (7), **Taumaturgia** (5), **Magia degli Antichi** (2), **Magia Clericale** (2), **Combattimento Elementale** (4), **Magia Protettiva** (3, di cui uno raggruppato per analogia — vedi tabella), **Scudo Elementale** (11, la famiglia più numerosa: tre scudi, quattro benedizioni di immunità e quattro parole di resistenza), **Via dell'Evocatore** (7), **Magia del Caos** (4), oltre a diverse coppie/triplette minori (es. Pelle Indurita coi suoi quattro livelli, Missile Magico con Zap e Zappatore Magico, Fretta con Lentezza, Forza con le sue due versioni potenziate, e altre indicate nella tabella sottostante tramite la colonna "Skill richiesta"). In tutti questi casi la colonna "Skill richiesta" della tabella del catalogo riporta la skill effettivamente necessaria, che può avere un nome diverso da quello dell'incantesimo.

### CAST contro RITUAL

Il comando base per lanciare qualsiasi incantesimo è `cast <incantesimo> [bersaglio]`. I personaggi che possiedono la skill **Maestria nei Rituali** (`ritual_mastery`) possono usare al suo posto `ritual <incantesimo> [bersaglio]`: normalmente non c'è alcuna differenza pratica fra i due comandi (confermato da *helps/ritual_mastery.txt* e *helps/cast.txt*), ma se il lanciatore è raggruppato (`GROUP`) con altri possessori della stessa skill presenti nella sua stanza, un lancio con RITUAL risulta più potente — tanto più quanti sono gli alleati col rating giusto. Il porting traduce questo bonus (mai quantificato dalla fonte) in una percentuale di successo aggiuntiva fissa per ogni alleato qualificato presente (`BONUS_RITUALE_PER_MEMBRO`, scelta di design dichiarata in `world/magic.py`), applicata solo alla riuscita del lancio, non al costo in mana né all'entità dell'effetto.

I comandi `spell <incantesimo>` e `spells` (senza argomenti, equivalente a digitare `cast` da solo) sono entrambi confermati da *helps/spell_casting.txt*: il primo mostra i dettagli di un incantesimo specifico (skill richiesta, rating attuale, costo in mana, se serve un bersaglio, la descrizione), il secondo elenca tutti gli incantesimi conosciuti col relativo costo in mana attuale — costo che, come spiegato sotto, scende man mano che sale il rating nella skill specifica.

### Il costo in mana

Il costo "di listino" di ogni incantesimo (colonna "Costo mana" nel catalogo) è quello per un lanciatore con rating 0 nella skill specifica. La fonte conferma che il costo scende all'aumentare del rating in quella skill; non pubblica però una formula esatta. Il porting applica una riduzione lineare fino al 50% del costo base (`RIDUZIONE_MANA_MASSIMA`, scelta di design) raggiunta a un rating pari o superiore a 100 — una scelta di design dichiarata, come tutte le formule numeriche esatte non pubblicate dalla fonte originale (vedi Dossier Miskatonic, capitolo Professioni). Il mana viene addebitato all'inizio del lancio (fase di canalizzazione, vedi sotto) e **non viene restituito** in caso di fallimento o interruzione, per coerenza con la convenzione classica dei MUD DikuMUD-derivati.

### Il lancio non è istantaneo: canalizzazione e interruzione

Confermato da *helps/spell_casting.txt* ma rimasto per lungo tempo non implementato nonostante fosse già descritto: lanciare un incantesimo richiede un breve intervallo di "canalizzazione" — **`TEMPO_LANCIO_SECONDI` = 2 secondi** nel porting (valore non specificato dalla fonte, quindi scelta di design) — prima che l'effetto si risolva davvero. Durante questo intervallo il lancio può essere interrotto in tre modi, tutti confermati dalla fonte:

- usando il comando `stand`;
- cambiando stanza (uscendo, fuggendo, venendo trascinati altrove);
- subendo un colpo in combattimento — con una probabilità dichiarata del **40%** (`PROBABILITA_INTERRUZIONE_COMBATTIMENTO`, scelta di design: la fonte conferma che può succedere ma non quantifica quanto spesso).

Un'interruzione, per qualunque causa, ha inoltre una probabilità dichiarata del **50%** (`PROBABILITA_AFFATICAMENTO_SU_INTERRUZIONE`, scelta di design) di lasciare il personaggio **affaticato** per 60 secondi (`DURATA_AFFATICAMENTO_SECONDI`) — uno stato temporaneo con effetti negativi, guaribile anzitempo con l'incantesimo Ristoro (o la sua versione potenziata, Passo Leggero). Da non confondere con l'incantesimo offensivo **Fatica** (`fatigue`, famiglia Danno Divino), che indebolisce un nemico drenandogli Forza e movimento: condividono solo il nome italiano, non il meccanismo.

Il mana speso durante la canalizzazione non viene restituito se il lancio viene interrotto, esattamente come in caso di fallimento a fine canalizzazione.

### Il bersaglio che si allontana

Se durante la canalizzazione è il **bersaglio** ad andarsene — fugge, viene trascinato altrove, cambia stanza per qualunque motivo — l'incantesimo si disperde: al termine dei due secondi il gioco controlla che il bersaglio sia ancora nella stanza del lanciatore (o fra gli oggetti che il lanciatore porta con sé), e se non c'è l'energia si perde, con il mana già speso.

Fino all'audit totale non era così: l'incantesimo raggiungeva il bersaglio ovunque fosse andato, e si poteva finire con un dardo di fuoco chi era già scappato. La regola è la stessa che la fonte applica al lanciatore (che interrompe il lancio se lascia la stanza), estesa al bersaglio come scelta di design dichiarata.

Fanno eccezione, per loro stessa natura, gli incantesimi pensati per raggiungere qualcuno lontano: **Varco Dimensionale**, **Evocazione**, **Teletrasporto**, **Evoca Antico**, **Anima Arma**, **Agonia** e **Incognito**.

### Incantesimi che agiscono solo sugli oggetti

Sette incantesimi lavorano su un oggetto e, secondo la fonte, rischiano di distruggerlo: **Consistenza**, **Permanenza**, **Universalità**, **Lama della Furia**, **Ricarica**, **Anima Arma** e **Personalizza Arma**. Accettano come bersaglio **solo un oggetto inanimato**: su un personaggio, un NPC, una stanza o un'uscita il lancio viene rifiutato prima di cominciare, e il mana non viene speso.

La regola esiste per una ragione precisa, documentata nel capitolo dello staff: prima dell'audit totale, `CAST CONSISTENCE` senza argomenti mirava al lanciatore stesso, e il rischio di "distruggere l'oggetto" poteva **cancellare dal database il personaggio** — il proprio, o quello di un altro giocatore presente.

### Percentuale di successo e tiro salvezza del bersaglio

Al termine della canalizzazione (se non interrotta) il gioco tira per il successo dell'incantesimo. La percentuale dipende dalla media fra il rating in Lancio degli Incantesimi e il rating nella skill specifica, con un piccolo contributo aggiuntivo dalla skill **Maestria negli Incantesimi** (`spell_mastery`) — nessuna formula esatta è pubblicata dalla fonte, quindi anche qui si tratta di una scelta di design (clampata fra un minimo del 5% e un massimo del 95%, per non rendere mai un lancio né impossibile né garantito).

Per gli incantesimi marcati come **ostili** (bersaglio non consenziente — segnalati con ⚔ nel catalogo) si applica poi un **tiro salvezza** del bersaglio, confermato da *helps/spell_casting.txt*: il personaggio colpito tenta di resistere con la propria skill **Autodisciplina** (già descritta altrove come fonte generica di "resistenza alla magia") più metà del proprio punteggio di Saggezza, contro la stessa media di skill che ha deciso il successo del lanciatore. Il porting implementa questo tiro come un tutto-o-niente (resiste = nessun effetto, fallisce = effetto pieno) invece della riduzione percentuale continua suggerita dalla fonte: una semplificazione dichiarata, necessaria per non dover aggiungere un parametro di "efficacia parziale" a ciascuna delle 235 funzioni di effetto che il registro degli incantesimi ormai comprende.

### Il costo in sanità per la magia proibita

*helps/sanity.txt* conferma che lanciare certi incantesimi fa parte dei tanti fattori che erodono la sanità mentale del personaggio, ma — come per gran parte del sistema di sanity — non specifica quali incantesimi né di quanto. Il porting ha scelto di applicare un piccolo costo in sanità (da 1 a 3 punti, casuale) a ogni incantesimo la cui **skill richiesta** appartiene a una delle famiglie esplicitamente legate a conoscenza proibita o orrore cosmico: **Negromanzia**, **Magia degli Antichi**, **Magia del Caos**, **Via dell'Evocatore**, **Vudù** e **Magia Divina**. La scelta è a livello di intera famiglia (skill), non di singolo incantesimo — diversamente dal tag "ostile" che invece è per singolo incantesimo — ed è dichiarata esplicitamente come tale nel codice sorgente. Il costo si paga già alla sola canalizzazione (insieme al mana), non al successo dell'effetto: la stessa identica logica del mana speso anche in caso di fallimento.

### Legenda della tabella del catalogo

Nel catalogo che segue, il simbolo **⚔** davanti al nome segnala un incantesimo **ostile** (bersaglio non consenziente, soggetto al tiro salvezza descritto sopra); il simbolo **🚫** segnala un incantesimo che la fonte originale dichiara esplicitamente **disabilitato** e che quindi, in questo porting, fallisce sempre onestamente invece di produrre il proprio effetto (vedi la sezione dedicata più sotto). La colonna "Bersaglio" indica se l'incantesimo richiede un bersaglio esplicito per poter essere lanciato.

## Catalogo completo degli incantesimi

Il registro completo (`world/spells.py`) conta **235 incantesimi**, ciascuno con una funzione di effetto dedicata in `world/magic.py` (nessuno resta senza un effetto meccanico implementato: la rete di sicurezza generica in `_esegui_effetto()` esiste solo per un eventuale incantesimo futuro aggiunto al registro senza ancora una funzione propria). Le tabelle seguenti li raggruppano secondo l'organizzazione delle famiglie/skill già presente nel file sorgente — che a sua volta rispecchia l'ordine di scoperta durante la scansione esaustiva del sito originale, dai sei incantesimi "storici" della prima implementazione fino alle famiglie di skill-prerequisito scoperte più avanti nel progetto.

#### Incantesimi fondamentali

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| Cura Leggera | Cura Leggera | 8 | si | Un incantesimo di guarigione di base. |
| ⚔ Presa Folgorante | Presa Folgorante | 10 | si | Scarica un fulmine attraverso il tocco, danneggiando il bersaglio. |
| Benedizione | Benedizione | 6 | si | Migliora temporaneamente la capacita' di colpire in combattimento. |
| Rilevare la Magia | Rilevare la Magia | 5 | no | Percepisce la presenza di magia nei dintorni. |
| Maschera di Se' | Maschera di Se' | 6 | no | Offusca il proprio aspetto con un'illusione (si lancia di nuovo per toglierla). |
| Chiaroveggenza | Chiaroveggenza | 10 | no | Vede a distanza in una direzione, senza spostarsi. |

#### Mago e Occultista (famiglia "Mage/Occult Master")

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| Assorbimento Magico | Assorbimento Magico | 15 | no | Concede protezione extra dagli attacchi magici, assorbendo e dissipando parte degli incantesimi diretti contro il lanciatore. |
| ⚔ Accecamento | Accecamento | 12 | si | Rende il bersaglio incapace di vedere. |
| Marchiatura | Marchiatura | 25 | si | Imprime su un'arma non ancora marchiata un elemento scelto a caso (Fiamma, Gelo, Acido o Fulmine), permanente se il tentativo riesce - ma l'arma rischia di essere distrutta nel tentativo. |
| ⚔ Mani Ardenti | Mani Ardenti | 12 | si | Scaglia una vampata di fiamme dalle mani, infliggendo danno da fuoco. |
| ⚔ Richiamo del Fulmine | Richiamo del Fulmine | 20 | no | Richiama un fulmine su ogni personaggio all'aperto nella stessa area del lanciatore - funziona solo all'aperto, con il maltempo. |
| Calma | Calma | 10 | no | Riduce paura e furia, puo' interrompere un combattimento e riduce temporaneamente la capacita' di colpire e il danno. |
| Cancellazione | Cancellazione | 20 | si | Rimuove gli effetti magici attivi su un bersaglio (pagina originale priva di dettagli: effetto qui scelto per analogia con Dissolvere la Magia). |
| ⚔ Ammaliare | Ammaliare | 18 | si | Asservisce una vittima, che seguira' e obbedira' agli ordini del lanciatore se l'incantesimo riesce. |
| Luce Continua | Luce Continua | 8 | no | Crea una sfera di luce arcana che non si spegne mai, fornendo illuminazione indefinita. |
| Creare Cibo | Creare Cibo | 10 | no | Forma un fagotto di frutta e verdura commestibile dal nulla. |
| Creare Sorgente | Creare Sorgente | 12 | no | Evoca una sorgente magica d'acqua scintillante, non permanente. |
| Rilevare il Nascosto | Rilevare il Nascosto | 8 | no | Permette di vedere oggetti e creature nascosti o occultati, di livello pari o inferiore al lanciatore. |
| Rilevare l'Invisibile | Rilevare l'Invisibile | 8 | no | Permette di vedere oggetti e creature invisibili, di livello pari o inferiore al lanciatore. |
| Dissolvere la Magia | Dissolvere la Magia | 20 | si | Rimuove gli effetti magici attivi su un bersaglio (pagina originale priva di dettagli: effetto qui scelto per coerenza col nome). |
| Scudo Elementale | Scudo Elementale | 18 | no | Avvolge il lanciatore in una protezione contro un elemento (pagina originale priva di dettagli: scelta di design in analogia con le altre magie difensive elementali). |
| Incantare Armatura | Incantare Armatura | 20 | si | Potenzia un'armatura con magia protettiva: ogni lancio riuscito ne alza il livello di 1 e ne migliora la classe armatura di 1-2 punti, ma un tentativo fallito rischia di danneggiarla o distruggerla (il rischio sale a ogni lancio riuscito successivo). |
| Incantare Arma | Incantare Arma | 20 | si | Potenzia un'arma con magia: ogni lancio riuscito ne migliora colpire e danno e ne alza il livello di 1; piu' lanci sono possibili sulla stessa arma, ma il rischio di danneggiarla sale a ogni successo. |
| ⚔ Fuoco Fatato | Fuoco Fatato | 10 | si | Incantesimo d'attacco che alza la classe armatura della vittima (la rende piu' facile da colpire) di 2 punti per livello del lanciatore. |
| Nebbia Fatata | Nebbia Fatata | 10 | no | Rivela personaggi e oggetti invisibili o nascosti nella stanza. |
| ⚔ Soffio di Fuoco | Soffio di Fuoco | 22 | si | Un potente soffio infuocato contro un bersaglio (parte della famiglia 'Magie del Soffio': Acido/Fuoco/Gelo/Gas, ognuna piu' o meno efficace contro immunita' naturali diverse). |
| ⚔ Palla di Fuoco | Palla di Fuoco | 25 | si | Crea una grande sfera di fuoco lanciata contro il bersaglio: il danno viene sia dall'impatto sia dal calore delle fiamme. |
| Volo | Volo | 15 | no | Permette di fluttuare in aria: il movimento diventa piu' facile e meno faticoso, ma non si puo' volare sott'acqua. |
| ⚔ Soffio Gelido | Soffio Gelido | 22 | si | Un potente soffio gelido contro un bersaglio (famiglia 'Magie del Soffio', vedi Soffio di Fuoco). |
| ⚔ Possessione Maggiore | Possessione Maggiore | 30 | si | Come Possessione Minore, ma funziona anche su NPC piu' potenti: sposta la mente del lanciatore nel corpo di un NPC, utilizzabile come proprio finche' non torna con il comando RETURN o quel corpo muore. |
| Pelle Indurita | Pelle Indurita | 15 | no | Il primo di una serie di incantesimi difensivi (Pelle di Corteccia / di Pietra / di Ferro / d'Acciaio) che induriscono la pelle del lanciatore, rendendolo piu' resistente ai danni; ciascuno della serie e' piu' difficile e costoso in mana del precedente. |
| Fretta | Fretta | 15 | si | Aumenta temporaneamente la Destrezza del bersaglio, rendendolo piu' rapido e agile in combattimento (l'opposto, Lentezza, la riduce). |
| Identificare | Identificare | 12 | si | Rivela le statistiche grezze di un oggetto, eventuali effetti magici, flag speciali e le zone d'origine - le stesse informazioni della skill Sapienza Arcana (LORE), ma dipende anche dal Lancio degli Incantesimi. |
| Invisibilita' | Invisibilita' | 15 | si | Rende invisibile il bersaglio; l'effetto svanisce entrando in combattimento, e i personaggi di livello piu' alto possono comunque vederlo. |
| ⚔ Possessione Minore | Possessione Minore | 20 | si | Sposta la mente del lanciatore nel corpo di un NPC debole, utilizzabile come proprio; se il corpo posseduto muore la mente torna incolume al proprio corpo (anche a comando, con RETURN). |
| ⚔ Missile Magico | Missile Magico | 10 | si | Scaglia numerosi proiettili di energia contro il bersaglio (versione intermedia della famiglia Zap/Missile Magico/Zappatore Magico, in ordine crescente di potenza). |
| Invisibilita' di Massa | Invisibilita' di Massa | 30 | no | Rende invisibile ogni personaggio nel gruppo del lanciatore, lanciatore incluso. |
| ⚔ Ammutolire | Ammutolire | 12 | si | Rende muta la vittima, impedendole di lanciare incantesimi con componente verbale e di usare le comunicazioni IC finche' l'effetto non svanisce. |
| Negare l'Allineamento | Negare l'Allineamento | 15 | si | Rimuove le aure legate all'allineamento su un oggetto, permettendo ad altri personaggi di usarlo. |
| Attraversare le Porte | Attraversare le Porte | 12 | no | Permette al lanciatore di attraversare la maggior parte delle porte chiuse. |
| Portale | Portale | 25 | no | Crea un varco arcano bidirezionale nello spazio, simile per funzione all'incantesimo Gate ma piu' comodo per chi deve fare la spola tra due luoghi. |
| Rimuovere Invisibilita' | Rimuovere Invisibilita' | 10 | si | Rimuove l'invisibilita' da un oggetto nell'inventario del lanciatore, rendendolo di nuovo visibile a tutti. |
| Scudo Magico | Scudo Magico | 20 | no | Versione piu' potente di Scudo di Mana: avvolge il lanciatore in una sfera di energia arcana che migliora la classe armatura e riduce il danno subito (non si puo' avere entrambi gli scudi attivi insieme). |
| ⚔ Sonno | Sonno | 15 | si | Fa sprofondare il bersaglio in un sonno profondo, da cui puo' essere molto difficile risvegliarlo. |
| Forza (incantesimo) | Forza (incantesimo) | 12 | si | Aumenta temporaneamente la Forza del bersaglio. |
| ⚔ Evocazione | Evocazione | 25 | si | Trasporta un personaggio da un'altra stanza fino alla posizione del lanciatore; e' molto difficile evocare un personaggio di livello superiore, e alcune stanze non permettono di essere evocati ne' di evocare. |
| Evocare Famiglio | Evocare Famiglio | 25 | no | Richiama una creatura al servizio del lanciatore, completamente obbediente ai suoi ordini; il tipo di creatura dipende dall'allineamento del lanciatore. |
| Ventriloquio | Ventriloquio | 10 | si | Getta la voce del lanciatore, facendo sembrare che sia stato un altro personaggio a dire il messaggio specificato. |
| Respirare in Acqua | Respirare in Acqua | 10 | si | Permette a chi non e' nativo di ambienti acquatici di respirare sott'acqua senza subire danni per mancanza d'ossigeno. |
| Parola di Richiamo | Parola di Richiamo | 15 | no | Funziona insieme a Ancora Psichica o Ancora Materiale: una volta ancorata una stanza, questo incantesimo trasporta il lanciatore li'. |
| ⚔ Teletrasporto | Teletrasporto | 20 | si | Trasporta il bersaglio in un luogo casuale del mondo: un modo interessante, e potenzialmente letale, di esplorare. |

#### Incantesimi delle professioni avanzate

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| ⚔ Getto Acido | Getto Acido | 20 | si | Scaglia un potente getto d'acido contro un nemico, causando gravi ustioni chimiche e danno. |
| ⚔ Soffio Acido | Soffio Acido | 22 | si | Un potente soffio d'acido contro un bersaglio (famiglia 'Magie del Soffio': Acido/Fuoco/Gelo/Gas/Fulmine, ognuna piu' o meno efficace contro immunita' naturali diverse - vedi Soffio di Fuoco/Gelo/Gas). |
| ⚔ Soffio di Gas | Soffio di Gas | 22 | no | A differenza degli altri Soffi (mirati a un bersaglio), questo colpisce chiunque nella stanza tranne il lanciatore. |
| ⚔ Soffio Fulminante | Soffio Fulminante | 22 | si | Un potente soffio elettrico contro un bersaglio (famiglia 'Magie del Soffio', vedi Soffio Acido/di Fuoco/Gelo/Gas). |
| ⚔ Invecchiamento | Invecchiamento | 18 | si | Aumenta l'eta' del bersaglio: dato che a CthulhuMUD si puo' morire di vecchiaia, e' trattato come un incantesimo d'attacco vero e proprio, e la vittima si difende. |
| Giovinezza | Giovinezza | 18 | si | Riduce l'eta' del bersaglio: l'opposto di Invecchiamento. |
| Aura | Aura | 10 | no | Circonda il lanciatore di un bagliore che riflette il proprio allineamento attuale; puo' incutere paura in chi ha un allineamento diverso dal proprio. |
| ⚔ Causa Ferita Leggera | Causa Ferita Leggera | 10 | si | Il piu' debole della famiglia Causa Ferita: un'esplosione di dolore che danneggia gli organi interni della vittima dall'interno. |
| ⚔ Causa Ferita Grave | Causa Ferita Grave | 16 | si | Versione intermedia della famiglia Causa Ferita: piu' dolorosa di Causa Ferita Leggera, ma anche piu' difficile da lanciare. |
| ⚔ Causa Ferita Critica | Causa Ferita Critica | 22 | si | Il piu' potente della famiglia Causa Ferita prima di Danno Divino: gravi danni interni, molto difficile da lanciare con successo. |
| ⚔ Danno Divino | Danno Divino | 28 | si | Il culmine della famiglia Causa Ferita (dopo Leggera/Grave/Critica): la piu' potente e la piu' difficile da lanciare con successo. |
| ⚔ Fulmine a Catena | Fulmine a Catena | 25 | no | Crea un fulmine che rimbalza per la stanza, colpendo ripetutamente ogni presente (lanciatore incluso) finche' non esaurisce la carica. |
| ⚔ Tocco Gelido | Tocco Gelido | 14 | si | Infligge danno alla vittima e ne riduce contemporaneamente la Forza con un tocco gelido. |
| ⚔ Spruzzo Cromatico | Spruzzo Cromatico | 18 | si | Spara vividi lampi di colore dalle dita del lanciatore, abbagliando il nemico e infliggendo il tipo di danno elementale a cui e' piu' vulnerabile. |
| Controllo del Tempo | Controllo del Tempo | 15 | no | Altera le condizioni meteo attuali, rendendole MIGLIORI (sereno e soleggiato) o PEGGIORI (nuvoloso e tempestoso) a seconda dell'indicazione fornita. |
| Crea Banchetto | Crea Banchetto | 18 | no | Versione potenziata di Creare Cibo: forma numerosi fagotti di frutta e verdura commestibile, tanti quanto piu' alta e' la skill del lanciatore. |
| Crea Acqua | Crea Acqua | 8 | si | Riempie un contenitore vuoto con acqua pura. |
| Cura Cecita' | Cura Cecita' | 14 | si | Rimuove la cecita' da un personaggio, permettendogli di vedere di nuovo. |
| Cura Ferita Critica | Cura Ferita Critica | 22 | si | Il piu' potente dei classici incantesimi di guarigione prima di Guarigione: ripristina grandi quantita' di punti ferita, ma costa piu' mana e richiede piu' tempo di Cura Leggera/Grave. |
| Guarigione | Guarigione | 28 | si | Il culmine della famiglia Cura Leggera/Grave/Critica: ripristina la maggior quantita' possibile di punti ferita tra questi incantesimi, ma e' anche il piu' difficile da lanciare con successo. |
| Cura Malattia | Cura Malattia | 16 | si | Rimuove una malattia infettiva da un personaggio, guarendo gli effetti debilitanti di un incantesimo come Peste. |
| Cura Veleno | Cura Veleno | 12 | si | Guarisce un personaggio avvelenato, rimuovendone gli effetti negativi. |
| Cura Ferita Grave | Cura Ferita Grave | 16 | si | Versione intermedia della famiglia di guarigione: piu' efficace di Cura Leggera, ma anche piu' difficile da lanciare. |
| ⚔ Maledizione | Maledizione | 18 | si | Rende impura e indebolita l'anima della vittima, riducendone la capacita' di colpire e la resistenza agli incantesimi. |
| ⚔ Fuoco Demoniaco | Fuoco Demoniaco | 25 | si | Evoca un'orda di demoni dagli abissi infernali per infliggere gravi danni al bersaglio. |
| Rileva Veleno | Rileva Veleno | 6 | no | Percepisce la presenza di veleno in cibo o bevande a portata di mano. |
| ⚔ Dissolvi Male | Dissolvi Male | 18 | si | Richiama la collera divina per infliggere danno a un nemico malvagio (vedi anche Dissolvi Bene, la controparte). |
| ⚔ Dissolvi Bene | Dissolvi Bene | 18 | si | Richiama la collera divina per infliggere danno a un nemico benevolo (vedi anche Dissolvi Male, la controparte). |
| ⚔ Terremoto | Terremoto | 28 | no | Scuote violentemente il terreno sotto ogni presente nella stanza, lanciatore escluso, infliggendo danno da impatto a tutti (pagina originale assente dal corpus scansionato: effetto scelto per analogia con Fulmine a Catena/Richiamo del Fulmine, altri incantesimi d'area gia' documentati). |
| ⚔ Drenaggio d'Energia | Drenaggio d'Energia | 20 | si | Assorbe esperienza, mana e movimento dal bersaglio. |
| Varco Dimensionale | Varco Dimensionale | 20 | si | Trasporta istantaneamente il lanciatore nella stessa stanza di un personaggio bersaglio (alcune stanze private o Immortali non sono raggiungibili in questo modo). |
| Parola Sacra | Parola Sacra | 28 | no | Evoca un potente angelo che combatte al fianco del lanciatore contro un nemico malvagio. |
| Percepisci Allineamento | Percepisci Allineamento | 8 | si | Rivela l'allineamento attuale del bersaglio. |
| Protezione Minore | Protezione Minore | 10 | no | Una difesa magica di base, precedente e piu' economica di Globo di Protezione/Santuario (pagina originale assente dal corpus scansionato: effetto scelto per analogia con la serie Pelle Indurita, altri incantesimi difensivi 'a gradini' gia' documentati). |
| ⚔ Fulmine | Fulmine | 18 | si | Scaglia un fulmine crepitante contro il bersaglio. |
| Localizza Oggetto | Localizza Oggetto | 12 | si | Rivela la posizione di tutti gli oggetti che corrispondono al nome specificato, ovunque nel mondo (non specifica se sono trasportati da qualcuno, e alcuni oggetti sono invisibili a questo incantesimo). |
| ⚔ Fuoco Arcano | Fuoco Arcano | 25 | si | Scaglia una o piu' scariche di energia arcana, ciascuna capace di rimuovere le protezioni magiche attive sul bersaglio. |
| Guarigione di Massa | Guarigione di Massa | 30 | no | Invia energia curativa che guarisce tutti gli alleati e amici del lanciatore in una vasta area. |
| ⚔ Peste | Peste | 20 | si | Infetta la vittima con una malattia altamente contagiosa: riduce le sue capacita' di combattimento e rischia di diffondersi ad altri. |
| ⚔ Veleno (incantesimo) | Veleno (incantesimo) | 12 | si | Indebolisce la vittima e ne riduce le capacita' di combattimento infliggendole il veleno. |
| Protezione dal Male | Protezione dal Male | 15 | no | Protegge il lanciatore dagli attacchi di nemici malvagi, riducendo di un quarto il danno subito da quell'allineamento (vedi anche Protezione dal Bene, la controparte). |
| Protezione dal Bene | Protezione dal Bene | 15 | no | Protegge il lanciatore dagli attacchi di nemici benevoli, riducendo di un quarto il danno subito da quell'allineamento (vedi anche Protezione dal Male, la controparte). |
| Ancora Psichica | Ancora Psichica | 15 | no | Lascia parte dell'essenza psichica del lanciatore in una stanza, creando un'ancora a cui tornare con Parola di Richiamo (le stanze private non si possono ancorare; l'ancora si spezza alla morte, alla disconnessione o non appena viene usata). |
| Rigenerazione | Rigenerazione | 15 | si | Aumenta la velocita' di guarigione naturale del bersaglio per tutta la durata dell'incantesimo. |
| Rimuovi Maledizione | Rimuovi Maledizione | 15 | si | Rimuove una maledizione attiva su un personaggio. |
| Rimuovi Paura | Rimuovi Paura | 12 | si | Annulla gli effetti dell'incantesimo Paura su un personaggio, che altrimenti fuggirebbe (o resterebbe incapace di attaccare) finche' l'effetto non svanisce da solo. |
| Visione | Visione | 12 | no | Concede al lanciatore un breve scorcio, sfocato ma reale, di un luogo lontano (pagina originale assente dal corpus scansionato: effetto scelto per analogia con Chiaroveggenza/Scrutare, altri incantesimi di percezione a distanza gia' documentati). |
| ⚔ Indebolisci | Indebolisci | 14 | si | Riduce temporaneamente la Forza del bersaglio, indebolendone le capacita' offensive in combattimento. |
| Frenesia | Frenesia | 20 | si | Manda il bersaglio in una furia insana durante il combattimento: effetti simili a Furia Berserk, con un grande incremento delle capacita' di combattimento e resistenza alla magia, ma anche incapacita' di ritirarsi anche quando in fin di vita. |
| Crea Pozione | Crea Pozione | 20 | no | Mescola erbe e ingredienti nella speranza di ottenere qualcosa di utile: crea una pozione magica casuale con effetti casuali, senza possibilita' di scegliere quali. |
| Vocalizzo | Vocalizzo | 10 | si | Permette al bersaglio di lanciare incantesimi senza componente verbale: anche se reso muto, potra' continuare a lanciarli finche' possiede anche questo effetto. |

#### Controllo del Corpo

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| Ascetismo | Controllo del Corpo | 15 | no | Sospende temporaneamente il bisogno di cibo e acqua del lanciatore, che non soffrira' gli effetti di fame o sete per la durata dell'effetto. |
| ⚔ Fardello di Ciccia | Controllo del Corpo | 15 | si | Fa ingrassare immediatamente il bersaglio, infliggendogli una serie di effetti negativi tipici dell'obesita'. |
| ⚔ Sete Ardente | Controllo del Corpo | 15 | si | Estrae gran parte dell'umidita' dal corpo della vittima, disidratandola e infliggendole una sete terribile. |
| Cambia Taglia | Controllo del Corpo | 12 | no | Permette al lanciatore di aumentare o diminuire la taglia del proprio corpo fisico. |
| ⚔ Grog Libero | Controllo del Corpo | 12 | si | Rende immediatamente ubriaco il bersaglio. |
| ⚔ Sobrieta' Spettrale | Controllo del Corpo | 15 | si | Rimuove immediatamente ogni alcol dal sangue e dal cervello del bersaglio, annullando all'istante gli effetti dell'ubriachezza - lasciandolo pero' con un violento mal di testa. |
| ⚔ Fame Rodente | Controllo del Corpo | 15 | si | Infligge al bersaglio una fame potente e feroce, causandogli grave debolezza e altri effetti negativi. |
| ⚔ Allucina | Controllo del Corpo | 20 | si | Confonde gravemente la mente del bersaglio, dando vita a figmenti della sua immaginazione con la magia arcana: le allucinazioni possono essere pericolose sia per lui sia per chiunque gli sia vicino. |
| Rilassati | Controllo del Corpo | 12 | si | Aumenta la resistenza del bersaglio alla perdita di sanity. |
| Linee Snelle | Controllo del Corpo | 15 | si | Rimuove una grande quantita' di grasso dal bersaglio, curandone l'obesita' e rimuovendone gli effetti negativi. |

#### Negromanzia

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| Anima Morto | Negromanzia | 25 | si | Rianima un cadavere, creando uno zombie senz'anima e totalmente obbediente al lanciatore. |
| 🚫 Lich | Negromanzia | 40 | no | Trasformerebbe permanentemente il lanciatore in un Lich non-morto. |
| ⚔ Oscurita' | Negromanzia | 18 | no | Riempie l'intera stanza di un'ondata magica di oscurita' per 30 secondi: chi vi si trova non riesce piu' a vedere la stanza (LOOK), a meno di avere con se' una fonte di luce accesa o l'incantesimo Infravisione (vedi world/illuminazione.py). |
| Mummifica | Negromanzia | 25 | si | Rianima un cadavere, creando una mummia senz'anima e totalmente obbediente al lanciatore. |
| ⚔ Profana | Negromanzia | 20 | no | Riempie l'intera stanza di un'aura malvagia, trasformandola temporaneamente in terra sconsacrata: i personaggi di allineamento buono presenti subiscono danno per il solo fatto di trovarcisi. |
| Lama dell'Anima | Negromanzia | 22 | no | Crea una spada magica incantata, forgiata dalla stessa anima del lanciatore. |
| Sosia | Negromanzia | 25 | no | Crea una replica non-morta del lanciatore, utilizzabile come un famiglio al suo fianco. |
| Sorgente di Sangue | Negromanzia | 15 | no | Evoca una fontana magica di sangue fresco. |
| ⚔ Pugno di Azathoth | Negromanzia | 40 | si | Un potente incantesimo d'attacco capace di uccidere istantaneamente il bersaglio. |
| ⚔ Inquietudine | Negromanzia | 22 | no | Diffonde un'aura malvagia nell'area, aumentando la probabilita' che i cadaveri presenti si rianimino spontaneamente in mostri non-morti. |

#### Magia Divina

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| ⚔ Mortalizza | Magia Divina | 35 | si | Rimuove la natura divina e invulnerabile di un Antico (staff). |
| ⚔ Evoca Antico | Magia Divina | 30 | si | Teletrasporta un Antico (staff) specifico nella posizione attuale del lanciatore. |
| Guardia dell'Anima | Magia Divina | 20 | si | Protegge l'anima del bersaglio dagli effetti delle proprie azioni: il suo allineamento non verra' influenzato, ad esempio uccidendo personaggi di vari allineamenti. |

#### Magia Onirica (Dreamlands)

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| Trance | Magia Onirica | 15 | si | Migliora la capacita' onirica del bersaglio, rendendo piu' probabile scivolare nelle Dreamlands sognando. |
| ⚔ Vera Dormienza | Magia Onirica | 25 | si | Trascina il bersaglio interamente nel mondo dei propri sogni: il corpo fisico viene proiettato nelle Dreamlands, recidendo il legame col mondo reale. |
| Risveglio Brusco | Magia Onirica | 18 | si | Respinge un bersaglio addormentato fuori dal proprio sogno, svegliandolo di soprassalto e riportandolo nel mondo reale. |
| ⚔ Sogno Ricorrente | Magia Onirica | 18 | si | Rimanda un bersaglio sveglio al punto esatto in cui si trovava l'ultima volta che sognava. |
| ⚔ Sonno Incantato | Magia Onirica | 20 | si | Immerge il bersaglio in un sonno profondissimo, che lo fa attraversare immediatamente nel regno dei propri sogni. |
| ⚔ Sonno Maledetto | Magia Onirica | 22 | si | Come Sonno Incantato, immerge il bersaglio in un sonno profondo e immediato - ma lo scaraventa in un incubo pericoloso invece che in un sogno sicuro. |

#### Magia Mentale / Cammino Astrale

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| Cammino Astrale | Magia Mentale | 20 | no | Distacca la mente del lanciatore dal corpo fisico, trasferendola nel proprio corpo astrale. |
| ⚔ Esplosione Astrale | Magia Mentale | 22 | si | Infligge danno a un corpo astrale - l'unico modo per colpire qualcuno mentre e' distaccato nel Cammino Astrale. |
| ⚔ Fusione Mentale | Magia Mentale | 22 | si | Un potente incantesimo d'attacco che sferra un possente colpo psionico alla mente del bersaglio, azzoppandola temporaneamente: infligge una penalita' di -5 all'Intelligenza e rende difficile ogni attivita' che richieda concentrazione profonda finche' l'effetto non svanisce. |

#### Via della Natura

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| Crea Seme | Via della Natura | 10 | no | Crea il seme di un albero. |
| Drena Vitalita' | Via della Natura | 15 | si | Drena mana da un albero, trasferendolo al lanciatore. |
| ⚔ Maledizione degli Insetti | Via della Natura | 18 | no | Evoca numerosi sciami di insetti di basso livello a infestare l'area attuale, tormentando chiunque vi si trovi. |
| ⚔ Morso di Lupo | Via della Natura | 30 | si | Trasforma il bersaglio in un licantropo. |

#### Via del Duellante

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| ⚔ Duello Magico | Via del Duellante | 20 | si | Avvia un duello arcano con un nemico: invece delle normali tecniche di combattimento, i due contendenti usano la pura forza dei propri poteri magici per sopraffarsi a vicenda. |
| Scudo Mentale | Via del Duellante | 18 | no | Avvolge il lanciatore in un'aura mistica che assorbe alcune forme di attacco mentale e magico. |
| ⚔ Psi Twister | Via del Duellante | 28 | no | Un potente incantesimo d'attacco che scatena la forza della mente del lanciatore, infliggendo danno significativo a chiunque altro si trovi nella stanza. |
| Telecinesi | Via del Duellante | 15 | no | Usa la forza della mente per spostare un oggetto da una stanza adiacente fino alla propria posizione attuale. |
| ⚔ Terrore degli Antichi | Via del Duellante | 22 | si | Crea l'immagine terrificante di Hastur l'Innominabile. |
| ⚔ Ira di Cthugha | Via del Duellante | 35 | si | Scatena una potente palla di fuoco contro il bersaglio. |
| ⚔ Ira di Ithaqua | Via del Duellante | 30 | si | Molto simile a Ira di Cthugha, ma crea una grande palla di neve che infligge danno stordente invece che letale: mette fuori combattimento invece di uccidere. |

#### Taumaturgia

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| Anima Arma | Taumaturgia | 20 | si | Richiama un'arma al suo proprietario, particolarmente utile se l'arma e' stata persa o il proprietario e' morto di recente. |
| Consistenza | Taumaturgia | 15 | si | Stabilizza un oggetto in decomposizione, impedendogli di deperire ulteriormente. |
| Permanenza | Taumaturgia | 25 | si | Rende un oggetto magico resistente a ogni forma di danno, quasi indistruttibile. |
| Ricarica | Taumaturgia | 18 | si | Riempie di nuove cariche un oggetto magico a cariche finite (come alcune bacchette o alcuni bastoni), rendendolo di nuovo utilizzabile. |
| Universalita' | Taumaturgia | 15 | si | Permette a un oggetto di esistere in ogni zona e area. |
| Personalizza Arma | Incantare Arma | 15 | si | Imbue un'arma con parte della forza vitale del lanciatore, impedendo a chiunque altro di poterla usare. |

#### Magia degli Antichi

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| Armatura di Ygolonac | Magia degli Antichi | 25 | si | Crea uno scudo arcano attorno al bersaglio, che riduce del 75% il danno fisico da combattimento (semplificazione dichiarata: la fonte limita la riduzione ai soli danni da taglio/perforazione/impatto, ma questo porting non distingue i tipi di danno fisico). |
| ⚔ Maledizione del Cacciatore | Magia degli Antichi | 35 | si | Evoca un Orrore Cacciatore a combattere contro i nemici del lanciatore. |

#### Magia Clericale, Combattimento Elementale e Magia Protettiva

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| Simbolo Clericale | Magia Clericale | 12 | si | Trasforma un comune gioiello in un simbolo sacro. |
| ⚔ Vendetta di Cthugha | Combattimento Elementale | 20 | si | Rende il bersaglio piu' vulnerabile al danno di fuoco. |
| ⚔ Vendetta di Ithaqua | Combattimento Elementale | 20 | si | Rende il bersaglio piu' vulnerabile al danno da freddo. |
| ⚔ Vendetta di Tsathoggua | Combattimento Elementale | 20 | si | Rende il bersaglio piu' vulnerabile al danno da armi. |
| ⚔ Vendetta di Yog | Combattimento Elementale | 20 | si | Rende il bersaglio piu' vulnerabile al danno da fulmine. |
| Globo di Protezione | Magia Protettiva | 25 | no | Avvolge il lanciatore in una sfera di energia protettiva che migliora drasticamente la classe armatura. |
| Santuario | Magia Protettiva | 25 | si | Riduce del 50% tutto il danno subito dal bersaglio. |
| Incantesimo d'Armatura | Magia Protettiva | 15 | si | Migliora la classe armatura complessiva del bersaglio. |

#### Pelle Indurita: i quattro livelli

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| Pelle di Corteccia | Pelle Indurita | 10 | no | Il piu' debole ed economico dei quattro incantesimi di indurimento della pelle (Corteccia/Pietra/Ferro/Acciaio), ciascuno piu' difficile e costoso del precedente. |
| Pelle di Pietra | Pelle Indurita | 18 | no | Il secondo livello di indurimento della pelle, piu' efficace di Pelle di Corteccia. |
| Pelle di Ferro | Pelle Indurita | 26 | no | Il terzo livello di indurimento della pelle, piu' efficace di Pelle di Pietra. |
| Pelle d'Acciaio | Pelle Indurita | 34 | no | Il quarto e piu' potente livello di indurimento della pelle. |

#### Famiglia di Benedizione

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| ⚔ Benedizione Oscura | Benedizione | 6 | si | Come Benedizione, ma per i non-morti: se lanciata su un vivente agisce invece come incantesimo d'attacco, infliggendo danno. |
| Elargisci Benedizione | Benedizione | 15 | si | Pone una benedizione su una fontana o sorgente: chiunque vi beva riceve il beneficio di Benedizione, ma un non-morto che beve subisce danno. |

#### Frenesia

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| Lama della Furia | Frenesia | 20 | si | Avvolge un'arma in fiamme magiche furiose, aumentandone di molto il danno inflitto. |

#### Scudo Elementale: scudi, benedizioni e parole

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| Scudo di Fuoco | Scudo Elementale | 20 | no | Crea una barriera elementale che infligge danno a chiunque colpisca il lanciatore in combattimento. |
| Scudo di Gelo | Scudo Elementale | 20 | no | Come Scudo di Fuoco, ma di ghiaccio. |
| Scudo di Fulmine | Scudo Elementale | 20 | no | Come Scudo di Fuoco, ma di fulmini. |
| Benedizione di Cthugha | Scudo Elementale | 28 | no | Concede immunita' al danno di fuoco. |
| Benedizione di Ithaqua | Scudo Elementale | 28 | no | Concede immunita' al danno da freddo. |
| Benedizione di Yog | Scudo Elementale | 28 | no | Concede immunita' al danno da fulmine. |
| Benedizione di Tsathoggua | Scudo Elementale | 28 | no | Concede immunita' al danno da armi. |
| Parola di Cthugha | Scudo Elementale | 18 | no | Concede resistenza (non immunita' completa) al danno di fuoco. |
| Parola di Ithaqua | Scudo Elementale | 18 | no | Concede resistenza al danno da freddo. |
| Parola di Yog | Scudo Elementale | 18 | no | Concede resistenza al danno da fulmine. |
| Parola di Tsathoggua | Scudo Elementale | 18 | no | Concede resistenza al danno da armi. |

#### Magia del Soffio: il sesto soffio

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| ⚔ Soffio Stordente | Soffio Stordente | 20 | si | Esala un soffio concussivo che stordisce il bersaglio invece di infliggere danno diretto. |

#### Via dell'Evocatore

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| Richiama Animale | Via dell'Evocatore | 15 | no | Richiama al proprio fianco un seguace perso o separato dal lanciatore. |
| Crea Statuetta | Via dell'Evocatore | 15 | si | Trasforma un seguace del lanciatore in una piccola statuetta, comoda da trasportare. |
| Sacca Dimensionale | Via dell'Evocatore | 15 | no | Apre uno squarcio nello spazio che da' accesso immediato al contenuto del proprio armadietto. |
| ⚔ Guardiano degli Antichi | Via dell'Evocatore | 30 | no | Evoca un potente Guardiano a sorvegliare la stanza, che attacchera' il primo personaggio che vi entra. |
| Evoca Spirito | Via dell'Evocatore | 25 | no | Evoca uno spirito magico e senziente al proprio servizio, capace di lanciare incantesimi. |
| Creazione Minore | Via dell'Evocatore | 12 | no | Forma dal nulla un oggetto a scelta tra una barca, una sacca o un attrezzo (una vanga). |
| Creazione Maggiore | Via dell'Evocatore | 25 | no | Come Creazione Minore, ma con una lista diversa di oggetti: un'incudine, una scaglia d'ambra, delle catene o uno scudo. |

#### Magia del Caos

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| ⚔ Causa Rivolta | Magia del Caos | 30 | no | Scatena le forze del caos nell'intera area, facendo impazzire gli NPC e rendendoli aggressivamente pericolosi. |
| Cambia Sesso | Magia del Caos | 10 | si | Cambia temporaneamente il genere della vittima. |
| ⚔ Caos | Magia del Caos | 28 | no | Apre un canale verso le pure forze arcane dell'universo, che lacerano il lanciatore e l'intera stanza: facile da lanciare, difficilissimo da cui proteggersi. |
| ⚔ Entropia | Magia del Caos | 20 | si | Avvolge il bersaglio in un campo di energia che danneggia il suo equipaggiamento, rendendolo meno utile o del tutto inservibile. |

#### Incantesimi singoli

| Nome | Skill richiesta | Costo mana | Bersaglio | Effetto |
|---|---|---|---|---|
| ⚔ Pioggia Acida | Getto Acido | 30 | no | Crea un acquazzone acido sull'intera area, danneggiando sia i personaggi sia il loro equipaggiamento. |
| ⚔ Agonia | Manipolazione | 25 | si | Un potente incantesimo d'attacco capace di infliggere danno significativo a qualunque personaggio si trovi nella stessa area del lanciatore, senza bisogno di trovarsi nella stessa stanza. |
| ⚔ Paura | Manipolazione | 20 | si | Puo' essere lanciato solo su chi e' impegnato in combattimento: se riesce, la vittima smette di combattere e fugge in preda al terrore (o, se non puo' fuggire, resta comunque incapace di attaccare). |
| ⚔ Paralisi | Manipolazione | 28 | si | Riduce drasticamente la mobilita' del bersaglio, che potra' solo difendersi, mai attaccare. |
| Confondi Cacciatori | Invisibilita' | 12 | no | Nasconde le proprie tracce, impedendo a chiunque di seguirle con successo. |
| ⚔ Consacra Bambola | Vudu' | 20 | si | Combina una bambola voodoo vuota con dei capelli del bersaglio (vedi CUT) per creare una bambola personalizzata, che potra' poi essere usata con VOODOO STAB/TWIST/TEAR per infliggere dolore e danno alla vittima ovunque essa si trovi. |
| Contromagia | Cancellazione | 15 | si | Dissolve un singolo effetto magico attivo sul bersaglio (a differenza di Cancellazione/Dissolvere la Magia, che li rimuovono tutti insieme). |
| Dissolvi Stanza | Cancellazione | 25 | no | Tenta di rimuovere gli effetti magici attivi sull'intera stanza (verificabili con RAFFECTS). |
| Crea Grimorio | Lancio degli Incantesimi | 10 | no | Crea un libro magico su cui annotare le Discipline che si trovano in giro per il mondo (nessun sistema di Discipline esiste ancora in questo porting: il grimorio resta per ora un oggetto reale ma di scena, pronto per quando verra' costruito). |
| ⚔ Maledizione della Mummia | Maledizione | 28 | si | Una versione molto piu' potente dell'incantesimo Maledizione. |
| Distruggi Portale | Portale | 10 | si | Chiude un singolo portale. |
| Dissolvi Portali | Portale | 15 | no | Chiude tutti i portali presenti nella stanza. |
| Portale Divino | Portale | 35 | no | Come Portale, ma capace di attraversare i confini di zona per raggiungere il bersaglio. |
| Personalizza Portale | Portale | 10 | si | Blocca un portale, impedendo a chiunque tranne il lanciatore di attraversarlo. |
| Rilevare il Male | Rilevare il Male | 5 | no | Rivela l'allineamento di chi si trova nei dintorni: i personaggi malvagi appaiono avvolti da un'aura rossa. |
| Rilevare il Bene | Rilevare il Bene | 5 | no | Rivela l'allineamento di chi si trova nei dintorni: i personaggi buoni appaiono avvolti da un'aura verde. |
| ⚔ Esorcismo | Magia Clericale | 30 | si | Un potente incantesimo d'attacco pensato per danneggiare gravemente i non-morti: evoca una raffica di energia sacra. |
| Vista Lunga | Visione | 10 | si | Rivela per un istante le uscite delle stanze adiacenti a quella del bersaglio, come se lo sguardo si estendesse oltre le mura. |
| ⚔ Fatica | Danno Divino | 18 | si | Un incantesimo d'attacco che prosciuga la vitalita' del bersaglio, drenandone il movimento e indebolendone la Forza. |
| ⚔ Colonna di Fuoco | Colonna di Fuoco | 30 | si | Evoca un'enorme colonna di fiamme intense che si abbatte sulla vittima, infliggendo gravi danni da fuoco. |
| Forza del Gigante | Forza (incantesimo) | 20 | si | Una versione piu' potente dell'incantesimo Forza. |
| Forza Divina | Forza (incantesimo) | 32 | si | Una versione ancora piu' potente di Forza del Gigante. |
| ⚔ Colpo di Calore | Palla di Fuoco | 20 | si | Dirige un potente getto di calore contro le armi impugnate dall'avversario, danneggiandole e con una probabilita' di fargliele cadere di mano. |
| Incognito | Maschera di Se' | 15 | si | Come Maschera di Se', ma l'NPC scelto come aspetto non deve trovarsi nella stessa stanza del lanciatore. |
| 🚫 Metamorfosi | Maschera di Se' | 20 | no | Travestirebbe il lanciatore da oggetto inanimato. |
| Infravisione | Visione | 8 | si | Permette di vedere nell'oscurita' piu' totale, incluso quella provocata dall'incantesimo Oscurita'. |
| Oracolo Minore | Chiaroveggenza | 15 | no | Evoca uno spirito oracolare che porta al lanciatore un messaggio criptico dagli Dei. |
| Luce del Mago | Luce Continua | 5 | no | Raccoglie la luce attorno al lanciatore in una piccola sfera, una fonte di luce che dura a lungo (ma non indefinitamente, a differenza di Luce Continua). |
| ⚔ Zap | Missile Magico | 6 | si | Il piu' debole della famiglia Zap/Missile Magico/Zappatore Magico: scaglia un singolo proiettile di energia viola contro il bersaglio. |
| ⚔ Zappatore Magico | Missile Magico | 20 | si | Il piu' potente della famiglia Zap/Missile Magico/Zappatore Magico: scaglia tanti proiettili quanto Missile Magico, ma il doppio piu' potenti ciascuno. |
| Falo' Magico | Lancio degli Incantesimi | 15 | no | Crea un falo' arcano che accelera il recupero di chi vi si riposa accanto, a differenza del comando CAMP funziona anche nelle stanze interne. |
| Scudo di Mana | Scudo Magico | 12 | no | Avvolge il lanciatore in una sfera di energia arcana che migliora la classe armatura e riduce il danno subito: una versione piu' debole ed economica di Scudo Magico. |
| Riserva di Mana | Preparare Pozioni | 0 | no | Consuma tutto il mana del lanciatore per crearne una piccola pillola (circa un quinto del totale), da mangiare in seguito per recuperarlo. |
| Trasferisci Mana | Lancio degli Incantesimi | 10 | si | Trasferisce parte del mana del lanciatore a un altro personaggio. |
| Ancora Materiale | Ancora Psichica | 25 | no | Come Ancora Psichica, ma crea un fulcro magico che sopravvive a morte, disconnessione e persino all'uso di Parola di Richiamo - utilizzabile piu' volte. |
| Parola di Potere | Lancio degli Incantesimi | 8 | no | Un incantesimo generico il cui effetto dipende dalla parola pronunciata e dal contesto esatto (di solito parte di una quest): da solo non fa nulla. |
| ⚔ Urlo Primordiale | Voce | 22 | si | Usa energia arcana per amplificare la voce del lanciatore in un urlo che infligge danno al bersaglio. |
| Ristoro (incantesimo) | Ristoro | 8 | si | Ripristina una piccola quantita' di movimento. |
| Ripristina Arto | Ripristina Arto | 20 | si | Ripristina la funzionalita' di un arto ferito. |
| ⚔ Silenzio | Ammutolire | 20 | no | Come Ammutolire, ma per l'intera stanza: chiunque vi si trovi ne soffre gli effetti finche' non se ne va. |
| ⚔ Lentezza | Fretta | 15 | si | L'opposto di Fretta: riduce temporaneamente la Destrezza del bersaglio, rallentandolo in combattimento. |
| Passo Leggero | Ristoro | 15 | si | Come Ristoro, ma ripristina una quantita' di movimento molto maggiore. |
| Vera Invisibilita' | Vera Invisibilita' | 40 | no | Una versione molto piu' potente di Invisibilita': dura di piu', resta attiva anche entrando in combattimento, e nasconde il lanciatore anche da chi puo' Rilevare l'Invisibile. |
| Vera Vista | Rilevare la Magia | 15 | si | Permette di vedere attraverso gli effetti di Maschera di Se'/Incognito, rivelando la vera identita' di chi li ha usati. |
## Note di ambientazione per gli incantesimi più insoliti

Alcuni incantesimi non sono semplici varianti numeriche di "danno" o "cura", ma agganciano sistemi di gioco interi o portano con sé un peso narrativo particolare. Meritano un approfondimento a parte.

### Cammino Astrale ed Esplosione Astrale

**Cammino Astrale** (skill Magia Mentale) è probabilmente l'incantesimo di esplorazione più caratteristico del gioco: distacca la mente del lanciatore dal proprio corpo fisico e la trasferisce in un corpo astrale, lasciando il corpo originale inerme (ma al sicuro) nel punto in cui si trovava. Esplorare in forma astrale è deliberatamente reso quasi privo di rischi — la maggior parte delle creature del mondo non può nemmeno percepire, tanto meno colpire, un corpo astrale — con un'unica, precisa eccezione: **Esplosione Astrale**, l'unico incantesimo capace di infliggere danno a chi si trova in questo stato. Per tornare al proprio corpo si usa il comando `return`. Insieme, i due incantesimi formano un piccolo sotto-gioco di rischio calcolato: chi padroneggia entrambi può esplorare l'ignoto in relativa sicurezza, ma un duello fra due maghi entrambi in forma astrale è un confronto a parte, quasi invisibile a chiunque altro nella stanza.

### La famiglia Onirica e le Dreamlands

I sei incantesimi della skill **Magia Onirica** — Trance, Vera Dormienza, Risveglio Brusco, Sogno Ricorrente, Sonno Incantato e Sonno Maledetto — si agganciano al sistema delle Dreamlands, la dimensione onirica lovecraftiana già presente nel porting (vedi il capitolo dedicato ai Luoghi). **Trance** si limita a rendere più probabile scivolare spontaneamente nelle Dreamlands sognando in modo naturale; **Vera Dormienza** è invece un salto diretto e immediato, che recide il legame del bersaglio col mondo reale trascinandone il corpo fisico intero nel regno dei sogni. **Sonno Incantato** e **Sonno Maledetto** condividono lo stesso meccanismo di "sonno immediato che sfocia in sogno", ma con un esito narrativo opposto: il primo garantisce un sogno sicuro e privo di incubi, il secondo scaraventa la vittima in un incubo pericoloso — la differenza fra i due è puramente nell'intento (curativo o offensivo) di chi lancia l'incantesimo, non nel meccanismo. **Risveglio Brusco** e **Sogno Ricorrente** gestiscono infine il percorso di ritorno: il primo strappa via un sognatore riportandolo bruscamente alla realtà, il secondo fa l'opposto, rispedendo un dormiente sveglio al punto esatto del proprio ultimo sogno.

### Negromanzia: creare e controllare i non-morti

La skill **Negromanzia** raccoglie dieci incantesimi legati alla morte e ai non-morti, il nucleo tematico più cupo del sistema magico. **Anima Morto** e **Mummifica** rianimano un cadavere in uno zombie o in una mummia senz'anima, totalmente obbedienti al lanciatore — la differenza fra i due è puramente estetica/di lore, non meccanica. **Sosia** va oltre, creando una replica non-morta del lanciatore stesso, utilizzabile come un famiglio al proprio fianco. **Profana** e **Inquietudine** riempiono un'intera area di un'influenza malvagia: il primo trasforma la stanza in terra sconsacrata che danneggia chiunque vi si trovi con un allineamento buono, il secondo aumenta la probabilità che i cadaveri presenti nell'area si rianimino da soli in mostri ostili, senza bisogno che nessuno lanci nulla su di loro. **Pugno di Azathoth**, il culmine della famiglia insieme a **Lich** (vedi sotto), è un incantesimo d'attacco capace di uccidere il bersaglio all'istante — e infligge comunque un danno pesante anche quando l'uccisione istantanea non scatta.

### Vudù: la bambola personalizzata

L'unico incantesimo della skill **Vudù**, **Consacra Bambola**, è il fulcro di un intero sotto-sistema che si estende oltre il semplice `CAST`. Per crearla servono: un rating sufficiente nella skill, una bambola voodoo vuota e dei capelli del bersaglio (ottenibili col comando `cut`); lanciando poi Consacra Bambola su quei due componenti si ottiene una bambola personalizzata e legata a quella specifica vittima. Una volta pronta, la bambola si manipola con comandi dedicati fuori da `CAST`: `voodoo stab` è poco più di un avvertimento doloroso, `voodoo twist` infligge danno sia alla bambola sia alla vittima, mentre `voodoo tear` distrugge la bambola infliggendo dolore e danno molto gravi — potenzialmente letali — alla vittima, ovunque essa si trovi nel mondo. È l'unico modo del gioco per colpire un bersaglio a prescindere dalla sua posizione senza bisogno di un incantesimo di localizzazione o di viaggio.

### Possessione: abitare corpi altrui

**Possessione Minore** e **Possessione Maggiore** (quest'ultima capace di funzionare anche su NPC più potenti) spostano letteralmente la mente del lanciatore nel corpo di un NPC, che diventa utilizzabile esattamente come il proprio personaggio finché non lo si abbandona col comando `return` o finché quel corpo non muore — nel qual caso la mente del lanciatore torna incolume al proprio corpo originale. È una delle poche meccaniche del gioco che permette di "diventare", temporaneamente, qualcun altro.

### Duello Magico e la Via del Duellante

**Duello Magico** apre un confronto arcano dedicato fra due contendenti, che durante il suo svolgimento smettono di usare le normali tecniche di combattimento fisico per affrontarsi con la pura forza dei propri poteri: il comando dedicato `duel off/def <mana>` permette di investire mana extra per rafforzare temporaneamente attacco o difesa nel corso dello scontro. È il fulcro dell'intera skill **Via del Duellante**, che raccoglie anche gli incantesimi offensivi più devastanti (e pericolosi da padroneggiare) del gioco: **Ira di Cthugha**, capace di infliggere danni fra i più alti dell'intero registro — al punto che la fonte stessa avverte che più di un incantatore si è fatto seriamente male cercando di dominarla — e la sua controparte **Ira di Ithaqua**, che infligge lo stesso genere di potenza ma come danno stordente anziché letale.

### Magia degli Antichi e Magia Divina: toccare il potere degli Immortali

Due famiglie distinte condividono un tratto insolito: interagiscono direttamente con gli Antichi (gli Immortali/staff del gioco). **Mortalizza** (Magia Divina) rimuove la natura divina e invulnerabile di un Antico, rendendolo — teoricamente — uccidibile; **Evoca Antico** ne teletrasporta uno specifico fino alla posizione del lanciatore. La fonte stessa, e di riflesso il porting, invita alla massima cautela nell'uso di entrambi: sono incantesimi pensati più per situazioni narrative eccezionali concordate con lo staff che per un uso quotidiano.

### Magia del Caos

I quattro incantesimi della skill omonima condividono un'estetica di instabilità pura. **Caos** è descritto come facile da lanciare ma difficilissimo da cui proteggersi: apre un canale verso le forze arcane grezze dell'universo, che feriscono chiunque si trovi nella stanza, lanciatore incluso. **Causa Rivolta** scatena le stesse forze su scala d'area, facendo impazzire gli NPC presenti e rendendoli aggressivi senza controllo.

## Incantesimi dichiarati disabilitati o fuori scope

### Disabilitati esplicitamente dalla fonte originale

Due incantesimi del registro sono dichiarati **disabilitati direttamente dal sito originale**, non da una scelta del porting: il codice li implementa comunque come lanciabili (superano la canalizzazione, consumano mana come ogni altro incantesimo), ma la loro funzione di effetto li fa sempre fallire con un messaggio narrativo onesto, invece di produrre l'effetto che il loro nome promette.

- **Lich** (skill Negromanzia): trasformerebbe permanentemente il lanciatore in un Lich non-morto. La pagina originale segnala esplicitamente: *"NOTE: This spell is currently disabled"*. In questo porting, diventare un Lich resta possibile **solo** tramite il comando `subrace` riservato allo staff (vedi `world/sottorazze.py`), mai lanciando questo incantesimo — coerentemente con quanto la fonte stessa dichiara.
- **Metamorfosi** (skill Maschera di Se'): travestirebbe il lanciatore da oggetto inanimato. La pagina originale la segnala altrettanto esplicitamente come temporaneamente disabilitata. Il porting onora questa disabilitazione esattamente come per Lich.

In entrambi i casi, tentare di lanciare l'incantesimo produce un messaggio in-character che allude a un potere "che si blocca a metà" — un modo di rendere visibile in gioco, senza rompere l'immersione con un errore tecnico, che quel potere resta volutamente fuori portata.

### Incantesimi "di scena": nessun effetto meccanico reale da rimuovere

Un secondo gruppo, più piccolo, non è disabilitato dalla fonte ma dichiarato dal porting come **puramente di scena**: l'incantesimo si lancia e riesce normalmente, e nella maggior parte dei casi produce comunque un oggetto reale nel mondo di gioco, ma la sua funzione meccanica "vera" dipende da un sistema di supporto che questo porting non ha (ancora) costruito.

- **Crea Seme** (Via della Natura): nella fonte il seme creato si può piantare col comando `plant`, dando origine a un sistema di coltivazione. Nessun sistema di questo tipo esiste ancora in questo porting: il seme resta un oggetto reale ma puramente di scena.
- **Crea Grimorio** (Lancio degli Incantesimi, ricevuto automaticamente al raggiungimento di un rating sufficiente): nella fonte serve ad annotare le "Discipline" reperibili in giro per il mondo. Nessun sistema di Discipline esiste ancora in questo porting: il grimorio è un oggetto reale pronto per quando quel sistema verrà eventualmente costruito.
- **Parola di Potere** (Lancio degli Incantesimi, anch'esso automatico): il suo effetto dipende dalla parola pronunciata e dal contesto esatto, normalmente parte di una quest specifica. Nessuna quest di questo porting lo richiede ancora: da solo, oggi, non fa nulla.
- **Universalità** (Taumaturgia): permetterebbe a un oggetto di esistere in ogni zona e area del mondo. Questo porting non impone alcuna restrizione di zona sul trasporto di oggetti, quindi non c'è alcuna limitazione reale da rimuovere: l'incantesimo resta lanciabile (con la stessa probabilità di distruggere l'oggetto nel tentativo delle altre magie di Taumaturgia) ma senza alcun effetto meccanico da annullare.

Questi quattro casi sono l'eccezione, non la regola: a parte questi e i due incantesimi disabilitati sopra, **tutti gli altri 229 incantesimi del registro hanno un effetto meccanico reale e verificabile** in `world/magic.py` — nessun buco silenzioso, nessun incantesimo che "finge" di funzionare senza fare nulla.
