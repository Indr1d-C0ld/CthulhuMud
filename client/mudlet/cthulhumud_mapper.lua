-- ---------------------------------------------------------------------
-- CthulhuMUD Redux - mappatore automatico e barre di stato per Mudlet
--
-- Si appoggia ai pacchetti GMCP che il server manda (vedi
-- game/world/gmcp.py):
--
--   Room.Info    {num, name, area, exits, specials}
--   Char.Vitals  {hp, maxhp, mana, maxmana, mv, maxmv, sanity, maxsanity}
--
-- Perche' un mappatore su misura invece del Generic Mapper di Mudlet:
-- nel mondo di CthulhuMUD il 54% delle uscite ha un nome proprio
-- ("tribunale", "navata", "fuori") invece di una direzione cardinale.
-- Il server le manda percio' in due campi separati - "exits" per quelle
-- cardinali, "specials" per le altre - e questo script le tratta di
-- conseguenza: le prime vanno sulla griglia, le seconde diventano
-- collegamenti speciali cliccabili. Un mapper generico dovrebbe
-- indovinare quale sia quale, e sbaglierebbe.
--
-- COMANDI DISPONIBILI IN GIOCO
--   mappa        apre/aggancia la finestra della mappa
--   mappadiag    diagnostica: dice cosa arriva e cosa manca
--   barre on|off mostra o nasconde le barre di stato in basso
-- ---------------------------------------------------------------------

cthulhu = cthulhu or {}
cthulhu.mapper = cthulhu.mapper or {}
cthulhu.ultimoErrore = nil

-- Direzioni che Mudlet sa disporre sulla griglia.
--
-- ATTENZIONE alla forma del nome: setExit() accetta le sigle BREVI
-- ("n", "ne", "up"...) e NON i nomi lunghi ("north", "northeast").
-- La prima versione di questo script passava i nomi lunghi, e siccome
-- setExit non solleva un errore ma restituisce false, la mappa restava
-- vuota senza che nulla lo segnalasse. Le sigle qui sotto sono le stesse
-- che il server manda in "exits", quindi non serve alcuna conversione:
-- la tabella tiene solo lo spostamento sulla griglia.
cthulhu.mapper.direzioni = {
  n    = {dx =  0, dy =  1, dz =  0},
  s    = {dx =  0, dy = -1, dz =  0},
  e    = {dx =  1, dy =  0, dz =  0},
  w    = {dx = -1, dy =  0, dz =  0},
  ne   = {dx =  1, dy =  1, dz =  0},
  nw   = {dx = -1, dy =  1, dz =  0},
  se   = {dx =  1, dy = -1, dz =  0},
  sw   = {dx = -1, dy = -1, dz =  0},
  up   = {dx =  0, dy =  0, dz =  1},
  down = {dx =  0, dy =  0, dz = -1},
  ["in"] = {dx =  0, dy =  0, dz =  0},
  out  = {dx =  0, dy =  0, dz =  0},
}

cthulhu.mapper.stanza_precedente = nil
cthulhu.mapper.ultima_direzione = nil
cthulhu.mapper.stanze_create = 0

-- Ricorda l'ultimo comando digitato: serve a capire in che direzione ci
-- si e' mossi, per posizionare una stanza nuova accanto a quella da cui
-- si arriva. Senza questo, ogni stanza nuova finirebbe nell'origine.
function cthulhu.mapper.ricordaComando(comando)
  local c = string.lower(comando or "")
  local abbreviazioni = {
    n = "n", nord = "n", s = "s", sud = "s",
    e = "e", est = "e", o = "w", ovest = "w",
    ne = "ne", nordest = "ne", no = "nw", nordovest = "nw",
    se = "se", sudest = "se", so = "sw", sudovest = "sw",
    su = "up", alto = "up", giu = "down", basso = "down",
    dentro = "in", fuori = "out",
  }
  cthulhu.mapper.ultima_direzione = abbreviazioni[c]
  cthulhu.mapper.ultimo_comando = c
end

local function areaDi(nome)
  local aree = getAreaTable() or {}
  if aree[nome] then return aree[nome] end
  local id = addAreaName(nome)
  return id
end

local function coordinateNuove()
  -- Posiziona la stanza accanto a quella da cui arriviamo, nella
  -- direzione in cui ci siamo mossi. Se non lo sappiamo (teletrasporto,
  -- login, uscita con nome proprio) la mettiamo di fianco, cosi' resta
  -- visibile e trascinabile a mano invece di sovrapporsi all'origine.
  local prec = cthulhu.mapper.stanza_precedente
  if not prec or not roomExists(prec) then
    return 0, 0, 0
  end
  local x, y, z = getRoomCoordinates(prec)
  local d = cthulhu.mapper.direzioni[cthulhu.mapper.ultima_direzione or ""]
  if d then
    return x + d.dx, y + d.dy, z + d.dz
  end
  return x + 2, y, z
end

local function aggiornaMappa()
  local info = gmcp.Room and gmcp.Room.Info
  if not info or not info.num then return end
  local id = tonumber(info.num)

  if not roomExists(id) then
    addRoom(id)
    local x, y, z = coordinateNuove()
    setRoomCoordinates(id, x, y, z)
    cthulhu.mapper.stanze_create = cthulhu.mapper.stanze_create + 1
  end

  setRoomName(id, info.name or ("stanza " .. id))
  if info.area then
    setRoomArea(id, areaDi(info.area))
  end

  -- Uscite cardinali: vanno sulla griglia. Si collegano solo verso
  -- stanze gia' note; quelle ancora inesplorate verranno collegate
  -- quando ci si arrivera' davvero.
  for sigla, destinazione in pairs(info.exits or {}) do
    local dest = tonumber(destinazione)
    if cthulhu.mapper.direzioni[sigla] and dest and roomExists(dest) then
      setExit(id, dest, sigla)          -- sigla breve: vedi la nota sopra
    end
  end

  -- Uscite con nome proprio: collegamenti speciali, cliccabili sulla
  -- mappa e utilizzabili dallo speedwalk.
  for nome, destinazione in pairs(info.specials or {}) do
    local dest = tonumber(destinazione)
    if dest and roomExists(dest) then
      addSpecialExit(id, dest, nome)
    end
  end

  cthulhu.mapper.stanza_precedente = id
  cthulhu.mapper.ultima_direzione = nil
  centerview(id)
  updateMap()
end

-- Un errore qui dentro non deve passare inosservato: la prima versione
-- falliva in silenzio e sembrava che il pacchetto non fosse installato.
function cthulhu.mapper.aggiorna()
  local ok, err = pcall(aggiornaMappa)
  if not ok then
    cthulhu.ultimoErrore = tostring(err)
    cecho("\n<red>[mappa] errore: " .. tostring(err) .. "<reset>\n")
    cecho("<dark_orange>Scrivi MAPPADIAG per un quadro completo.<reset>\n")
  end
end

-- ------------------------------------------------------- barre di stato
--
-- Volutamente SPENTE all'avvio: il pannello laterale di Mudlet mostra
-- gia' Vita, Mana e Movimento leggendoli dal nostro stesso Char.Vitals,
-- e delle barre in fondo alla finestra principale coprirebbero l'ultima
-- riga di testo. Restano disponibili con BARRE ON per chi vuole anche la
-- Sanita' mentale, che il pannello laterale non conosce; in quel caso si
-- riserva lo spazio col bordo inferiore, cosi' non coprono piu' nulla.
cthulhu.stato = cthulhu.stato or {}
cthulhu.stato.attive = false
local ALTEZZA_BARRE = 28   -- pixel riservati in fondo quando sono accese

function cthulhu.stato.crea()
  if cthulhu.stato.contenitore then return end
  cthulhu.stato.contenitore = Geyser.Container:new({
    name = "cthulhu_stato",
    x = 0, y = -ALTEZZA_BARRE, width = "100%", height = ALTEZZA_BARRE,
  })
  local function barra(nome, x, colore)
    local g = Geyser.Gauge:new({name = nome, x = x, y = "0%",
                                width = "24%", height = "100%"},
                               cthulhu.stato.contenitore)
    g.front:setStyleSheet("background-color: " .. colore .. ";")
    return g
  end
  cthulhu.stato.hp     = barra("cthulhu_hp",     "0%",  "rgb(140,20,20)")
  cthulhu.stato.mana   = barra("cthulhu_mana",   "25%", "rgb(40,60,150)")
  cthulhu.stato.mv     = barra("cthulhu_mv",     "50%", "rgb(40,120,50)")
  -- verde tossico: la stessa famiglia cromatica che il gioco usa per il
  -- Mythos e la magia (game/world/colori.py)
  cthulhu.stato.sanity = barra("cthulhu_sanity", "75%", "rgb(90,160,40)")
end

function cthulhu.stato.mostra(acceso)
  cthulhu.stato.attive = acceso and true or false
  if cthulhu.stato.attive then
    cthulhu.stato.crea()
    -- riserva lo spazio: senza questo le barre si sovrappongono
    -- all'ultima riga di testo dell'ambientazione
    setBorderBottom(ALTEZZA_BARRE)
    cthulhu.stato.contenitore:show()
    cthulhu.stato.aggiorna()
    cecho("\n<green_yellow>Barre di stato accese (con Sanita' mentale).<reset>\n")
  else
    if cthulhu.stato.contenitore then cthulhu.stato.contenitore:hide() end
    setBorderBottom(0)
    cecho("\n<green_yellow>Barre di stato spente: restano quelle del pannello laterale.<reset>\n")
  end
end

function cthulhu.stato.aggiorna()
  if not cthulhu.stato.attive then return end
  local v = gmcp.Char and gmcp.Char.Vitals
  if not v then return end
  cthulhu.stato.crea()
  local function imposta(barra, valore, massimo, etichetta)
    valore, massimo = tonumber(valore) or 0, tonumber(massimo) or 0
    if massimo <= 0 then massimo = 1 end
    barra:setValue(math.min(valore, massimo), massimo,
                   string.format("<center>%s %d/%d</center>", etichetta, valore, massimo))
  end
  imposta(cthulhu.stato.hp,     v.hp,     v.maxhp,     "Vita")
  imposta(cthulhu.stato.mana,   v.mana,   v.maxmana,   "Mana")
  imposta(cthulhu.stato.mv,     v.mv,     v.maxmv,     "Movimento")
  imposta(cthulhu.stato.sanity, v.sanity, v.maxsanity, "Sanita'")
end

-- ------------------------------------------------------ finestra mappa
function cthulhu.apriMappa()
  -- createMapper con coordinate crea il mappatore dentro la finestra
  -- principale; senza, Mudlet usa il pannello agganciato se c'e'.
  if openMapWidget then
    openMapWidget()
    cecho("\n<green_yellow>Finestra mappa aperta.<reset>\n")
  else
    createMapper(0, 0, 400, 400)
    cecho("\n<green_yellow>Mappatore creato nella finestra principale.<reset>\n")
  end
  if cthulhu.mapper.stanza_precedente then
    centerview(cthulhu.mapper.stanza_precedente)
  end
  updateMap()
end

-- ------------------------------------------------------- diagnostica
function cthulhu.diagnostica()
  local function riga(etichetta, valore, buono)
    local colore = buono and "green_yellow" or "orange_red"
    cecho(string.format("  <white>%-34s<%s>%s<reset>\n", etichetta, colore, tostring(valore)))
  end
  cecho("\n<green_yellow>--- diagnostica CthulhuMUD Redux ---<reset>\n")

  local haGmcp = gmcp ~= nil
  riga("tabella gmcp presente", haGmcp, haGmcp)

  local info = gmcp and gmcp.Room and gmcp.Room.Info
  riga("gmcp.Room.Info ricevuto", info ~= nil, info ~= nil)
  if info then
    riga("  stanza corrente", tostring(info.num) .. " - " .. tostring(info.name), true)
    riga("  area", tostring(info.area), true)
    local nc, ns = 0, 0
    for _ in pairs(info.exits or {}) do nc = nc + 1 end
    for _ in pairs(info.specials or {}) do ns = ns + 1 end
    riga("  uscite cardinali", nc, true)
    riga("  uscite con nome proprio", ns, true)
    local esiste = roomExists(tonumber(info.num))
    riga("  esiste nella mappa", esiste, esiste)
  end

  local v = gmcp and gmcp.Char and gmcp.Char.Vitals
  riga("gmcp.Char.Vitals ricevuto", v ~= nil, v ~= nil)

  local aree = getAreaTable() or {}
  local na = 0
  for _ in pairs(aree) do na = na + 1 end
  riga("aree nella mappa", na, na > 0)
  riga("stanze create da questa sessione", cthulhu.mapper.stanze_create,
       cthulhu.mapper.stanze_create > 0)
  riga("barre di stato in basso", cthulhu.stato.attive and "accese" or "spente", true)
  riga("ultimo errore del mappatore", cthulhu.ultimoErrore or "nessuno",
       cthulhu.ultimoErrore == nil)

  if not info then
    cecho("\n<orange_red>Non e' arrivato alcun Room.Info.<reset> Muoviti di una stanza:\n")
    cecho("il server lo manda a ogni spostamento e al collegamento.\n")
    cecho("Se non arriva comunque, il GMCP e' spento nel client.\n")
  elseif na == 0 then
    cecho("\n<orange_red>I dati arrivano ma la mappa e' vuota.<reset> Prova <white>MAPPA<reset>.\n")
  else
    cecho("\n<green_yellow>Tutto a posto.<reset> Se non vedi nulla, apri la finestra con <white>MAPPA<reset>.\n")
  end
end

-- ------------------------------------------------------------- avvio
function cthulhu.avvia()
  cecho("\n<green_yellow>CthulhuMUD Redux: pacchetto attivo.<reset>\n")
  cecho("<grey>  MAPPA<reset> apre la mappa  ")
  cecho("<grey>MAPPADIAG<reset> diagnostica  ")
  cecho("<grey>BARRE ON<reset> barre in basso (con Sanita')\n")
end


-- ------------------------------------------------- smistamento eventi
-- Mudlet chiama, per ogni evento registrato, la funzione globale che ha
-- LO STESSO NOME dello script del pacchetto. Il nome dev'essere percio'
-- un identificatore Lua valido, e deve combaciare con <name> nel file
-- .xml: se i due divergono, lo script viene caricato senza errori e non
-- fa semplicemente nulla - un guasto silenzioso.
function cthulhuEvento(nome, ...)
  if nome == "gmcp.Room.Info" then
    cthulhu.mapper.aggiorna()
  elseif nome == "gmcp.Char.Vitals" then
    cthulhu.stato.aggiorna()
  elseif nome == "sysDataSendRequest" then
    -- ogni comando digitato passa di qui: ci serve per sapere in che
    -- direzione ci si e' mossi quando arriva la stanza nuova
    cthulhu.mapper.ricordaComando(...)
  elseif nome == "sysConnectionEvent" then
    cthulhu.mapper.stanza_precedente = nil
    cthulhu.mapper.ultima_direzione = nil
    cthulhu.avvia()
  end
end
