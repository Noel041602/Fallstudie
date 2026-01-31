import pandas as pd
from pyscipopt import Model, quicksum

#----------------------------------------------------------------------------------------
# Daten hard codieren
#----------------------------------------------------------------------------------------

routes_data = [
    {"route_id": "t-4", "distance_total": 250.0, "distance_toll": 150.0, "starttime": 0.28125, "endtime": 0.71875},
    {"route_id": "t-5", "distance_total": 250.0, "distance_toll": 150.0, "starttime": 0.2708333333333333, "endtime": 0.7083333333333334},
    {"route_id": "t-6", "distance_total": 250.0, "distance_toll": 150.0, "starttime": 0.25, "endtime": 0.6875},

    {"route_id": "s-1", "distance_total": 120.0, "distance_toll": 32.0, "starttime": 0.22916666666666666, "endtime": 0.6458333333333334},
    {"route_id": "s-2", "distance_total": 120.0, "distance_toll": 32.0, "starttime": 0.25, "endtime": 0.6666666666666666},
    {"route_id": "s-3", "distance_total": 120.0, "distance_toll": 32.0, "starttime": 0.375, "endtime": 0.6666666666666666},
    {"route_id": "s-4", "distance_total": 120.0, "distance_toll": 32.0, "starttime": 0.2708333333333333, "endtime": 0.6875},

    {"route_id": "w1", "distance_total": 100.0, "distance_toll": 32.0, "starttime": 0.22916666666666666, "endtime": 0.6458333333333334},
    {"route_id": "w2", "distance_total": 100.0, "distance_toll": 32.0, "starttime": 0.3333333333333333, "endtime": 0.75},
    {"route_id": "w3", "distance_total": 100.0, "distance_toll": 32.0, "starttime": 0.28125, "endtime": 0.6979166666666666},
    {"route_id": "w4", "distance_total": 100.0, "distance_toll": 32.0, "starttime": 0.25, "endtime": 0.6666666666666666},
    {"route_id": "w5", "distance_total": 100.0, "distance_toll": 32.0, "starttime": 0.2916666666666667, "endtime": 0.7083333333333334},
    {"route_id": "w6", "distance_total": 100.0, "distance_toll": 32.0, "starttime": 0.22916666666666666, "endtime": 0.6458333333333334},
    {"route_id": "w7", "distance_total": 100.0, "distance_toll": 32.0, "starttime": 0.3020833333333333, "endtime": 0.71875},

    {"route_id": "r1", "distance_total": 285.0, "distance_toll": 259.0, "starttime": 0.75, "endtime": 0.9375},
    {"route_id": "r2", "distance_total": 250.0, "distance_toll": 220.0, "starttime": 0.6875, "endtime": 0.90625},
    {"route_id": "r3", "distance_total": 235.0, "distance_toll": 219.0, "starttime": 0.7395833333333334, "endtime": 0.8958333333333334},

    {"route_id": "h3", "distance_total": 180.0, "distance_toll": 160.0, "starttime": 0.78125, "endtime": 0.9479166666666666},
    {"route_id": "h4", "distance_total": 180.0, "distance_toll": 160.0, "starttime": 0.7708333333333334, "endtime": 0.9375},

    {"route_id": "k1", "distance_total": 275.0, "distance_toll": 235.0, "starttime": 0.6875, "endtime": 0.9375},
]

routes_df = pd.DataFrame(routes_data)

#----------------------------------------------------------------------------------------
# Modell initialisieren 
#----------------------------------------------------------------------------------------
model = Model("Stufe3_Diesel-Elektro_Optimierung")


#----------------------------------------------------------------------------------------
# Indexmengen
#----------------------------------------------------------------------------------------
#Tour
ROUTEN = routes_df.index.tolist()   # Menge aller Touren
     
#LKW
FUHRPARK = range(1, len(ROUTEN)+1)  # Alle geleasten LKWs im Fuhrpark
FTypen = ["Diesel", "E400", "E600"] # Verfügbare LKW-Typen
     
#Zeit
ZEIT = range(0, 96)  # Zeitschritte in 15-Minuten-Intervallen
ZEIT_Nacht = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96)
ZEIT_Tag = (25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72)
     
#Ladeinfrastruktur
STypen = ["Alpitronic-50", "Alpitronic-200", "Alpitronic-400"]
LADEPUNKT = [1, 2]
SAULENBESTAND = [1, 2, 3]
NETZANSCHLUSSERWEITERUNG = ["Trafo", "Speicher"]


#----------------------------------------------------------------------------------------
# Indexmengen
#----------------------------------------------------------------------------------------
# -- Farhzeugtyp --
# Investitonskosten von LKW-Typ t
C_CAPEX_LKW = {"Diesel": 24000.0,
           "E400": 50000.0,
           "E600": 60000.0
}

# Operative Kosten von LKW-Typ t
C_OPEX_LKW = {"Diesel": 6000.0,
          "E400": 5000.0,
          "E600": 6000.0
}

# Engerieverbrauch der LKW-Typ t
VERBRAUCH = {"Diesel": 26.0/100,
             "E400":  20/100, #105.0/100,
             "E600": 20/100 #110.0/100
}

# Batteriekapazität
BATTERIE = {"Diesel": 0.0,
            "E400": 414.0,
            "E600": 621.0
            }

# Steuerkosten von Fahrzeugtyp t
C_STEUER = {"Diesel": 556.0,
            "E400": 0.0,
            "E600": 0.0
}

# Erlös THG von Fahrzeugtyp t
THG = {"Diesel": 0.0,
       "E400": 1000.0,
       "E600": 1000.0
}

# Power Limit, max. Ladeleistung von LKW-Typ t
POWER_LIMIT_LKW = {"Diesel": 0.0,
          "E400": 400.0,
          "E600": 400.0
}


# -- Preise --
# Kraftstoffpreis
P_DIESEL = 1.60

# Stromkosten pro kwH
P_STROM = 0.25

# Leistungspreis pro kW
P_LEISTUNGSPREIS = 150 


# --Tour/Route--
#Gesamte Fahrstrecke der Tour r
DISTANZ_GESAMT = {r: routes_df.loc[r, 'distance_total'] for r in ROUTEN}  #Wir schauen in jeder Spalte Gesamtdistanz in der Tabelle von den Routen und nehmen das für jede ROute raus

#Mautpflichtige STrecke der Tour r
DISTANZ_MAUT = {r: routes_df.loc[r, 'distance_toll'] for r in ROUTEN}  #siehe oben

# Mautgebühr
C_MAUT = 0.34

#Startzeitpunkt der Tour r
START = {r: routes_df.loc[r, 'starttime'] * 96 for r in ROUTEN}

#Endzeitpunkt der Tour r
END = {r: routes_df.loc[r, 'endtime'] * 96 for r in ROUTEN}

#Hilfsvariable ->läuft Route r zu welchen zeitpunkt z
from collections import defaultdict
ROUTE_AKTIV = defaultdict(int)
for r in ROUTEN:
    for z in ZEIT:
        ROUTE_AKTIV[r, z] = 1 if START[r] <= z < END[r] else 0    #Ende kommt raus, weil sonst haben wir anstatt 27 28 Slots (nahc ENde kommt ja kein Slot mehr) + verbruacht zu viel Energie

# Dauer der Route r
ROUTE_DAUER = {
    r: sum(ROUTE_AKTIV[r,z] for z in ZEIT)
    for r in ROUTEN
}


# --Zeit--
#Einsatztage pro Jahr
N_TAGE = 260

# Hilfparameter: Start-Indikator 
for r in ROUTEN:
    for z in ZEIT:
        START_INDIKATOR[r, z] = 1 if ... else 0 agfiahf


# --Ladeinfrastruktur-- 
# Jährliche Kosten Ladeinfrastruktur (Capex + Opex)
C_CAPEX_S = {
    "Alpitronic-50": 3000.0,
    "Alpitronic-200": 10000.0,
    "Alpitronic-400": 16000.0
}

C_OPEX_S = {
    "Alpitronic-50": 1000.0,
    "Alpitronic-200": 1500.0,
    "Alpitronic-400": 2000.0
}

# Power Limit, max. Ladeleistung vom Säulentyp S
POWER_LIMIT_S = {"Alpitronic-50": 50.0,
        "Alpitronic-200": 200.0,
        "Alpitronic-400": 400.0
}

# jährliche Stromgebühr (Grundgebühr)
C_Gebuhr = 1000

# --Netzanschluss-- 
# maximale Netzanschlussleistung
POWER_LIMIT_NETZ = 500

# jährliche Kosten für Transformator 
C_CAPEX_TRAFO = 10000

# maximale zusätzliche Leistung vom Transformator
POWER_LIMIT_TRAFO = 500

# jährliche Kosten des Speichers für die Leistung pro kW
C_CAPEX_SPEICHER_LEISTUNG = 30

# jährliche Kosten des Speichers für die Kappazität pro kWh
C_CAPEX_SPEICHER_KAPPA = 350

# jährliche Wartungskosten des Speichers (2% von den Investitionskosten)
C_CAPEX_SPEICHER_WARTUNGSKOSTEN = 0.02

# Round-Trip-Efficiency des Speichers (98%) (Speicher braucht für sich selbst auch einen ANteil, um sihc selbst zu versorgen)
RTE_SPEICHER = 0.98

# maximale Entladetiefe des Speichers (97,5%)
ENTLADETIEFE_SPEICHER = 0.975


#----------------------------------------------------------------------------------------
# Entscheidungsvariablen
#----------------------------------------------------------------------------------------
# LKW und Routenverteilung
# wenn LKW f die Tour r fährt = 1
lkw_fahrt_r = {}
for f in FUHRPARK:
    for r in ROUTEN:
        lkw_fahrt_r= model.addVar(vtype="B", name=f"LKW_fährt_Route{f}_{r}") 
     
# wenn LKW f den Typ t hat = 1
lkw_hat_typ = {}
for f in FUHRPARK:
    for t in FTypen:
        lkw_hat_typ[f, t] = model.addVar(vtype="B", name=f"LKW_hat_Typ_{f}_{t}") 
     
# Bedeutung: LKW f vom Typ t fährt Route r (ersetzt das Produkt von den ersten beiden -> Modell bleibt linear)
lkw_fahrt_Route_mit_typ = {}
for f in FUHRPARK:
   for r in ROUTEN:
       for t in FTypen:
           lkw_fahrt_Route_mit_typ[f, r, t] = model.addVar(vtype="B", name=f"LKW_fährt_Route_mit_Type{f}_{r}_{t}")

# Wenn LKW f zum Zeitpunkt z an Ladepunkt l lädt = 1
lkw_ladt = {}
for f in FUHRPARK:
    for z in ZEIT:
            for l in LADEPUNKT:
              lkw_ladt[f, z, l] = model.addVar(vtype="B", name=f"LKW_lädt_{f}_{z}_{l}") 

# Batteriestand LKW f zum Zeitpunkt z
soc_lkw = {}
for f in FUHRPARK:
    for z in ZEIT:
        soc_lkw[f, z] = model.addVar(vtype="C", lb=0, name=f"soc_LKW_{f}_{z}")


# --Ladeinfrastruktur-- 
# Maximale Netzleistung zum Zeitpunkt z am Ladepunkt l 
max_leistung_von_ladepunkt = {}
for z in ZEIT:
   for l in LADEPUNKT: 
      max_leistung_von_ladepunkt = model.addVar(vtype="C", lb=0, name=f"Max_Leistung_von_Ladepunkt_{z}_{l}")

# Momente Batterieleistung von LKW f zum Zeitpunkt z an Ladepunkt l (=wie viel Leistung ziehe ich aktuell aus dem Stromnetz)
momentane_leistung_an_lkw = {}
for f in FUHRPARK:
   for z in ZEIT:
      for l in LADEPUNKT: 
         momentane_leistung_an_lkw = model.addVar(vtype="C", lb=0, name=f"Max_Leistung_an_LKW_{f}_{z}_{l}")

# Wenn Säule b Typ s hat = 1
säule_hat_typ = {}
for b in SAULENBESTAND:
    for s in STypen:
        säule_hat_typ[b, s] = model.addVar(vtype="B", name=f"Säule_hat_Typ_{b}_{s}") 

# wenn Lkw f zum Zeitpunkt z mit ladepunkt l verbunden ist = 1
lkw_verbunden_ladepunkt = {}
for f in FUHRPARK:
    for z in ZEIT:
        for l in LADEPUNKT: 
            lkw_verbunden_ladepunkt[b, s] = model.addVar(vtype="B", name=f"LKW_verbunden_Ladepunkt_{f}_{z}_{l}") 


# wenn Ladepunkt l zu Säule b gehört = 1
ladepunkt_gehort_saule = {}
for b in SAULENBESTAND:
    for l in LADEPUNKT: 
        ladepunkt_gehort_saule[b, s] = model.addVar(vtype="B", name=f"LKW_gehört_Ladepunkt_{b}_{l}") 

# Wenn Entscheidung bei Netzwerweiterung n für Trafo = 1
entscheidung_trafo = {}
for n in "Trafo":
    entscheidung_trafo = model.addVar(vtype="B", name=f"Entscheidung_für_Trafo{n}") 

# Wenn Entscheidung bei Netzwerweiterung n für Speicher = 1
entscheidung_speicher = {}
for n in "Speicher":
    entscheidung_trafo = model.addVar(vtype="B", name=f"Entscheidung_für_Speicher{n}")

# festzulegende Leistung des Speichers 
leistung_speicher = {}
for n in "Speicher":
    leistung_speicher = model.addVar(vtype="C", lb=0, name=f"Leistung_des_Speichers_{n}")

# festezulegende Batteriekapazität der Netzschlusserweiterung Speicher zum Zeitpunkt z 
kapa_Speicher = {}
for n in "Speicher":
    for z in ZEIT:
        kapa_speicher = model.addVar(vtype="C", lb=0, name=f"Batteriekapazität_des_Speichers_{n}_{z}")

# Ladezustand der Netzanschlusserweiterung Speicher zum Zeitpunkt z 
soc_speicher = {}
for n in "Speicher":
    for z in ZEIT:
        soc_speicher = model.addVar(vtype="C", lb=0, name=f"Ladezustand_des_Speichers_{n}_{z}")

# Ladeleistung der Netzanschlusserweiterung Speicher zum Zeitpunkt z 
leistung_inSpeicher = {}
for n in "Speicher":
    for z in ZEIT:
        leistung_inSpeicher = model.addVar(vtype="C", lb=0, name=f"Leistung_in_Speicher_{n}_{z}")

# Entladeleistung der Netzanschlusserweiterung Speicher zum Zeitpunkt z 
leistung_outSpeicher = {}
for n in "Speicher":
    for z in ZEIT: 
        leistung_outSpeicher = model.addVar(vtype="C", lb=0, name=f"Leistung_out_Speicher_{n}_{z}")

# maximale erreichet Netzanschlussleistung (peak) zum Zeitpunkt z 
leistung_peak = {}
for z in ZEIT: 
    leistung_peak = model.addVar(vtype="C", lb=0, name=f"Leistung_peak_{z}")

