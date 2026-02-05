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
# --Tour-- 
# Menge aller Routen/Touren
ROUTEN = routes_df.index.tolist() 
     

# --LKW--
# Menge aller LKW im Fuhrpark
#FUHRPARK = range(1, len(ROUTEN)+1)  -> theoretisch nur so viele LKW wie Routen benötigt ABER Solver hat zu viele Kombinatione
FUHRPARK = range(1, 20+1)

# Menge der Verfügbare LKW-Typen
FTypen = ["Diesel", "E400", "E600"] 
     

# --Zeit--
# Menge der Zeitschritte in 15-Minuten-Intervallen
ZEIT = range(0, 96)  

# Menge der Nachtzeiten in 15 Minuten-Intervallen (von 0-6 Uhr und 18-24 Uhr)
ZEIT_Nacht = set(range(0, 24)).union(set(range(72, 96))) 

  
# --Ladeinfrastruktur--
# Menge der verfügbaren STypen der Ladensäulen
STypen = ["Alpitronic-50", "Alpitronic-200", "Alpitronic-400"]

# Menge der Ladepunkte (3 Säulen gesamt = 6 Ladepunkte)
LADEPUNKT = range(1, 7)

# direkte Zuordnung der Ladepunkte zu den Säulen
SAULE_ZU_LP = {  
    "S1": [1, 2],
    "S2": [3, 4],
    "S3": [5, 6]
}

# Menge der gekauften Säulen
SAULENBESTAND = ["S1", "S2", "S3"]

# --Netzanschlusserweiterung--
# Menge der möglichen Erweiterungen des Netzanschlusses
NETZANSCHLUSSERWEITERUNG = ["Trafo", "Speicher"]



#----------------------------------------------------------------------------------------
# Parameter
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
             "E400":  105.0/100,
             "E600": 110.0/100
}

# Batteriekapazität von LKW-Typ t
BATTERIE = {"Diesel": 0.0,
            "E400": 414.0,
            "E600": 621.0
            }

# Steuerkosten von LKW-Typ t
C_STEUER = {"Diesel": 556.0,
            "E400": 0.0,
            "E600": 0.0
}

# Erlös THG von LKW-Typ t
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
# Kraftstoffpreis pro Liter Diesel
#P_DIESEL = 1.60
P_DIESEL = {}
for z in ZEIT:
    if z in ZEIT_Nacht:
        P_DIESEL[z] = 1.50
    else:
        P_DIESEL[z] = 1.70

# NEU -> Niedrigerer Preis in der Nacht + Höherer Preis tagsüber
# Stromkosten pro kwH
# P_STROM = 0,25
P_STROM = {}
for z in ZEIT:
    if z in ZEIT_Nacht:
        P_STROM[z] = 0.18
    else:
        P_STROM[z] = 0.30

# Leistungspreis pro kW
P_LEISTUNGSPREIS = 150 


# --Tour/Route--
#Gesamte Fahrstrecke der Tour r
DISTANZ_GESAMT = {r: routes_df.loc[r, 'distance_total'] for r in ROUTEN}  #Wir schauen in jeder Spalte Gesamtdistanz in der Tabelle von den Routen und nehmen das für jede ROute raus

#Mautpflichtige STrecke der Tour r
DISTANZ_MAUT = {r: routes_df.loc[r, 'distance_toll'] for r in ROUTEN}  #siehe oben

# Mautgebühr pro km
C_MAUT = 0.34

#Startzeitpunkt der Tour r
START = {r: routes_df.loc[r, 'starttime'] * 96 for r in ROUTEN}

#Endzeitpunkt der Tour r
# END = {r: routes_df.loc[r, 'endtime'] * 96 for r in ROUTEN}

# --Zeit--
#Einsatztage pro Jahr
N_TAGE = 260


# --Ladeinfrastruktur-- 
# Jährliche Kosten Ladeinfrastruktur (Capex + Opex) pro Säulentyp s
C_CAPEX_S = {
    "Alpitronic-50": 3000.0,
    "Alpitronic-200": 10000.0,
    "Alpitronic-400": 16000.0
}

# Jährliche Betriebskosten Ladeinfrastruktur pro Säulentyp s
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
# maximale Leistung des Netzanschlusses
POWER_LIMIT_NETZ = 500

# jährliche Kosten für Transformator 
C_CAPEX_TRAFO = 10000

# maximale zusätzliche Leistung vom Transformator
POWER_LIMIT_TRAFO = 500

# jährliche Kosten des Speichers für die Leistung pro kW
C_CAPEX_SPEICHER_LEISTUNG = 30

# jährliche Kosten des Speichers für die Kapazität pro kWh
C_CAPEX_SPEICHER_KAPA = 350

# jährliche Wartungskosten des Speichers (2% von den Investitionskosten)
C_CAPEX_SPEICHER_WARTUNGSKOSTEN = 0.02

# Round-Trip-Efficiency des Speichers (98%) (Speicher braucht für sich selbst auch einen ANteil, um sich selbst zu versorgen)
RTE_SPEICHER = 0.98

# maximale Entladetiefe des Speichers (97,5%)
ENTLADETIEFE_SPEICHER = 0.975

#--------------------------------------------------------------------------------
# Neue Erweiterung - Aufgabe 4
#--------------------------------------------------------------------------------

# -- Unsicherheits-Parameter --

 # 10% Zeitpuffer auf jede Route
STAU_ZEIT_FAKTOR = 1.10   

# 10% Mindest-SoC (Sicherheitsreserve)
BATTERIE_RESERVE = 0.10    

# Fiktive Verschleißkosten pro geladener kWh (z.B. 2 Cent)
# Je höher dieser Wert, desto "langsamer/schonender" wird das Modell laden
C_DEGRADATION = 0.02

# --NEU Stau miteinberechnen--
# Neue Endzeit mit Puffer für Staueinbrechungen
END = {}
for r in ROUTEN:
    start_t = routes_df.loc[r, 'starttime'] * 96
    ende_t = routes_df.loc[r, 'endtime'] * 96
    dauer = ende_t - start_t  
    # Ende wird nach hinten verschoben
    END[r] = start_t + (dauer * STAU_ZEIT_FAKTOR)



#--------------------------------------------------------------------------------
# Nicht neue varaiblen (verschoben)
#--------------------------------------------------------------------------------
#Hilfsvariable ->läuft Route r zum zeitpunkt z
from collections import defaultdict
ROUTE_AKTIV = defaultdict(int)
for r in ROUTEN:
    for z in ZEIT:
        ROUTE_AKTIV[r, z] = 1 if START[r] <= z < END[r] else 0    

# Dauer der Route r
ROUTE_DAUER = {
    r: sum(ROUTE_AKTIV[r,z] for z in ZEIT)
    for r in ROUTEN
}



#----------------------------------------------------------------------------------------
# Entscheidungsvariablen
#----------------------------------------------------------------------------------------
# --LKW und Routenverteilung--
# wenn LKW f die Tour r fährt = 1
lkw_fahrt_r = {}

# wenn LKW f den Typ t hat = 1
lkw_hat_typ = {}

# Wenn LKW f vom Typ t fährt Route r = 1 (ersetzt das Produkt von den ersten beiden -> Modell bleibt linear)
lkw_fahrt_Route_mit_typ = {}

for f in FUHRPARK:
    for r in ROUTEN:
        lkw_fahrt_r[f, r] = model.addVar(vtype="B", name=f"LKW_fährt_Route{f}_{r}")  
        for t in FTypen:
            lkw_fahrt_Route_mit_typ[f, r, t] = model.addVar(vtype="B", name=f"LKW_fährt_Route_mit_Type{f}_{r}_{t}")

for f in FUHRPARK:
    for t in FTypen:
        lkw_hat_typ[f, t] = model.addVar(vtype="B", name=f"LKW_hat_Typ_{f}_{t}")
     


# Wenn LKW f zum Zeitpunkt z an Ladepunkt l lädt = 1
lkw_ladt = {}

# Batteriestand LKW f zum Zeitpunkt z
soc_lkw = {}

# Wenn LKW f zum Zeitpunkt z an Ladepunkt l angeschlossen ist = 1
lkw_verbunden_ladepunkt = {}

# Momente Batterieleistung an LKW f zum Zeitpunkt z von Ladepunkt l 
momentane_leistung_an_lkw = {}

for f in FUHRPARK:
    for z in ZEIT:
        soc_lkw[f, z] = model.addVar(vtype="C", lb=0, name=f"soc_LKW_{f}_{z}")
        for l in LADEPUNKT:
            lkw_ladt[f, z, l] = model.addVar(vtype="B", name=f"LKW_lädt_{f}_{z}_{l}")
            lkw_verbunden_ladepunkt[f, z, l] = model.addVar(vtype="B", name=f"LKW_verbunden_{f}_{z}_{l}")
            momentane_leistung_an_lkw[f, z, l] = model.addVar(vtype="C", lb=0, name=f"Max_Leistung_an_LKW_{f}_{z}_{l}")


# --Ladeinfrastruktur-- 
# Wenn Säule b Typ s hat = 1
saule_hat_typ = {}

# wenn die Säule b installiert ist = 1
saule_installiert = {}

for b in SAULENBESTAND:
    saule_installiert[b] = model.addVar(vtype="B", name=f"Säule_installiert_{b}")
    for s in STypen:
        saule_hat_typ[b, s] = model.addVar(vtype="B", name=f"Säule_hat_Typ_{b}_{s}") 


# --Netzanschlusserweiterung--
# Wenn Entscheidung bei Netzwerweiterung n für Trafo = 1
entscheidung_trafo = {}
for n in ["Trafo"]:
    entscheidung_trafo[n] = model.addVar(vtype="B", name=f"Entscheidung_für_Trafo{n}") 

# Wenn Entscheidung bei Netzwerweiterung n für Speicher = 1
entscheidung_speicher = {}

# festzulegende Leistung des Speichers 
leistung_speicher = {}

# festezulegende Batteriekapazität der Netzschlusserweiterung Speicher zum Zeitpunkt z 
kapa_speicher = {}

# Ladezustand der Netzanschlusserweiterung Speicher zum Zeitpunkt z 
soc_speicher = {}

# Ladeleistung der Netzanschlusserweiterung Speicher zum Zeitpunkt z 
leistung_inSpeicher = {}

# Entladeleistung der Netzanschlusserweiterung Speicher zum Zeitpunkt z 
leistung_outSpeicher = {}

for n in ["Speicher"]:
    entscheidung_speicher[n] = model.addVar(vtype="B", name=f"Entscheidung_für_Speicher{n}")
    leistung_speicher[n] = model.addVar(vtype="C", lb=0, name=f"Leistung_des_Speichers_{n}")
    kapa_speicher[n] = model.addVar(vtype="C", lb=0, name=f"Batteriekapazität_des_Speichers_{n}")
    for z in ZEIT:
        soc_speicher[n, z] = model.addVar(vtype="C", lb=0, name=f"Ladezustand_des_Speichers_{n}_{z}")
        leistung_inSpeicher[n, z] = model.addVar(vtype="C", lb=0, name=f"Leistung_in_Speicher_{n}_{z}")
        leistung_outSpeicher[n, z] = model.addVar(vtype="C", lb=0, name=f"Leistung_out_Speicher_{n}_{z}")

# maximale erreichet Netzanschlussleistung (peak) 
leistung_peak = {}
leistung_peak = model.addVar(vtype="C", lb=0, name=f"Leistung_peak")



#----------------------------------------------------------------------------------------
# Zielfunktion
#----------------------------------------------------------------------------------------
model.setObjective(
    # 1. Fuhrpark-Kosten (LKW)
    quicksum(lkw_hat_typ[f, t] * (C_CAPEX_LKW[t] + C_OPEX_LKW[t] + C_STEUER[t] - THG[t])
             for f in FUHRPARK for t in FTypen) +

    # 2. Variable Energiekosten (Diesel & Strom)
    N_TAGE * quicksum(lkw_fahrt_Route_mit_typ[f, r, "Diesel"] * DISTANZ_GESAMT[r] * VERBRAUCH["Diesel"] * P_DIESEL[z] # neu: Abhängig von Zeit z
                  for f in FUHRPARK for r in ROUTEN for z in ZEIT) +
   # N_TAGE * quicksum(momentane_leistung_an_lkw[f, z, l] * 0.25 * P_STROM # 0.25h pro Zeitschritt
                     # for f in FUHRPARK for z in ZEIT for l in LADEPUNKT) +

    # --Neue Erweiterung - Aufgabe 4:--              
    # Verbrauch Elektro-LKW + Degradationskosten
    N_TAGE * quicksum(momentane_leistung_an_lkw[f, z, l] * 0.25 * (P_STROM[z] + C_DEGRADATION) # neu: Abhängig von Zeit z und Degradationskosten
                for f in FUHRPARK for z in ZEIT for l in LADEPUNKT) +
   
    # 3. Mautkosten (nur Diesel)
    N_TAGE * quicksum(lkw_fahrt_Route_mit_typ[f, r, "Diesel"] * DISTANZ_MAUT[r] * C_MAUT
                      for f in FUHRPARK for r in ROUTEN) +
 
    # 4. Netzkosten (Grundgebühr + Leistungspreis)
    C_Gebuhr + (P_LEISTUNGSPREIS * leistung_peak) + # leistung_peak_max muss als Hilfsvariable definiert sein
 
    # 5. Ladeinfrastruktur (Säulen)
    quicksum(saule_hat_typ[b, s] * (C_CAPEX_S[s] + C_OPEX_S[s])
             for b in SAULENBESTAND for s in STypen) +
 
    # 6. Netzanschluss-Erweiterung (Trafo)
    entscheidung_trafo["Trafo"] * C_CAPEX_TRAFO +

    # 7. Netzanschluss-Erweiterung (Speicher)
    (leistung_speicher["Speicher"] * C_CAPEX_SPEICHER_LEISTUNG + kapa_speicher["Speicher"] * C_CAPEX_SPEICHER_KAPA # kapa_speicher_max ist die gewählte Kapazität
    ) * (1 + C_CAPEX_SPEICHER_WARTUNGSKOSTEN),
    
    # Kostenminimierung
    "minimize"
)


#----------------------------------------------------------------------------------------
# Nebenbedingung
#----------------------------------------------------------------------------------------
# --Fahrezeug und Tourenzuordnung--
# (3) Lineare NB:  Wenn LKW f die Route r fährt UND vom Typ t ist, dann lkw_fahrt_Route_mit_typ (Verknüpfung von Fahrt, Typ und der Hilfsvariablen 'lkw_fahrt_Route_mit_typ')
for f in FUHRPARK:
    
    #(1) Jede LKW f hat einen (oder keinen) Typen t
    model.addCons(quicksum(lkw_hat_typ[f, t] for t in FTypen) <= 1, name=f"EinTypProLKW_{f}")
    
    for r in ROUTEN:

        # zu (3) 
        model.addCons(
            lkw_fahrt_r[f, r] <= quicksum(lkw_fahrt_Route_mit_typ[f, r, t] for t in FTypen),
            name=f"Activate_a_{f}_{r}")
        
        for t in FTypen:
            # zu (3)       
            model.addCons(
                lkw_fahrt_Route_mit_typ[f, r, t] <= lkw_fahrt_r[f, r]
                )

            # zu (3)
            model.addCons(
                lkw_fahrt_Route_mit_typ[f, r, t] <= lkw_hat_typ[f, t],
                          name=f"Link_zfdrt_y_{f}_{r}_{t}")


for r in ROUTEN:        
    # (2) Jede Tour r muss genau von einem LKW f gefahren werden
    model.addCons(quicksum(lkw_fahrt_r[f, r] for f in FUHRPARK) == 1, name=f"EinLKWProTour_{r}")



for f in FUHRPARK:
    for z in ZEIT:

        # (4) Für jedes Fahrzeug f dürfen sich aktive Routen zum Zeitpunkt z nicht überschneiden
        model.addCons(
            quicksum(ROUTE_AKTIV[r, z] * lkw_fahrt_r[f, r] for r in ROUTEN) <= 1, 
            name=f"KeineUeberschneidung_{f}_{z}"
        )
            
        # (5) Ein LKW f kann pro Zeitschritt z maximal an EINEM Ladepunkt l laden
        model.addCons(
            quicksum(lkw_ladt[f, z, l] for l in LADEPUNKT) <= 1,
            name=f"MaxEinLadepunkt_{f}_{z}"
        )

        # (6) LKW f darf nur laden, wenn er nicht fährt
        model.addCons(
            quicksum(lkw_ladt[f, z, l] for l in LADEPUNKT) <= 1 - quicksum(lkw_fahrt_r[f, r] * ROUTE_AKTIV[r, z] for r in ROUTEN),
            name=f"Laden_nicht_waehrend_Fahrt_{f}_{z}"
        )

        # (7) Der SOC eines LKW f ergibt sich aus SOC des vorherigen Zeitschrittes, vermindert durch Verbrauch beim Fahren und erhöht durch Ladung
        #     + Energiekreislauf (Start-SoC = End-SoC)
        verbrauch_fz = quicksum(
            ROUTE_AKTIV[r, z] * lkw_fahrt_Route_mit_typ[f, r, t] * (DISTANZ_GESAMT[r] / ROUTE_DAUER[r]) * VERBRAUCH[t] * 0.25 for r in ROUTEN for t in FTypen if t != "Diesel"
        )
        ladung_fz = quicksum(momentane_leistung_an_lkw[f, z, l] * 0.25 for l in LADEPUNKT)
    
        if z > 0:
            model.addCons(
                soc_lkw[f, z] == soc_lkw[f, z-1] - verbrauch_fz + ladung_fz,
                name=f"Energiebilanz_{f}_{z}"
            )
        else:
            # zu (7) (Energiekreislauf)
            model.addCons(
                soc_lkw[f, 0] == soc_lkw[f, 95] - verbrauch_fz + ladung_fz,
                name=f"Energiebilanz_{f}_Start"
            )

        # (8) SoC darf die Batteriekapazität des gewählten LKW-Typs t nicht überschreiten
        model.addCons(
            soc_lkw[f, z] <= quicksum(lkw_hat_typ[f, t] * BATTERIE[t] for t in FTypen),
            name=f"Kapazitaetslimit_{f}_{z}"
        )
        # NEU: Die Sicherheitsreserve nach unten
        # LKW nie ganz leer zu fahren. Das fängt den Mehrverbrauch im Stau (Heizung/Standby) ab.
        model.addCons(
            soc_lkw[f, z] >= BATTERIE_RESERVE * quicksum(lkw_hat_typ[f, t] * BATTERIE[t] for t in FTypen),
            name=f"Sicherheitsreserve_Unten_{f}_{z}"
        )

        for l in LADEPUNKT:

            # (9) Laden nur erlaubt für Elektro-Typen ("E400" und "E600")
            model.addCons(
                lkw_ladt[f, z, l] <= lkw_hat_typ[f, "E400"] + lkw_hat_typ[f, "E600"],
                name=f"ElektroPflicht_Laden_{f}_{z}_{l}"
            )

            # (10) Leistung fließt nur, wenn LKW f zum Zeitpunkt z an Ladepunkt l lädt
            # Big-M Logik (M=400, da dies die max. LKW-Ladeleistung im Code ist)
            model.addCons(
                momentane_leistung_an_lkw[f, z, l] <= 400 * lkw_ladt[f, z, l],
                name=f"Leistung_nur_bei_Aktivierung_{f}_{z}_{l}"
            )

            # (11) Momentane Ladeleistung darf nicht größer sein als das Power Limit des LKW-Typs t
            model.addCons(
                momentane_leistung_an_lkw[f, z, l] <= quicksum(lkw_hat_typ[f, t] * POWER_LIMIT_LKW[t] for t in FTypen),
                name=f"LadeleistungLimit_LKW_{f}_{z}_{l}"
            )


# --Ladeinfrastruktur und Laden der LKWs--
# (12) Jede Säule b hat höchstens einen Säulentyp s
for b in SAULENBESTAND:
    model.addCons(
        quicksum(saule_hat_typ[b, s] for s in STypen) <= 1,
        name=f"EinTypProSaule_{b}"
    )

    # (13) Jede Säule b ist installiert, wenn sie einen Typ s zugewiesen bekommen hat
    model.addCons(saule_installiert[b] == quicksum(saule_hat_typ[b,s] for s in STypen)
        ,name=f"Säule_installiert_definieren_{b}")
    
    # (14) Die Summe der momentanen Leistung an den zugeordneten Ladepunkten l darf die Gesamtkapazität der Säule b nicht überschreiten.
    for z in ZEIT:
        model.addCons(
            quicksum(momentane_leistung_an_lkw[f, z, l] for f in FUHRPARK for l in SAULE_ZU_LP[b]) <= quicksum(saule_hat_typ[b, s] * POWER_LIMIT_S[s] for s in STypen),
            name=f"KapazitaetSaule_{b}_{z}"
        )

    # (15) Maximal dürfen 3 Säulen installiert werden
    model.addCons(
        quicksum(saule_installiert[b] for b in SAULENBESTAND) <= 3,
        name="MaxDreiSaulen"
    )

# (16) Anzahl gleichzeitig ladender LKWs f je Zeitpunkt z ist durch die Anzahl der installierten Ladesäulen b begrenzt, wobei jede Säule 2 Ladepunkte hat
for z in ZEIT:
    model.addCons(
        quicksum(lkw_ladt[f, z, l] for f in FUHRPARK for l in LADEPUNKT)
        <= quicksum(2 * saule_installiert[b] for b in SAULENBESTAND),
        name=f"Ladepunkte_durch_Saulen_begrenzt_{z}"
    )

     # (17) Die momentane Leistung an alle LKW f muss kleiner gleich der verfügbaren Netzleistung + Erweiterung durch Trafo + Speicher sein
    model.addCons(
        # Summe der Ladeleistung an allen LKW
        quicksum(momentane_leistung_an_lkw[f, z, l] for f in FUHRPARK for l in LADEPUNKT) <= 
        # Verfügbare Leistung aus Netz + Speicher-Entladung - Speicher-Ladung
        POWER_LIMIT_NETZ + (POWER_LIMIT_TRAFO * entscheidung_trafo["Trafo"]) 
        + leistung_outSpeicher["Speicher", z] - leistung_inSpeicher["Speicher", z],
        name=f"Leistungsbilanz_Depot_{z}"
    )
 
    # (18) Berechnung des SoC des Speichers unter Verlusten
    if z > 0:
        model.addCons(
            soc_speicher["Speicher", z] == soc_speicher["Speicher", z-1] + (leistung_inSpeicher["Speicher", z] * RTE_SPEICHER - leistung_outSpeicher["Speicher", z]) * 0.25,
            name=f"Speicherdynamik_{z}"
        )
 
    # (19) SoC muss innerhalb der Entladetiefe liegen
    model.addCons(
        soc_speicher["Speicher", z] >= (1 - ENTLADETIEFE_SPEICHER) * kapa_speicher["Speicher"],
        name=f"Speicher_MinSoC_{z}"
    )

    # (20) Der SoC vom Speicher darf nicht größer sein als die Batteriekapazität des Speichers es erlaubt
    model.addCons(
        soc_speicher["Speicher", z] <= kapa_speicher["Speicher"],
        name=f"Speicher_MaxSoC_{z}"
    )

    # (21) Ein- und Ausspeisung des Speichers sind begrenzt durch installierte Speicherleistung
    # 21.1 Einspeisung
    model.addCons(
        leistung_inSpeicher["Speicher", z] <= leistung_speicher["Speicher"],
        name=f"Speicher_Limit_In_{z}"
    )
    # 21.2 Ausspeisung
    model.addCons(
        leistung_outSpeicher["Speicher", z] <= leistung_speicher["Speicher"],
        name=f"Speicher_Limit_Out_{z}"
    )

    # (22) Der Hochpunkt der Leistung (peak) muss größer gleich der Leistung sein, die vom LKW f zum Zeitpunkt z an Ladepunkt l vom netz genommen wird (unter Berücksichtigung Speicher)
    model.addCons(
        leistung_peak >= quicksum(momentane_leistung_an_lkw[f, z, l] for f in FUHRPARK for l in LADEPUNKT) + leistung_inSpeicher["Speicher", z] - leistung_outSpeicher["Speicher", z],
        name=f"Peak_Definition_{z}"
    )

    for l in LADEPUNKT:

        # (23) An einem Ladepunkt l darf max. ein LKW gleichzeitig laden zum Zeitpunkt z
        model.addCons(
            quicksum(lkw_ladt[f, z, l] for f in FUHRPARK) <= 1,
            name=f"MaxEinLKWProLadepunkt_{z}_{l}"
        )

# (24) Säule b wird nur gekauft, wenn wir einen E-LKW t im Fuhrpark f haben
model.addCons(
    quicksum(saule_installiert[b] for b in SAULENBESTAND)
    <= quicksum(lkw_hat_typ[f, "E400"] + lkw_hat_typ[f, "E600"] for f in FUHRPARK) / 2,
    name="Max_Saulen_durch_E_LKW"
)
 
# (25) Leistung hat nur einen Wert, wenn Speicher installiert ist
# Big-M Logik (M=500 als ausreichend großer Platzhalter (max. Netzlimit 500kW))
model.addCons(
    leistung_speicher["Speicher"] <= 500 * entscheidung_speicher["Speicher"],
    name="Speicher_Leistung_Kopplung"
)

# (26) Kapazität hat nur einen Wert, wenn Speicher installiert ist 
# Big-M Logik (M=10000 als ausreichend großer Platzhalter)
model.addCons(
    kapa_speicher["Speicher"] <= 10000 * entscheidung_speicher["Speicher"],
    name=f"Speicher_Kapa_Kopplung_"
)
 
# (27) Energiefluss Kreislauf Speicher: Start-SoC = End-SoC
model.addCons(
    soc_speicher["Speicher", 0] == soc_speicher["Speicher", 95],
    name="Speicher_Kreislauf"
)
 
 

# ------------------------------------------------------------------------
# --Erweiterung--
# ------------------------------------------------------------------------

for f in FUHRPARK:
    for z in ZEIT:

        # (28)LKW f darf nicht mit Ladepunkt l verbunden sein, wenn er fährt
        model.addCons(
                quicksum(lkw_verbunden_ladepunkt[f, z, l] for l in LADEPUNKT)  <= 1 - quicksum(lkw_fahrt_r[f, r] * ROUTE_AKTIV[r, z] for r in ROUTEN),
                name=f"Nicht_verbunden_waehrend_Fahrt_{f}_{z}"
            )
        
        # (29) LKW f kann maximal eine Verbindung an Ladepunkt l zum Zeitpunkt z haben (Säulensicht)
        model.addCons(
            quicksum(lkw_verbunden_ladepunkt[f, z, l] for l in LADEPUNKT) <= 1,
            name=f"MaxEinLadepunkt_verbunden_{f}_{z}"
        )
    
        for l in LADEPUNKT:
            # (30) Laden des LKWs f nur wenn er an Ladepunkt l zum Zeitpunkt z verbunden ist
            model.addCons(
                lkw_ladt[f, z, l] <= lkw_verbunden_ladepunkt[f, z, l],
                name=f"Laden_nur_wenn_verbunden_{f}_{z}_{l}"
            )

            # (31) LKW f kann nur an Ladepunkt l verbunden sein, wenn die zugehörige Säule b installiert ist
            model.addCons(
                lkw_verbunden_ladepunkt[f, z, l] <= quicksum(saule_installiert[b] for b in SAULE_ZU_LP),
                name=f"Verbunden_nur_wenn_Säule_installiert_{f}_{z}_{l}"
            )

            # (32) Anschließen an Ladepunkt l nur für Elektro-Typen ("E400" und "E600")
            model.addCons(
                lkw_verbunden_ladepunkt[f, z, l] <= lkw_hat_typ[f, "E400"] + lkw_hat_typ[f, "E600"],
                name=f"ElektroPflicht_verbunden_{f}_{z}_{l}"
            )

for l in LADEPUNKT:
    for z in ZEIT:

        # (33) Maximal eine Verbindung an LKW f pro Ladepunkt l zum Zeitpunkt z (LKW-Sicht)
        model.addCons(
            quicksum(lkw_verbunden_ladepunkt[f, z, l] for f in FUHRPARK) <= 1,
            name=f"MaxEinLKWProLadepunkt_verbunden_{z}_{l}"
        )



#----------------------------------------------------------------------------------------
# Erweiterung 1: zwischen 6 - 18 Uhr darf LKW f Zwischenparken (vor und nach dem Laden ->bevor er an Ladepunkt l angeschlossen wird)
# -> automatisch erfüllt, weil tagsüber keine Pflicht zum Verbinden

for f in FUHRPARK:
    for z in ZEIT:

        # Erweiterung 3: (34) Wenn LKW f zwischen 18 - 6 Uhr ins Depot zurückkehrt, sofort an Ladepunkt l anschließen 
        faehrt_fz = quicksum(lkw_fahrt_r[f, r] * ROUTE_AKTIV[r, z] for r in ROUTEN)
        ist_elektro_f = lkw_hat_typ[f, "E400"] + lkw_hat_typ[f, "E600"]
        model.addCons(
            quicksum(lkw_verbunden_ladepunkt[f, z, l] for l in LADEPUNKT) >= ist_elektro_f - faehrt_fz,
            name=f"Nacht_Sofort_Anschluss_{f}_{z}"
        )

        #------------------------------------------------------------------------------------------------

        # Erweiterung 2: (35) Während des Ladens darf LKW f nicht Ladepunkt l wechseln
        if z == 0:
            continue
        fahrt_fz = quicksum(lkw_fahrt_r[f, r] * ROUTE_AKTIV[r, z] for r in ROUTEN)
        for l in LADEPUNKT:
            model.addCons(
                lkw_verbunden_ladepunkt[f, z, l] >= lkw_verbunden_ladepunkt[f, z-1, l] - fahrt_fz,
                name=f"Kontinuitaet_Anschluss_{f}_{z}_{l}"
            )



# ------------------------------------------------------------------------
# --Für eine bessere Laufleistung des Codes--
# ------------------------------------------------------------------------

# Zwinge den Solver, die LKWs in einer festen Reihenfolge zu benutzen. LKW 2 darf nur benutzt werden, wenn LKW 1 auch einen Typ zugewiesen bekommen hat: 
#for f in FUHRPARK:
 #   if f > 1:
  #      model.addCons(
   #         quicksum(lkw_hat_typ[f, t] for t in FTypen) <= quicksum(lkw_hat_typ[f-1, t] for t in FTypen),
    #        name=f"Symmetriebrechung_LKW_{f}"
     #   )



#----------------------------------------------------------------------------------------
#Testing 
#----------------------------------------------------------------------------------------

# Zum Test: Modell soll einen E400 und einen E600 LKW im Fuhrpark haben (Modell erzeugt das selbst)
# -- Erzwinge spezifische Fahrzeugtypen --
# Mindestens ein E400 im Fuhrpark
#model.addCons(
  #  quicksum(lkw_hat_typ[f, "E400"] for f in FUHRPARK) >= 1,
 #   name="Mindestens_ein_E400"
#)
# Mindestens ein E600 im Fuhrpark
#model.addCons(
  #  quicksum(lkw_hat_typ[f, "E600"] for f in FUHRPARK) >= 1,
 #   name="Mindestens_ein_E600"
#)

#----------------------------------------------------------------------------------------
# Modell optimiieren
#----------------------------------------------------------------------------------------

model.setRealParam("limits/time", 1800) # Gib ihm 5 Minuten Zeit
model.optimize()


#----------------------------------------------------------------------------------------
# Ausgabe
#----------------------------------------------------------------------------------------
 
def format_time_from_step(t_step: int) -> str:
    """Wandelt Zeitschritte (0-95) in Uhrzeit (HH:MM) um."""
    total_minutes = t_step * 15
    hh = total_minutes // 60
    mm = total_minutes % 60
    return f"{hh:02d}:{mm:02d}"
 
if model.getNSols() > 0:
    # --- TEIL A: SOFORTIGE AUSGABE IM TERMINAL ---
    print("\n" + "="*80)
    print(f"LÖSUNG GEFUNDEN: {model.getObjVal():,.2f} € Gesamtkosten")
    print("="*80)
    print(f"[SOLVER STATUS]")
    print(f"  Status:      {model.getStatus()}")
    print(f"  Gap:         {model.getGap()*100:.2f} %")
    print(f"  Rechenzeit:  {model.getSolvingTime():.2f} s")
    print("-" * 80)
   
    # Vorbereitung: Liste der aktiven LKW (N/A filtern) mit neuer Nummerierung ab 01
    aktive_lkw_liste = []
    display_id = 1
    for f in FUHRPARK:
        lkw_typ = next((t for t in FTypen if model.getVal(lkw_hat_typ[f, t]) > 0.5), None)
        if lkw_typ:
            aktive_lkw_liste.append({
                'orig_f': f,
                'typ': lkw_typ,
                'display_name': f"LKW {display_id:02d}"
            })
            display_id += 1
 
    print(f"Erstelle detailliertes Protokoll in 'Simulationsergebnis_A4.txt'...")
 
    # --- TEIL B: SCHREIBEN ALLER DETAILS IN DIE DATEI ---
    log_filename = "Simulationsergebnis_A4.txt"
    with open(log_filename, "w", encoding="utf-8") as f_out:
        # 1) HEADER
        f_out.write("="*95 + "\n")
        f_out.write(f"SIMULATIONSERGEBNIS - STRATEGISCHES PROTOKOLL (ERWEITERT)\n")
        f_out.write(f"Gesamtkosten p.a.: {model.getObjVal():,.2f} €\n")
        f_out.write("="*95 + "\n")
        f_out.write(f"Solver Status: {model.getStatus()} | Gap: {model.getGap()*100:.2f}%\n\n")

        # --- NEU: ANALYSE DER ERWEITERUNGEN ---
        f_out.write("[SONDERANALYSE: PRAXIS-ERWEITERUNGEN]\n")
        
        # Dynamische Preise
        f_out.write(f"  ➤ 1. DYNAMISCHE PREISE:\n")
        f_out.write(f"     Status: Aktiv (Nacht: {P_STROM[0]:.2f}€/kWh | Tag: {P_STROM[40]:.2f}€/kWh)\n")
        
        # Stau-Puffer & Dauer
        f_out.write(f"  ➤ 2. STAU-PUFFER & ROUTENDAUER:\n")
        f_out.write(f"     Sicherheitsfaktor: {STAU_ZEIT_FAKTOR*100-100:.0f}% zusätzliche Zeit pro Route.\n")
        beispiel_r = ROUTEN[0]
        original_dauer = (routes_df.loc[beispiel_r, 'endtime'] - routes_df.loc[beispiel_r, 'starttime']) * 96
        f_out.write(f"     Beispiel Route {routes_df.loc[beispiel_r, 'route_id']}: {original_dauer:.1f} -> {ROUTE_DAUER[beispiel_r]:.1f} Zeitschritte\n")

        # Batterie-Reserve
        f_out.write(f"  ➤ 2.1 ENERGIE-RESERVE:\n")
        f_out.write(f"     Mindest-SoC: {BATTERIE_RESERVE*100:.0f}% der Kapazität verbleiben als Puffer.\n")

        # Degradation
        degrad_kosten_gesamt = N_TAGE * sum(model.getVal(momentane_leistung_an_lkw[f, z, l]) * 0.25 * C_DEGRADATION 
                                           for f in FUHRPARK for z in ZEIT for l in LADEPUNKT)
        f_out.write(f"  ➤ 3. BATTERIE-DEGRADATION:\n")
        f_out.write(f"     Fiktive Verschleißkosten: {C_DEGRADATION:.3f} €/kWh\n")
        f_out.write(f"     Gesamte kalkulatorische Abnutzung: {degrad_kosten_gesamt:,.2f} € p.a.\n")

        # 2) GEKAUFTE FLOTTE
        f_out.write("[GEKAUFTE FLOTTE]\n")
        for t in FTypen:
            anzahl = sum(1 for lkw in aktive_lkw_liste if lkw['typ'] == t)
            if anzahl > 0:
                f_out.write(f"  ➤ {t:<15} : {int(anzahl)} Fahrzeug(e)\n")
        f_out.write(f"  --- Gesamt: {len(aktive_lkw_liste)} aktive Fahrzeuge\n\n")

        # 3) DETAILLIERTE KOSTENANALYSE
        lkw_fix = sum(model.getVal(lkw_hat_typ[f, t]) * (C_CAPEX_LKW[t] + C_OPEX_LKW[t] + C_STEUER[t] - THG[t]) for f in FUHRPARK for t in FTypen)
        diesel_var = N_TAGE * sum(model.getVal(lkw_fahrt_Route_mit_typ[f, r, "Diesel"]) * (DISTANZ_GESAMT[r] * VERBRAUCH["Diesel"] * P_DIESEL[z]) for f in FUHRPARK for r in ROUTEN)
        maut_kosten = N_TAGE * sum(model.getVal(lkw_fahrt_Route_mit_typ[f, r, "Diesel"]) * (DISTANZ_MAUT[r] * C_MAUT) for f in FUHRPARK for r in ROUTEN)
        strom_rein = N_TAGE * sum(model.getVal(momentane_leistung_an_lkw[f, z, l]) * 0.25 * P_STROM[z] for f in FUHRPARK for z in ZEIT for l in LADEPUNKT)
        peak_leistung = model.getVal(leistung_peak)
        netz_fix = C_Gebuhr + (P_LEISTUNGSPREIS * peak_leistung)
        lade_infra = sum(model.getVal(saule_hat_typ[b, s]) * (C_CAPEX_S[s] + C_OPEX_S[s]) for b in SAULENBESTAND for s in STypen)
        trafo_k = model.getVal(entscheidung_trafo["Trafo"]) * C_CAPEX_TRAFO if "Trafo" in entscheidung_trafo else 0
        speicher_k = (model.getVal(leistung_speicher["Speicher"]) * C_CAPEX_SPEICHER_LEISTUNG + model.getVal(kapa_speicher["Speicher"]) * C_CAPEX_SPEICHER_KAPA) * (1 + C_CAPEX_SPEICHER_WARTUNGSKOSTEN) if "Speicher" in entscheidung_speicher else 0

        f_out.write("[1 - FINANZIELLE DETAILS]\n")
        f_out.write(f"  ➤ LKW Fixkosten (netto):         {lkw_fix:12,.2f} €\n")
        f_out.write(f"  ➤ Diesel Variable Kosten:        {diesel_var:12,.2f} €\n")
        f_out.write(f"  ➤ Mautkosten (nur Diesel):       {maut_kosten:12,.2f} €\n")
        f_out.write(f"  ➤ Stromkosten (exkl. Verschleiß): {strom_rein:12,.2f} €\n")
        f_out.write(f"  ➤ Batterie-Abnutzung (Degrad.):  {degrad_kosten_gesamt:12,.2f} €\n")
        f_out.write(f"  ➤ Netz (Peak: {peak_leistung:6.1f} kW):   {netz_fix:12,.2f} €\n")
        f_out.write(f"  ➤ Ladeinfrastruktur (Säulen):    {lade_infra:12,.2f} €\n")
        f_out.write(f"  ➤ Netzerweiterung (Trafo/Spei.): {trafo_k + speicher_k:12,.2f} €\n\n")

        # 4) HEADER
        f_out.write("="*95 + "\n")
        f_out.write(f"SIMULATIONSERGEBNIS - STRATEGISCHES PROTOKOLL\n")
        f_out.write(f"Gesamtkosten p.a.: {model.getObjVal():,.2f} €\n")
        f_out.write("="*95 + "\n")
        f_out.write(f"Solver Status: {model.getStatus()} | Gap: {model.getGap()*100:.2f}%\n\n")
 
        # 5) GEKAUFTE FLOTTE (Zusammenfassung)
        f_out.write("[GEKAUFTE FLOTTE]\n")
        for t in FTypen:
            anzahl = sum(1 for lkw in aktive_lkw_liste if lkw['typ'] == t)
            if anzahl > 0:
                f_out.write(f"  ➤ {t:<15} : {int(anzahl)} Fahrzeug(e)\n")
        f_out.write(f"  --- Gesamt: {len(aktive_lkw_liste)} aktive Fahrzeuge\n\n")
 
        # 6) DETAILLIERTE KOSTENANALYSE
        lkw_fix = sum(model.getVal(lkw_hat_typ[f, t]) * (C_CAPEX_LKW[t] + C_OPEX_LKW[t] + C_STEUER[t] - THG[t]) for f in FUHRPARK for t in FTypen)
        diesel_var = N_TAGE * sum(model.getVal(lkw_fahrt_Route_mit_typ[f, r, "Diesel"]) * (DISTANZ_GESAMT[r] * VERBRAUCH["Diesel"] * P_DIESEL[z]) for f in FUHRPARK for r in ROUTEN)
        maut_kosten = N_TAGE * sum(model.getVal(lkw_fahrt_Route_mit_typ[f, r, "Diesel"]) * (DISTANZ_MAUT[r] * C_MAUT) for f in FUHRPARK for r in ROUTEN)
        strom_var = N_TAGE * sum(model.getVal(momentane_leistung_an_lkw[f, z, l]) * 0.25 * P_STROM[z] for f in FUHRPARK for z in ZEIT for l in LADEPUNKT)
        peak_leistung = model.getVal(leistung_peak)
        netz_fix = C_Gebuhr + (P_LEISTUNGSPREIS * peak_leistung)
        lade_infra = sum(model.getVal(saule_hat_typ[b, s]) * (C_CAPEX_S[s] + C_OPEX_S[s]) for b in SAULENBESTAND for s in STypen)
        trafo_k = model.getVal(entscheidung_trafo["Trafo"]) * C_CAPEX_TRAFO if "Trafo" in entscheidung_trafo else 0
        speicher_k = (model.getVal(leistung_speicher["Speicher"]) * C_CAPEX_SPEICHER_LEISTUNG + model.getVal(kapa_speicher["Speicher"]) * C_CAPEX_SPEICHER_KAPA) * (1 + C_CAPEX_SPEICHER_WARTUNGSKOSTEN) if "Speicher" in entscheidung_speicher else 0
 
        f_out.write("[1 - KOSTENANALYSE]\n")
        f_out.write(f"  ➤ LKW Fixkosten (netto):         {lkw_fix:12,.2f} €\n")
        f_out.write(f"  ➤ Diesel Variable Kosten:        {diesel_var:12,.2f} €\n")
        f_out.write(f"  ➤ Mautkosten (nur Diesel):       {maut_kosten:12,.2f} €\n")
        f_out.write(f"  ➤ Strom Variable Kosten:         {strom_var:12,.2f} €\n")
        f_out.write(f"  ➤ Netz (Peak: {peak_leistung:6.1f} kW):   {netz_fix:12,.2f} €\n")
        f_out.write(f"  ➤ Ladeinfrastruktur (Säulen):    {lade_infra:12,.2f} €\n")
        f_out.write(f"  ➤ Netzerweiterung (Trafo/Spei.): {trafo_k + speicher_k:12,.2f} €\n\n")
 
        # 7) INFRASTRUKTUR & INVESTITIONSBEGRÜNDUNG
        f_out.write("[2 - INFRASTRUKTUR & INVESTITIONS-LOGIK]\n")
        for b in SAULENBESTAND:
            for s in STypen:
                if model.getVal(saule_hat_typ[b, s]) > 0.5:
                    f_out.write(f"  ➤ Säule {b}: Typ {s} installiert\n")
 
        trafo_entscheidung = model.getVal(entscheidung_trafo["Trafo"]) if "Trafo" in entscheidung_trafo else 0
        if trafo_entscheidung < 0.5:
            f_out.write(f"\n  ➤ Trafo-Erweiterung: NICHT GEKAUFT\n")
            f_out.write(f"     Grund: Die vorhandene Netzkapazität reicht aus. Ein Ausbau wäre teurer als der operative Nutzen.\n")
        else:
            f_out.write(f"\n  ➤ Trafo-Erweiterung: GEKAUFT ({trafo_k:,.2f} €)\n")
 
        speicher_entscheidung = model.getVal(entscheidung_speicher["Speicher"]) if "Speicher" in entscheidung_speicher else 0
        if speicher_entscheidung < 0.5:
            f_out.write(f"  ➤ Batteriespeicher: NICHT GEKAUFT\n")
            f_out.write(f"     Grund: Peak-Shaving durch Hardware ist aktuell teurer als die Netzentgelte für die Spitzenlast.\n")
        else:
            f_out.write(f"  ➤ Batteriespeicher: GEKAUFT (Leistung: {model.getVal(leistung_speicher['Speicher']):.1f} kW)\n")
 
        # 8) TOURENPLAN
        f_out.write("\n[3 - TOURENPLAN]\n")
        for lkw in aktive_lkw_liste:
            touren = [routes_df.loc[r, 'route_id'] for r in ROUTEN if model.getVal(lkw_fahrt_r[lkw['orig_f'], r]) > 0.5]
            if touren:
                f_out.write(f"    {lkw['display_name']} [{lkw['typ']:10}]: Touren -> {', '.join(touren)}\n")
       
        # 9) PERFORMANCE-ANALYSE
        f_out.write(f"\n[4 - PERFORMANCE-ANALYSE]\n")
        f_out.write(f"  ➤ Laufleistung (Km pro Tag):\n")
        for t in FTypen:
            km_typ = sum(model.getVal(lkw_fahrt_r[lkw['orig_f'], r]) * DISTANZ_GESAMT[r]
                         for lkw in aktive_lkw_liste if lkw['typ'] == t for r in ROUTEN)
            anz_lkw = sum(1 for lkw in aktive_lkw_liste if lkw['typ'] == t)
            if anz_lkw > 0:
                f_out.write(f"     - {t:<12}: Gesamt {km_typ:8.1f} km (Schnitt: {km_typ/anz_lkw:6.1f} km/LKW)\n")
 
        # 10) VOLLSTÄNDIGER AKTIVITÄTS-LOG
        f_out.write(f"\n[5 - AKTIVITÄTS-LOG]\n")
        header_log = f"{'Uhrzeit':<8} | {'LKW':<7} | {'Typ':<12} | {'Status':<12} | {'Säule':<7} | {'LP':<4} | {'SoC (kWh)':<10} | {'Info'}"
        f_out.write("-" * len(header_log) + "\n")
        f_out.write(header_log + "\n")
        f_out.write("-" * len(header_log) + "\n")
 
        for lkw in aktive_lkw_liste:
            f_orig = lkw['orig_f']
            for z in ZEIT:
                # Suche nach dem aktiven Ladepunkt
                aktiver_lp = None
                for l in LADEPUNKT:
                    if model.getVal(lkw_ladt[f_orig, z, l]) > 0.5:
                        aktiver_lp = l
                        break
               
                # Säule über Dictionary auflösen (Suche in Werten der Säulen)
                aktive_saule = "---"
                if aktiver_lp is not None:
                    for s_id, lp_list in SAULE_ZU_LP.items():
                        if aktiver_lp in lp_list:
                            aktive_saule = s_id
                            break
 
                # Status-Ermittlung
                aktive_tour = next((routes_df.loc[r, 'route_id'] for r in ROUTEN
                                   if model.getVal(lkw_fahrt_r[f_orig, r]) > 0.5 and ROUTE_AKTIV[r, z] > 0.5), None)
 
                if aktive_tour:
                    status, info = "FÄHRT", f"Tour {aktive_tour}"
                elif aktiver_lp is not None:
                    p_ist = sum(model.getVal(momentane_leistung_an_lkw[f_orig, z, lp]) for lp in LADEPUNKT if lp == aktiver_lp)
                    if p_ist > 0.1:
                        status, info = "LÄDT", f"mit {p_ist:.1f} kW"
                    else:
                        status, info = "VERBUNDEN", "Wartet auf Strom"
                else:
                    status, info = "DEPOT", "Standby"
 
                soc_val = model.getVal(soc_lkw[f_orig, z])
                soc_display = f"{soc_val:9.1f}" if lkw['typ'] != "Diesel" else "   ---    "
               
                f_out.write(f"{format_time_from_step(z):<8} | {lkw['display_name']} | {lkw['typ']:<12} | {status:<12} | {str(aktive_saule):<7} | {str(aktiver_lp) if aktiver_lp is not None else '---':<4} | {soc_display} | {info}\n")
            f_out.write("-" * len(header_log) + "\n")
 
    print(f"\n>>> Protokoll unter '{log_filename}' gespeichert.")
else:
    print("\nKeine Lösung gefunden.")