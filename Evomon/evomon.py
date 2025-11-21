import random
import pygame
# --- Typen-Konstanten ---
Normal = 0
Feuer = 1
Wasser = 2
Pflanze = 3
Elektro = 4
Unlicht = 5
Psycho = 6
Eis = 7
Fee = 8

Neutral = 9
Nicht_sehr_Effektiv = 10
Sehr_Effektiv = 11

# Fenstereinstellungen
FENSTER_BREITE = 1080
FENSTER_HOEHE = 720


# Positioneneinstellungen
spieler_pos_bild = (150, 200)  # links oben
gegner_pos_bild = (730, 200)   # Rechts unten
HINTERGRUND_POS_BILD = (0,0)
text_ausgabe_spiel_pos = (420, 700)

spieler_pos_text_oben = (spieler_pos_bild[0] + 0, spieler_pos_bild[1] - 24) #
gegner_pos_text_oben = (gegner_pos_bild[0] + 0, gegner_pos_bild[1] - 24)

spieler_pos_kp_balken_x = spieler_pos_bild[0] + 0
spieler_pos_kp_balken_y = spieler_pos_bild[1] + 0

gegner_pos_kp_balken_x = gegner_pos_bild[0] + 0
gegner_pos_kp_balken_y = gegner_pos_bild[1] + 0

spieler_pos_text_kp = (spieler_pos_kp_balken_x, spieler_pos_kp_balken_y + 1)
gegner_pos_text_kp = (gegner_pos_kp_balken_x, gegner_pos_kp_balken_y + 1)

liste_ausgabe_spiel = []
KP_TOD_POKEMON = 0
ep_tod_gegner= 40
kp_balken_länge = 200
kp_balken_breite = 15
liste_level_unterschied_gegner = [-1, 0, 1]
bild_pokemon_skalierung = (200, 200)
# Button
# === Positionseinstellungen ===
button_width = 238
button_height = 50

# obere Buttons (Standardattacken)
oben_y = 569  # Höhe etwas über "Last Subscriber" und "Last Bits"
links_oben_x = 288
rechts_oben_x = 556

# untere Buttons (neue Attacken)
unten_y = 648.7  # Höhe etwas über "Last Follower" und "Last Bits"
links_unten_x = 21
rechts_unten_x = 824

# Farben
LIGHT_GREY = (200, 200, 200)
HOVER = (255, 220, 120)
GREEN = (80, 200, 80)
RED = (230, 80, 80)
LIGHT_BLUE = (106, 171, 237)

#pygame setup
pygame.init()
screen = pygame.display.set_mode((FENSTER_BREITE, FENSTER_HOEHE))  # Fenstereinstellung
clock = pygame.time.Clock()                                         # clokc für fps
running = True                                                      # game loop variable
pygame.display.set_caption("Evomon")                                # Name des Fensters
font_main = pygame.font.Font(None, 36)
font_kp = pygame.font.Font(None, 22)
font_text_ausgabe = pygame.font.Font(None, 19)         # Fenster für Textausgabe spieler

# Hintergrundbild laden
hintergrund_bild = pygame.image.load("graphics/Background/Background.png")
hintergrund_bild = pygame.transform.scale(hintergrund_bild, (FENSTER_BREITE, FENSTER_HOEHE))

# --- Effektivitätsmatrix ---
effektiv = [
    [9, 9, 9, 9, 9, 9, 9, 9, 9],
    [9, 10, 10, 11, 9, 9, 9, 11, 9],
    [9, 11, 10, 10, 10, 9, 9, 11, 9],
    [9, 10, 11, 10, 9, 9, 9, 10, 9],
    [9, 9, 11, 10, 9, 9, 9, 9, 9],
    [9, 9, 9, 9, 9, 9, 11, 9, 9],
    [9, 9, 9, 9, 9, 10, 9, 9, 9],
    [9, 10, 10, 11, 9, 9, 9, 10, 9],
    [9, 9, 9, 9, 9, 11, 9, 9, 9]
]
#Scaling werte
scaling_evolidmg = 1.12
scaling_kp = 0.1
scaling_enmydmg = 0.03


def effekt_faktor(angreifer_typ, verteidiger_typ):
    code = effektiv[angreifer_typ][verteidiger_typ]
    if code == Sehr_Effektiv:
        return 1.45
    elif code == Nicht_sehr_Effektiv:
        return 0.5
    else:
        return 1.0


# --- Klassen ---
class Attacke:
    def __init__(self, name, schaden, typ):
        self.name = name
        self.schaden = schaden
        self.typ = typ


class Pokemon:
    def __init__(self, name, typ, maxkp, ep, lvl, attacken, bilddatei):
        self.name = name
        self.typ = typ
        self.maxkp = maxkp
        self.kp = maxkp
        self.ep = ep
        self.lvl = lvl
        self.attacken = attacken
        self.entwickelt = False

        self.bilddatei = pygame.image.load(bilddatei)#.convert_alpha()
        self.bilddatei = pygame.transform.scale(self.bilddatei, bild_pokemon_skalierung)


    def angreifen(self, ziel, Attacke):
        faktor = effekt_faktor(Attacke.typ, ziel.typ)
        schaden = int(Attacke.schaden * faktor)
        ziel.kp = max(ziel.kp - schaden, 0)
        return schaden, faktor

    def erhalte_ep(self, menge):
        self.ep += menge
        # Dynamische EP-Schwelle
        while self.ep >= 100 + (self.lvl - 5) * 20:
            self.ep -= 100 + (self.lvl - 5) * 20
            self.level_up()

    def level_up(self):
        self.lvl += 1
        self.maxkp += 2
        self.kp = self.maxkp
        print(f"⬆️ {self.name} erreicht Level {self.lvl}!")

        # Attackenschaden leicht erhöhen
        for atk in self.attacken:
            atk.schaden = atk.schaden * scaling_evolidmg

        if self.lvl == 15 and not self.entwickelt:
            self.entwickeln()

    def entwickeln(self):
        entwicklungen = {
            "Flamara": {
                "typ": Feuer,
                "attacken": [Attacke("Flammenwurf", 12, Feuer), Attacke("Glut", 10, Feuer)],
                "bild": "graphics/Pokemon/Flamara.png"
            },
            "Aquana": {
                "typ": Wasser,
                "attacken": [Attacke("Aquaknarre", 12, Wasser), Attacke("Hydropumpe", 10, Wasser)],
                "bild": "graphics/Pokemon/Aquana.png"
            },
            "Blitza": {
                "typ": Elektro,
                "attacken": [Attacke("Donnerschock", 12, Elektro), Attacke("Ladungsstoss", 10, Elektro)],
                "bild": "graphics/Pokemon/Blitza.png"
            },
            "Psiana": {
                "typ": Psycho,
                "attacken": [Attacke("Konfusion", 10, Psycho), Attacke("Psychokinese", 12, Psycho)],
                "bild": "graphics/Pokemon/Psiana.png"
            },
            "Nachtara": {
                "typ": Unlicht,
                "attacken": [Attacke("Finsteraura", 10, Unlicht), Attacke("Biss", 12, Unlicht)],
                "bild": "graphics/Pokemon/Nachtara.png"
            },
            "Glaziola": {
                "typ": Eis,
                "attacken": [Attacke("Blizzard", 10, Eis), Attacke("Eiszahn", 12, Eis)],
                "bild": "graphics/Pokemon/Glaziola.png"
            },
            "Folipurba": {
                "typ": Pflanze,
                "attacken": [Attacke("Laubklinge", 12, Pflanze), Attacke("Rasierblatt", 10, Pflanze)],
                "bild": "graphics/Pokemon/Folipurba.png"
            },
            "Feelinara": {
                "typ": Fee,
                "attacken": [Attacke("Mondgewalt", 12, Fee), Attacke("Säuselstimme", 10, Fee)],
                "bild": "graphics/Pokemon/Feelinara.png"
            }
        }

        # zufällige Entwicklung auswählen
        name, daten = random.choice(list(entwicklungen.items()))

        # Attribute ändern
        self.name = name
        self.typ = daten["typ"]
        self.attacken.extend(daten["attacken"])

        # Neues Bild laden
        self.bilddatei = pygame.image.load(daten["bild"])
        self.bilddatei = pygame.transform.scale(self.bilddatei, bild_pokemon_skalierung)
        #self.bilddatei = pygame.transform.flip(self.bilddatei, True, False)  # Evoli schaut nach links

        self.entwickelt = True
        print(f"✨ Dein Evoli hat sich zu {self.name} entwickelt!")

    def heilen(self):
        self.kp = self.maxkp


class Aquana(Pokemon):
    def __init__(self, name, typ, maxkp, ep, lvl, attacken):
        super().__init__(name, typ, maxkp, ep, lvl, attacken, "graphics/Pokemon/Aquana.png")

class Flamara(Pokemon):
    def __init__(self, name, typ, maxkp, ep, lvl, attacken):
        super().__init__(name, typ, maxkp, ep, lvl, attacken, "graphics/Pokemon/Flamara.png")

class Blitza(Pokemon):
    def __init__(self, name, typ, maxkp, ep, lvl, attacken):
        super().__init__(name, typ, maxkp, ep, lvl, attacken, "graphics/Pokemon/Blitza.png")

class Folipurba(Pokemon):
    def __init__(self, name, typ, maxkp, ep, lvl, attacken):
        super().__init__(name, typ, maxkp, ep, lvl, attacken,"graphics/Pokemon/Folipurba.png")

class Glaziola(Pokemon):
    def __init__(self, name, typ, maxkp, ep, lvl, attacken):
        super().__init__(name, typ, maxkp, ep, lvl, attacken, "graphics/Pokemon/Glaziola.png")

class Nachtara (Pokemon):
    def __init__(self, name, typ, maxkp, ep, lvl, attacken):
        super().__init__(name, typ, maxkp, ep, lvl, attacken, "graphics/Pokemon/Nachtara.png")

class Feelinara (Pokemon):
    def __init__(self, name, typ, maxkp, ep, lvl, attacken):
        super().__init__(name, typ, maxkp, ep, lvl, attacken, "graphics/Pokemon/Feelinara.png")

class Psiana (Pokemon):
    def __init__(self, name, typ, maxkp, ep, lvl, attacken):
        super().__init__(name, typ, maxkp, ep, lvl, attacken, "graphics/Pokemon/Psiana.png")

class Evoli (Pokemon):
    def __init__(self, name, typ, maxkp, ep, lvl, attacken):
        super().__init__(name, typ, maxkp, ep, lvl, attacken, "graphics/Pokemon/Evoli.png")

    # --- Attacken definieren ---
tackle = Attacke("Tackle", 10, Normal)
bodycheck = Attacke("Bodycheck", 12, Normal)
biss = Attacke("Biss", 12, Unlicht)
finsteraura = Attacke("Finsteraura", 10, Unlicht)
aquaknarre = Attacke("Aquaknarre", 12, Wasser)
hydropumpe = Attacke("Hydropumpe", 10, Wasser)
glut = Attacke("Glut", 10, Feuer)
flammenwurf = Attacke("Flammenwurf", 12, Feuer)
ladungsstoss = Attacke("Ladungsstoss", 10, Elektro)
donnerzahn = Attacke("Donnerschock", 12, Elektro)
rasierblatt = Attacke("Rasierblatt", 10, Pflanze)
laubklinge = Attacke("Laubklinge", 12, Pflanze)
säuselstimme = Attacke("Säuselstimme", 10, Fee)
mondgewalt = Attacke("Mondgewalt", 12, Fee)
eiszahn = Attacke("Eiszahn", 12, Eis)
blizzard = Attacke("Blizzard", 10, Eis)
konfusion = Attacke("Konfusion", 12, Psycho)
psychokinese = Attacke("Psychokinese", 10, Psycho)

# --- Gegnerliste (Basiswerte) ---
GEGNER_LISTE = [
    Aquana("Aquana", Wasser, 28, 0, 1, [hydropumpe, aquaknarre, bodycheck, tackle]),
    Flamara("Flamara", Feuer, 26, 0, 1, [flammenwurf, glut, bodycheck, tackle]),
    Blitza("Blitza", Elektro, 26, 0, 1, [donnerzahn, ladungsstoss, bodycheck, tackle]),
    Folipurba("Folipurba", Pflanze, 26, 0, 1, [laubklinge, rasierblatt, bodycheck, tackle]),
    Glaziola("Glaziola", Eis, 26, 0, 1, [blizzard, eiszahn, bodycheck, tackle]),
    Nachtara("Nachtara", Unlicht, 26, 0, 1, [finsteraura, biss, bodycheck, tackle]),
    Feelinara("Feelinara", Fee, 26, 0, 1, [mondgewalt, säuselstimme, bodycheck, tackle]),
    Psiana("Psiana", Psycho, 26, 0, 1, [psychokinese, konfusion, bodycheck, tackle]),
    Evoli("Evoli", Normal, 24, 0, 1, [bodycheck, tackle]),
]

# --- Spieler ---
Evoli = Pokemon("Evoli", Normal, 24, 0, 1, [bodycheck, tackle], "graphics/Pokemon/Evoli.png")


# --- Gegner erzeugen, angepasst an Evoli ---
def gegner_generieren(evoli_lvl):
    basis_gegner = random.choice(GEGNER_LISTE)
    gegner_lvl = max(1, evoli_lvl + random.choice(liste_level_unterschied_gegner))

    gegner_klasse = type(basis_gegner)

    gegner_attacken = [Attacke(atk.name, atk.schaden, atk.typ) for atk in basis_gegner.attacken]

    gegner = gegner_klasse(
        basis_gegner.name,
        basis_gegner.typ,
        basis_gegner.maxkp,
        0,
        gegner_lvl,
        gegner_attacken

    )


    # Schwächere Skalierung
    kp_faktor = 1 + (gegner.lvl - 5) * scaling_kp
    atk_faktor = 1+  (gegner.lvl - 5) * scaling_enmydmg

    gegner.maxkp = int(basis_gegner.maxkp * kp_faktor)
    gegner.kp = gegner.maxkp

    for atk in gegner.attacken:
        atk.schaden = atk.schaden * atk_faktor

    return gegner



# --- Button zeichnen ---
def draw_button(screen, text, x, y, w, h, mouse_pos):
    rect = pygame.Rect(x, y, w, h)
    color = HOVER if rect.collidepoint(mouse_pos) else LIGHT_GREY
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, LIGHT_BLUE, rect, 2, border_radius=8)
    txt = font_main.render(text, True, "BLACK")
    screen.blit(txt, (x + (w - txt.get_width()) // 2, y + (h - txt.get_height()) // 1.7))
    return rect

def add_message_text_ausgabe(inhalt_text_hinzufügen):
    liste_ausgabe_spiel.append(inhalt_text_hinzufügen)
    if len(liste_ausgabe_spiel) > 4:
        liste_ausgabe_spiel.pop(0)


def text_ausgabe():
    liste_ausgabe_spiel_letzte_zeilen = liste_ausgabe_spiel[-3:]

    for i, zeile in enumerate(liste_ausgabe_spiel_letzte_zeilen):
        text_surface = font_text_ausgabe.render(zeile, True, "WHITE")
        screen.blit(text_surface, (text_ausgabe_spiel_pos[0], text_ausgabe_spiel_pos[1] - (3 - i) * 17.25))



# --- Kampfschleife ---
gegner = gegner_generieren(Evoli.lvl)
while running:
    # Bildhintergrund hinzufügen
    screen.blit(hintergrund_bild, HINTERGRUND_POS_BILD)
    # Pokemon-Bilder anzeigen
    screen.blit(Evoli.bilddatei, spieler_pos_bild)
    screen.blit(gegner.bilddatei, gegner_pos_bild)

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(button_rects):
                if rect.collidepoint(mouse_pos):
                    atk = Evoli.attacken[i]
                    schaden, faktor = Evoli.angreifen(gegner, atk)
                    # Textausgabe schaden Spieler
                    inhalt_text_ausgabe_spiel_schaden_spieler = f"{Evoli.name} nutzt {atk.name}! ({schaden} Schaden)"
                    add_message_text_ausgabe(inhalt_text_ausgabe_spiel_schaden_spieler)
                    print(f"{Evoli.name} nutzt {atk.name}! ({schaden} Schaden)")

                    if gegner.kp <= KP_TOD_POKEMON:
                        # Textausgabe bei besigtem gegner
                        inhalt_text_ausgabe_spiel_besiegt_gegner = f"{gegner.name} wurde besiegt!"
                        add_message_text_ausgabe(inhalt_text_ausgabe_spiel_besiegt_gegner)
                        print(f"{gegner.name} wurde besiegt!")

                        Evoli.erhalte_ep(ep_tod_gegner)
                        Evoli.heilen()
                        gegner = gegner_generieren(Evoli.lvl)
                        break
                    else:
                        gegner_atk = random.choice(gegner.attacken)
                        schaden2, _ = gegner.angreifen(Evoli, gegner_atk)
                        # Schaden gegener Ausgabe
                        inhalt_text_ausgabe_spiel_schaden_gegner = f"{gegner.name} nutzt {gegner_atk.name}! ({schaden2} Schaden)"
                        add_message_text_ausgabe(inhalt_text_ausgabe_spiel_schaden_gegner)
                        print(f"{gegner.name} nutzt {gegner_atk.name}! ({schaden2} Schaden)")

                        if Evoli.kp <= KP_TOD_POKEMON:
                            print(f"💀 {Evoli.name} wurde besiegt! Spiel vorbei.")
                            running = False

    # Textanzeige
    spieler_text_oben = font_main.render(f"{Evoli.name} Lvl {Evoli.lvl}", True, "WHITE")
    spieler_text_kp = font_kp.render(f"{Evoli.kp}/{Evoli.maxkp}", True, "BLACK")

    gegner_text_oben = font_main.render(f"{gegner.name} Lvl {gegner.lvl}", True, "WHITE")
    gegner_text_kp = font_kp.render(f"{gegner.kp}/{gegner.maxkp}", True, "BLACK")

    screen.blit(spieler_text_oben, spieler_pos_text_oben)
    screen.blit(gegner_text_oben,gegner_pos_text_oben)


    # KP-Balken
    pygame.draw.rect(screen, RED, (spieler_pos_kp_balken_x, spieler_pos_kp_balken_y, kp_balken_länge, kp_balken_breite))
    pygame.draw.rect(screen, GREEN, (spieler_pos_kp_balken_x, spieler_pos_kp_balken_y, int(kp_balken_länge * (Evoli.kp / Evoli.maxkp)), kp_balken_breite))
    pygame.draw.rect(screen, RED, (gegner_pos_kp_balken_x, gegner_pos_kp_balken_y, kp_balken_länge, kp_balken_breite))
    pygame.draw.rect(screen, GREEN, (gegner_pos_kp_balken_x, gegner_pos_kp_balken_y, int(kp_balken_länge * (gegner.kp / gegner.maxkp)), kp_balken_breite))

    screen.blit(spieler_text_kp, spieler_pos_text_kp)
    screen.blit(gegner_text_kp, gegner_pos_text_kp)

    text_ausgabe()  # anzeige der letzten 3 geschehnisse

    # --- Buttons für Attacken ---
    button_rects = []

    # --- Buttons zeichnen ---
    for i, atk in enumerate(Evoli.attacken[:4]):
        if i == 0:
            x, y = links_oben_x, oben_y
        elif i == 1:
            x, y = rechts_oben_x, oben_y
        elif i == 2:
            x, y = links_unten_x, unten_y
        elif i == 3:
            x, y = rechts_unten_x, unten_y
        else:
            x, y = 400, 700

        rect = draw_button(screen, atk.name, x, y, button_width, button_height, mouse_pos)
        button_rects.append(rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()


