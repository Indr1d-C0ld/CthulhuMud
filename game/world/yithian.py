"""
Yithian MINDTRANSFER (Fase G, nona tornata): confermato dalla scansione
esaustiva (guides_yithianfaq.txt, un'intera pagina di FAQ dedicata) come
un sottosistema completo e specifico della razza, finora assente dal
porting oltre a un commento. Riassunto dei punti confermati verbatim:

- Gli Yithiani sono fisicamente deboli: passano la maggior parte del
  tempo a possedere corpi di NPC con MINDTRANSFER invece di esplorare
  nel proprio corpo.
- Costo di MINDTRANSFER: mana E movimento, ciascuno pari a 10 volte il
  livello dell'NPC bersaglio. Molto difficile (quasi impossibile)
  possedere un NPC di livello superiore al proprio; se il tentativo
  fallisce contro un NPC piu' forte, l'NPC diventa ostile e attacca.
- Mentre si possiede un NPC, il corpo Yithiano originale resta immobile
  e "cieco" (nessuna informazione sensoriale) nella stanza dov'era.
  RETURN riporta la mente al corpo originale in qualunque momento.
- L'esperienza da uccisione, mentre si possiede un NPC, si divide a
  meta' tra il corpo Yithiano e il corpo posseduto (entrambi salgono di
  livello, piu' lentamente).
- Se il corpo posseduto muore: si ritorna automaticamente al corpo
  Yithiano; la perdita di XP alla morte e' MINORE di quella normale (qui:
  meta'); il cadavere dell'NPC NON va alla morgue (resta dov'e' morto,
  gia' il comportamento di default per gli NPC) e gli oggetti che
  portava restano sul cadavere, non tornano al corpo Yithiano.
- YITH ADAPT <skill> [volte]: da usare mentre si possiede un NPC, spende
  le PRACTICE del corpo Yithiano (non del corpo posseduto) per alzare
  una skill del corpo Yithiano. Il rating di base e' la MEDIA tra il
  rating dell'NPC e quello dello Yithian in quella skill, poi modificato
  dalla media del rating "Insegnamento" (Teach) di entrambi; solo le
  skill con un rating finale sopra 25 sono disponibili nella lista.
- YITH ABDUCT: disponibile solo mentre si possiede un NPC, lo trasporta
  nella stanza di partenza della Biblioteca Yithiana.

I cristalli-focus Yithiani (Focus Crystal), dichiarati fuori scope in
questa tornata (Fase G, nona), sono stati poi costruiti in Fase K,
settima tornata - vedi world/focus_crystal.py.
"""

CAP_ADATTAMENTO_YITH = 25   # sotto questo rating finale, la skill non compare nella lista YITH ADAPT
PENALITA_XP_MORTE_YITHIAN = 0.5  # la perdita di XP alla morte del corpo posseduto e' dimezzata


def costo_mindtransfer(npc):
    livello = npc.livello_per_equip() if hasattr(npc, "livello_per_equip") else 1
    return 10 * max(1, livello)


def possibilita_successo_mindtransfer(yithiano, npc):
    """Molto difficile (quasi impossibile) possedere un NPC di livello
    superiore al proprio - formula esplicita, non specificata dalla
    fonte in dettaglio numerico."""
    divario = npc.livello_per_equip() - yithiano.livello_per_equip()
    base = 80 - divario * 15
    return max(5, min(95, base))


def puo_adattare(rating_npc, rating_yithian, teach_npc, teach_yithian):
    """Ritorna il rating finale disponibile per YITH ADAPT, o None se
    sotto CAP_ADATTAMENTO_YITH."""
    base = (rating_npc + rating_yithian) / 2
    modificatore_teach = (teach_npc + teach_yithian) / 2
    finale = base * (0.5 + modificatore_teach / 100)
    return finale if finale > CAP_ADATTAMENTO_YITH else None
