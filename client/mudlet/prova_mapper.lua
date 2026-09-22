-- Banco di prova per cthulhumud_mapper.lua.
--
-- Uso:  texlua prova_mapper.lua cthulhumud_mapper.lua stanze_prova.lua
--
-- (texlua arriva con TeX Live ed e' un interprete Lua a tutti gli
-- effetti: comodo perche' spesso e' gia' installato.)
--
-- Rifa' in Lua puro le funzioni di Mudlet che il mappatore usa, tenendo
-- il conto di come vengono chiamate, e ci fa passare dentro pacchetti
-- Room.Info VERI catturati dal server. Non sostituisce una prova dentro
-- Mudlet - le funzioni qui sono finte - ma verifica la logica: che le
-- stanze vengano create, che le uscite cardinali finiscano in setExit e
-- quelle con nome proprio in addSpecialExit, e che le sigle passate a
-- setExit siano quelle che Mudlet accetta davvero.

local registro = {
  stanze = {}, nomi = {}, coordinate = {}, aree = {},
  uscite = {}, speciali = {}, errori = {},
}

-- Le sigle che setExit() di Mudlet accetta. Qualunque altra cosa viene
-- segnalata come errore: e' esattamente il difetto che questa prova
-- esiste per impedire (prima ci finivano "north", "northeast", ...).
local SIGLE_VALIDE = {
  n=true, ne=true, e=true, se=true, s=true, sw=true, w=true, nw=true,
  up=true, down=true, ["in"]=true, out=true,
}

function roomExists(id) return registro.stanze[id] == true end
function addRoom(id) registro.stanze[id] = true; return true end
function setRoomName(id, nome) registro.nomi[id] = nome end
function setRoomCoordinates(id, x, y, z) registro.coordinate[id] = {x, y, z} end
function getRoomCoordinates(id)
  local c = registro.coordinate[id]
  if not c then return 0, 0, 0 end
  return c[1], c[2], c[3]
end
function getAreaTable() return registro.aree end
function addAreaName(nome)
  local n = 1
  for _ in pairs(registro.aree) do n = n + 1 end
  registro.aree[nome] = n
  return n
end
function setRoomArea(id, area) registro.nomi[id .. "_area"] = area end
function setExit(da, a, direzione)
  if not SIGLE_VALIDE[direzione] then
    table.insert(registro.errori,
      string.format("setExit ha ricevuto la direzione '%s', che Mudlet NON accetta", tostring(direzione)))
    return false
  end
  registro.uscite[#registro.uscite + 1] = {da, a, direzione}
  return true
end
function addSpecialExit(da, a, comando)
  registro.speciali[#registro.speciali + 1] = {da, a, comando}
  return true
end
function centerview(id) registro.ultima_centrata = id end
function updateMap() end
function cecho(t) registro.ultimo_cecho = t end
function setBorderBottom(n) registro.bordo = n end
function openMapWidget() registro.mappa_aperta = true end
function createMapper() registro.mappa_aperta = true end
Geyser = {
  Container = {new = function(_, o) o.show = function() end; o.hide = function() end; return o end},
  Gauge = {new = function(_, o)
      o.front = {setStyleSheet = function() end}
      o.setValue = function() end
      return o
    end},
}

gmcp = {}

dofile(arg[1])   -- carica il mappatore vero

-- ---------------------------------------------------------------- prova
local stanze_json = arg[2]

-- I dati arrivano gia' come tabella Lua, generata da Python dal JSON
-- catturato: un parser JSON scritto a mano in Lua aveva tagliato i
-- blocchi alla prima graffa chiusa, perdendo le uscite speciali - e il
-- banco di prova accusava il mappatore di un difetto che era suo.
local stanze = dofile(stanze_json)
print(string.format("pacchetti Room.Info di prova: %d", #stanze))

-- Simula il percorso: comando digitato, poi arrivo della stanza.
local percorso = {"nord", "sud", "commissariato", "fuori"}
for i, s in ipairs(stanze) do
  cthulhuEvento("sysDataSendRequest", percorso[i] or "")
  gmcp.Room = {Info = s}
  cthulhuEvento("gmcp.Room.Info")
end

gmcp.Char = {Vitals = {hp=2, maxhp=53, mana=21, maxmana=21,
                       mv=133, maxmv=133, sanity=90, maxsanity=105}}
cthulhuEvento("gmcp.Char.Vitals")

-- --------------------------------------------------------------- esito
local n_stanze = 0
for _ in pairs(registro.stanze) do n_stanze = n_stanze + 1 end
local n_aree = 0
for _ in pairs(registro.aree) do n_aree = n_aree + 1 end

print("")
print(string.format("stanze create          : %d", n_stanze))
print(string.format("aree create            : %d", n_aree))
print(string.format("uscite cardinali poste : %d", #registro.uscite))
print(string.format("uscite speciali poste  : %d", #registro.speciali))
print(string.format("ultima stanza centrata : %s", tostring(registro.ultima_centrata)))
print(string.format("barre accese all'avvio : %s", tostring(cthulhu.stato.attive)))

print("")
print("uscite cardinali registrate:")
for _, u in ipairs(registro.uscite) do
  print(string.format("   %d -[%s]-> %d", u[1], u[3], u[2]))
end
print("uscite speciali registrate:")
for _, u in ipairs(registro.speciali) do
  print(string.format("   %d -[%s]-> %d", u[1], u[3], u[2]))
end

print("")
if #registro.errori > 0 then
  print("ERRORI:")
  for _, e in ipairs(registro.errori) do print("   " .. e) end
  os.exit(1)
else
  print("nessun errore: tutte le direzioni passate a setExit sono valide")
end
