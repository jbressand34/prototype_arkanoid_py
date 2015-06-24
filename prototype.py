#!/usr/bin/python3
#-*- coding: utf-8 -*-

from tkinter import *
from math import sqrt, cos, sin, pi

"""@package prototype
Prototype du jeu arkanoid.
Les fonctionnalitées implémentées sont :
- Afficher et bouger la raquette.
- Afficher et mouvoir la balle.
- Affiher et faire disparaître des briques.
- Faire rebondir la balle contre les parois, la raquette
  et les briques
"""

# fonction de manipulation des sprites

def subimage(x1, y1, x2, y2):
    dst = PhotoImage()
    dst.tk.call(dst, 'copy', sprites, '-from', x1, y1, x2, y2, '-to', 0, 0)
    return dst

def updateyoshi():
    global numimages, flagyoshis

    for i in range(8):
        if dangeryoshi(i):
            numimages[i] = 4 
        elif flagyoshis[i]:
            numimages[i] = (numimages[i]+1)%4
            flagyoshis[i]=0
            fen.after(500, leverdrapeauyoshi, i)
        if numimages[i] == 4:
            yyoshis[i]+=1
        elif sqrt((xballe-xyoshis[i])**2+(yballe-yyoshis[i])**2) < 40:
            numimages[i] = 5

def leverdrapeauyoshi(i):
    global flagyoshis
    flagyoshis[i]=1

def dangeryoshi(i):
    global briques, yyoshis, xyoshis, vies, \
           xballe, yballe
    danger = 1
    for brique in briques:
        #si la brique est juste en dessous de yoshi
        if vies[brique[4]] and \
           brique[1]+brique[2]/2>=(yyoshis[i]+16) and \
           brique[1]-brique[2]/2<=(yyoshis[i]+16) and \
           brique[0]-brique[3]/2<=(xyoshis[i]+14) and \
           brique[0]+brique[3]/2>=(xyoshis[i]-14):
            yyoshis[i] = brique[1]-brique[2]/2-16
            danger = 0

    return danger


# gestionnaires d'événements

def mouvementraquette(dx):
    """Gère le déplacement de la raquette.
    Appelle la fonction miseenmouvement qui
    met en mouvement la balle lors du premier 
    déplacement de la raquette.
    """
    global xraquette
    xraquette += dx
    miseenmouvement(dx)

def mouvementraquettegauche(event):
    """ Gestionnaire de l'évènement :
    L'utilisateur à appuyé sur la flèche gauche
    du clavier.
    """
    global xraquette, LONGUEUR_RAQUETTE
    if (xraquette - 10) > LONGUEUR_RAQUETTE/2:
        mouvementraquette(-10)

def mouvementraquettedroit(event):
    """ Gestionnaire de l'évènement :
    L'utilisateur à appuyé sur la flèche droite
    du clavier.
    """
    global xraquette, LONGUEUR_RAQUETTE, LARGEUR_ECRAN
    if (xraquette + 10 + LONGUEUR_RAQUETTE/2) < LARGEUR_ECRAN :
        mouvementraquette(+10)

def miseenmouvement(dx):
    """ Fonction permettant la mise en mouvement
    de la balle. Cette fonction n'appelle la fonction
    mouvementballe qu'une seule fois au debut quand 
    le drapeau flag est à 0.
    """
    global flag, theta
    if not flag:
        flag = 1
        theta = pi/2-dx*pi/(10*6)
        mouvementballe()

def fin():
    """ Fonction appelée lorsque la balle
    passe en dessous de la raquette.
    Cette fonction met fin au programme.
    """
    fen.quit()

def collisionparoi():
    """ Fonction testant la collision
    entre la balle et les parois de
    l'écran et modifiant la position et 
    la trajectoire de la balle en fonction.
    """
    global xballe, yballe, rvballe, theta, rballe, LARGEUR_ECRAN, \
        HAUTEUR_ECRAN
    if xballe < (rballe + 5):
        xballe, theta = rballe + 5, pi-theta
    if yballe < (rballe + 5):
        yballe, theta = rballe + 5, -theta
    if xballe > (LARGEUR_ECRAN - rballe - 5):
        xballe, theta = (LARGEUR_ECRAN-rballe-5), pi-theta
    if yballe > (HAUTEUR_ECRAN - rballe - 5):
        yballe, theta = (HAUTEUR_ECRAN-rballe-5), -theta    


def collisionraquette():

    """ Fonction testant la collision de
    la balle avec la raquette et adapte
    la trajectoire et la position de la balle 
    en fonction.
    """

    global xballe, yballe, rvballe, theta, rballe, \
        xraquette, LONGUEUR_RAQUETTE, LARGEUR_RAQUETTE, \
        LARGEUR_ECRAN, HAUTEUR_ECRAN
    t = (xraquette + LONGUEUR_RAQUETTE/2 - xballe)/LONGUEUR_RAQUETTE 
    # indice du point de collision : 0<t<1,  
    # t=0 : la balle est située tout à droite de la raquette
    # t=1 : la balle est située tout à gauche

    #Si la balle se situe à la même hauteur que la raquette
    if (yballe-rballe)<(HAUTEUR_ECRAN-20) and \
       (yballe+rballe)>(HAUTEUR_ECRAN-20-LARGEUR_RAQUETTE) :

        #Si la balle tape sur le dessus de la raquette
        if xballe > (xraquette - LONGUEUR_RAQUETTE/2) and \
           xballe < (xraquette + LONGUEUR_RAQUETTE/2): 
            yballe = HAUTEUR_ECRAN-20-LARGEUR_RAQUETTE-rballe
            theta = pi/6+t*2*pi/3
                
                
        #Sinon si elle heurte le côté gauche de la raquette
        elif xballe <= (xraquette - LONGUEUR_RAQUETTE/2) and \
             (xballe+rballe) >= (xraquette-LONGUEUR_RAQUETTE/2):
            xballe = xraquette - LONGUEUR_RAQUETTE/2 - rballe 
            theta = 3*pi/4

        #Sinon si elle heurte le côté droit de la raquette
        elif xballe >= (xraquette + LONGUEUR_RAQUETTE/2) and \
             (xballe-rballe) <= (xraquette + LONGUEUR_RAQUETTE/2):
            xballe = xraquette + LONGUEUR_RAQUETTE/2 + rballe
            theta = pi/4



def collisionbriques():

    """ Fonction testant la collision
    de la balle avec les briques. 
    Si il y a collision, le numero
    de la brique est conservé dans la liste drapeaux.
    """

    global xballe, yballe, rballe, \
           briques, vies, drapeaux

    for brique in briques:
        if vies[brique[4]] :
            #Si la balle est en contact avec la brique
            if (yballe + rballe)>(brique[1]-brique[2]/2) and \
               (yballe - rballe)<(brique[1]+brique[2]/2) and \
               (xballe + rballe)>(brique[0]-brique[3]/2) and \
               (xballe - rballe)<(brique[0]+brique[3]/2):
                drapeaux.append(brique[4])
                vies[brique[4]] -= 1
    calcultrajectoire()
    drapeaux = []



def calcultrajectoire():
    
    """ Fonction calculant la trajectoire
    de la balle à partir de la liste des
    briques qui entrent en contact avec
    la balle.
    """
    global xballe, yballe, rballe, theta, drapeaux, briques

    if len(drapeaux) == 1:
        i = drapeaux[0]
        #si la balle tape en dessous ou au dessus de la brique
        if xballe>(briques[i][0]-briques[i][3]/2) and \
           xballe<(briques[i][0]+briques[i][3]/2):
            #si la balle tape au dessus
            if sin(theta) <= 0:
                yballe = briques[i][1]-briques[i][2]/2-rballe
            #si la balle tape en dessous
            else:
                yballe = briques[i][1]+briques[i][2]/2+rballe
            theta = -theta
        #sinon si elle tape sur le côté gauche
        elif xballe<(briques[i][0]-briques[i][3]/2):
            #si la balle va vers la gauche
            if cos(theta) <= 0:
                #si la  balle va vers le haut
                if sin(theta)>=0:
                    yballe = briques[i][1]+briques[i][2]/2+rballe
                #sinon
                else:
                    yballe = briques[i][1]-briques[i][2]/2-rballe
                theta = -theta
            #si la balle va vers la droite
            else:
                theta = pi - theta
                xballe = briques[i][0]-briques[i][3]/2-rballe

        #sinon si elle tape sur le côté droit
        else:
            #si la balle va vers la droite
            if cos(theta) >=0:
                #si la  balle va vers le haut
                if sin(theta)>=0:
                    yballe = briques[i][1]+briques[i][2]/2+rballe
                #sinon
                else:
                    yballe = briques[i][1]-briques[i][2]/2-rballe
                theta = -theta
            #si la balle va vers la gauche
            else:
                theta = pi - theta
                xballe = briques[i][0]+briques[i][3]/2+rballe

        
    elif len(drapeaux) == 2:
        i = drapeaux[0]
        j = drapeaux[1]

        #Si les deux briques se situent à gauche
        if xballe>=(briques[i][0]+briques[i][3]/2) and \
           xballe>=(briques[j][0]+briques[j][3]/2):
            theta = pi - theta
            xballe = briques[i][0]+briques[i][3]/2+rballe
        #Sinon si les deux briques se situent à droite
        elif xballe<=(briques[i][0]-briques[i][3]/2) and \
             xballe<=(briques[j][0]-briques[j][3]/2):
            theta = pi - theta
            xballe = briques[i][0]-briques[i][3]/2-rballe
        #Sinon si les deux briques se situent en haut
        elif yballe>=(briques[i][1]+briques[i][2]/2) and \
             yballe>=(briques[j][1]+briques[j][2]/2):
            theta = -theta
            yballe = briques[i][1]+briques[i][2]/2+rballe
        #Sinon si les deux briques se situent en bas
        elif yballe<=(briques[i][1]-briques[i][2]/2) and \
             yballe<=(briques[j][1]-briques[j][2]/2):
            theta = -theta
            yballe = briques[i][1]-briques[i][2]/2-rballe
        #Sinon si les deux briques sont opposées par rapport à la balle
        else:
            #Si brique i se situe en haut à gauche de brique j
            if briques[i][0]<briques[j][0] and \
               briques[i][1]<briques[j][1]:
                #Si la balle se dirige vers le haut
                if sin(theta)>=0:
                    xballe = min(briques[i][0]+briques[i][3]/2, \
                                 briques[j][0]-briques[j][3]/2)-rballe
                    yballe = max(briques[i][1]+briques[i][2]/2, \
                                 briques[j][1]-briques[j][2]/2)+rballe
                #Sinon si la balle se dirige vers le bas
                if sin(theta)>=0:
                    xballe = max(briques[i][0]+briques[i][3]/2, \
                                 briques[j][0]-briques[j][3]/2)+rballe
                    yballe = min(briques[i][1]+briques[i][2]/2, \
                                 briques[j][1]-briques[j][2]/2)-rballe
            #Sinon si brique i se situe en bas a gauche de brique j
            elif briques[i][0]<briques[j][0] and \
                 briques[i][1]>briques[j][1]:            
                #Si la balle se dirige vers le haut
                if sin(theta)>=0:
                    xballe = max(briques[i][0]+briques[i][3]/2, \
                                 briques[j][0]-briques[j][3]/2)+rballe
                    yballe = max(briques[i][1]-briques[i][2]/2, \
                                 briques[j][1]+briques[j][2]/2)+rballe
                #Sinon si la balle se dirige vers le bas
                if sin(theta)>=0:
                    xballe = min(briques[i][0]+briques[i][3]/2, \
                                 briques[j][0]-briques[j][3]/2)-rballe
                    yballe = min(briques[i][1]-briques[i][2]/2, \
                                 briques[j][1]+briques[j][2]/2)-rballe
            #Sinon si brique j se situe en haut a gauche de brique i
            elif briques[j][0]<briques[i][0] and \
                 briques[j][1]<briques[i][1]:
                #Si la balle se dirige vers le haut
                if sin(theta)>=0:
                    xballe = min(briques[i][0]-briques[i][3]/2, \
                                 briques[j][0]+briques[j][3]/2)-rballe
                    yballe = max(briques[i][1]-briques[i][2]/2, \
                                 briques[j][1]+briques[j][2]/2)+rballe
                #Sinon si la balle se dirige vers le bas
                if sin(theta)>=0:
                    xballe = max(briques[i][0]-briques[i][3]/2, \
                                 briques[j][0]+briques[j][3]/2)+rballe
                    yballe = min(briques[i][1]-briques[i][2]/2, \
                                 briques[j][1]+briques[j][2]/2)-rballe
            #Sinon si brique j se situe en bas à gauche de brique i
            elif briques[j][0]<briques[i][0] and \
                 briques[j][1]>briques[i][1]:
                #Si la balle se dirige vers le haut
                if sin(theta)>=0:
                    xballe = max(briques[i][0]-briques[i][3]/2, \
                                 briques[j][0]+briques[j][3]/2)+rballe
                    yballe = max(briques[i][1]+briques[i][2]/2, \
                                 briques[j][1]-briques[j][2]/2)+rballe
                #Sinon si la balle se dirige vers le bas
                if sin(theta)>=0:
                    xballe = min(briques[i][0]-briques[i][3]/2, \
                                 briques[j][0]+briques[j][3]/2)-rballe
                    yballe = min(briques[i][1]+briques[i][2]/2, \
                                 briques[j][1]-briques[j][2]/2)-rballe
            #Dans tous les cas
            theta = theta + 180

        

                
def mouvementballe():
    """ Fonction permettant de déplacer
    et de tester les collisions de la balle.
    Cette fonction s'appelle elle-même au
    bout d'un temps défini.
    """
    global xballe, yballe, rvballe, theta, rballe, \
           xraquette, LONGUEUR_RAQUETTE, LARGEUR_RAQUETTE ,\
           LARGEUR_ECRAN, HAUTEUR_ECRAN
    xballe, yballe = xballe+rvballe*cos(theta), yballe-rvballe*sin(theta)
    collisionparoi()
    collisionraquette()
    collisionbriques()
    if yballe > (HAUTEUR_ECRAN - 20 - LARGEUR_RAQUETTE/2):
        fin()
    dessin()
    fen.after(20, mouvementballe)


def dessin():

    """ Fonction gérant l'affichage
    de tous les éléments.   
    """
    global xballe, yballe, vxballe, vyballe, rballe, \
           xraquette, LONGUEUR_RAQUETTE, LARGEUR_RAQUETTE ,\
           LARGEUR_ECRAN, HAUTEUR_ECRAN, briques, couleurs, xyoshis, yyoshis, numimages, images
    
    updateyoshi()

    can.delete(ALL)
    can.create_oval(xballe-rballe, yballe-rballe, xballe+rballe, \
                   yballe+rballe, fill = 'red')

    can.create_rectangle(xraquette-(LONGUEUR_RAQUETTE/2), \
                             HAUTEUR_ECRAN - 20 - LARGEUR_RAQUETTE, \
                             xraquette+(LONGUEUR_RAQUETTE/2), \
                             HAUTEUR_ECRAN - 20, fill='green')

    for i in range(8):
        can.create_image(xyoshis[i], yyoshis[i], image=images[numimages[i]])

    for brique in briques:
        if vies[brique[4]]:
            can.create_rectangle(brique[0]-(brique[3]/2), \
                                 brique[1]-(brique[2]/2),\
                                 brique[0]+(brique[3]/2),\
                                 brique[1]+(brique[2]/2),\
                                 fill = couleurs[5-vies[brique[4]]])

        

# Variables globales

LONGUEUR_RAQUETTE, LARGEUR_RAQUETTE, xraquette = 50, 10, 250
LARGEUR_ECRAN, HAUTEUR_ECRAN = 500, 500
rballe, rvballe, theta = 5, 4, pi/2
xballe, yballe = xraquette, HAUTEUR_ECRAN - 20 - LARGEUR_RAQUETTE - rballe

xyoshis = [(LARGEUR_ECRAN/9), (LARGEUR_ECRAN/9)*2,\
           (LARGEUR_ECRAN/9)*3, (LARGEUR_ECRAN/9)*4,\
           (LARGEUR_ECRAN/9)*5, (LARGEUR_ECRAN/9)*6,\
           (LARGEUR_ECRAN/9)*7, (LARGEUR_ECRAN/9)*8]
yyoshis = [74, 74, 74, 74, 74, 74, 74, 74]

numimages = [0, 0, 0, 0, 0, 0, 0, 0]

flag = 0
flagyoshis = [1,1,1,1,1,1,1,1] 

drapeaux = []

couleurs = ['blue','green','cyan','orange','yellow']

briques = [((LARGEUR_ECRAN/9), 100, 20, (LARGEUR_ECRAN/10), 0), \
           ((LARGEUR_ECRAN/9)*2, 100, 20, (LARGEUR_ECRAN/10), 1), \
           ((LARGEUR_ECRAN/9)*3, 100, 20, (LARGEUR_ECRAN/10), 2), \
           ((LARGEUR_ECRAN/9)*4, 100, 20, (LARGEUR_ECRAN/10), 3), \
           ((LARGEUR_ECRAN/9)*5, 100, 20, (LARGEUR_ECRAN/10), 4), \
           ((LARGEUR_ECRAN/9)*6, 100, 20, (LARGEUR_ECRAN/10), 5), \
           ((LARGEUR_ECRAN/9)*7, 100, 20, (LARGEUR_ECRAN/10), 6), \
           ((LARGEUR_ECRAN/9)*8, 100, 20, (LARGEUR_ECRAN/10), 7), \
           ((LARGEUR_ECRAN/9), 125, 20, (LARGEUR_ECRAN/10), 8), \
           ((LARGEUR_ECRAN/9)*2, 125, 20, (LARGEUR_ECRAN/10), 9), \
           ((LARGEUR_ECRAN/9)*3, 125, 20, (LARGEUR_ECRAN/10), 10), \
           ((LARGEUR_ECRAN/9)*4, 125, 20, (LARGEUR_ECRAN/10), 11), \
           ((LARGEUR_ECRAN/9)*5, 125, 20, (LARGEUR_ECRAN/10), 12), \
           ((LARGEUR_ECRAN/9)*6, 125, 20, (LARGEUR_ECRAN/10), 13), \
           ((LARGEUR_ECRAN/9)*7, 125, 20, (LARGEUR_ECRAN/10), 14), \
           ((LARGEUR_ECRAN/9)*8, 125, 20, (LARGEUR_ECRAN/10), 15), \
           ((LARGEUR_ECRAN/9), 150, 20, (LARGEUR_ECRAN/10), 16), \
           ((LARGEUR_ECRAN/9)*2, 150, 20, (LARGEUR_ECRAN/10), 17), \
           ((LARGEUR_ECRAN/9)*3, 150, 20, (LARGEUR_ECRAN/10), 18), \
           ((LARGEUR_ECRAN/9)*4, 150, 20, (LARGEUR_ECRAN/10), 19), \
           ((LARGEUR_ECRAN/9)*5, 150, 20, (LARGEUR_ECRAN/10), 20), \
           ((LARGEUR_ECRAN/9)*6, 150, 20, (LARGEUR_ECRAN/10), 21), \
           ((LARGEUR_ECRAN/9)*7, 150, 20, (LARGEUR_ECRAN/10), 22), \
           ((LARGEUR_ECRAN/9)*8, 150, 20, (LARGEUR_ECRAN/10), 23), \
           ((LARGEUR_ECRAN/9), 175, 20, (LARGEUR_ECRAN/10), 24), \
           ((LARGEUR_ECRAN/9)*2, 175, 20, (LARGEUR_ECRAN/10), 25), \
           ((LARGEUR_ECRAN/9)*3, 175, 20, (LARGEUR_ECRAN/10), 26), \
           ((LARGEUR_ECRAN/9)*4, 175, 20, (LARGEUR_ECRAN/10), 27), \
           ((LARGEUR_ECRAN/9)*5, 175, 20, (LARGEUR_ECRAN/10), 28), \
           ((LARGEUR_ECRAN/9)*6, 175, 20, (LARGEUR_ECRAN/10), 29), \
           ((LARGEUR_ECRAN/9)*7, 175, 20, (LARGEUR_ECRAN/10), 30), \
           ((LARGEUR_ECRAN/9)*8, 175, 20, (LARGEUR_ECRAN/10), 31), \
           ((LARGEUR_ECRAN/9), 200, 20, (LARGEUR_ECRAN/10), 32), \
           ((LARGEUR_ECRAN/9)*2, 200, 20, (LARGEUR_ECRAN/10), 33), \
           ((LARGEUR_ECRAN/9)*3, 200, 20, (LARGEUR_ECRAN/10), 34), \
           ((LARGEUR_ECRAN/9)*4, 200, 20, (LARGEUR_ECRAN/10), 35), \
           ((LARGEUR_ECRAN/9)*5, 200, 20, (LARGEUR_ECRAN/10), 36), \
           ((LARGEUR_ECRAN/9)*6, 200, 20, (LARGEUR_ECRAN/10), 37), \
           ((LARGEUR_ECRAN/9)*7, 200, 20, (LARGEUR_ECRAN/10), 38), \
           ((LARGEUR_ECRAN/9)*8, 200, 20, (LARGEUR_ECRAN/10), 39), \
           ((LARGEUR_ECRAN/9), 225, 20, (LARGEUR_ECRAN/10), 40), \
           ((LARGEUR_ECRAN/9)*2, 225, 20, (LARGEUR_ECRAN/10), 41), \
           ((LARGEUR_ECRAN/9)*3, 225, 20, (LARGEUR_ECRAN/10), 42), \
           ((LARGEUR_ECRAN/9)*4, 225, 20, (LARGEUR_ECRAN/10), 43), \
           ((LARGEUR_ECRAN/9)*5, 225, 20, (LARGEUR_ECRAN/10), 44), \
           ((LARGEUR_ECRAN/9)*6, 225, 20, (LARGEUR_ECRAN/10), 45), \
           ((LARGEUR_ECRAN/9)*7, 225, 20, (LARGEUR_ECRAN/10), 46), \
           ((LARGEUR_ECRAN/9)*8, 225, 20, (LARGEUR_ECRAN/10), 47), \
           ((LARGEUR_ECRAN/9), 250, 20, (LARGEUR_ECRAN/10), 48), \
           ((LARGEUR_ECRAN/9)*2, 250, 20, (LARGEUR_ECRAN/10), 49), \
           ((LARGEUR_ECRAN/9)*3, 250, 20, (LARGEUR_ECRAN/10), 50), \
           ((LARGEUR_ECRAN/9)*4, 250, 20, (LARGEUR_ECRAN/10), 51), \
           ((LARGEUR_ECRAN/9)*5, 250, 20, (LARGEUR_ECRAN/10), 52), \
           ((LARGEUR_ECRAN/9)*6, 250, 20, (LARGEUR_ECRAN/10), 53), \
           ((LARGEUR_ECRAN/9)*7, 250, 20, (LARGEUR_ECRAN/10), 54), \
           ((LARGEUR_ECRAN/9)*8, 250, 20, (LARGEUR_ECRAN/10), 55)]

vies = [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
         1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
         1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
         1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, \
         1, 1, 1, 1, 1, 1, 1, 1]

#brique[0] = abscisse 
#brique[1] = ordonnée
#brique[2] = largeur
#brique[3] = longueur
#brique[4] = numero brique

#-------------- PROGRAMME PRINCIPAL ------------------

# Création du widget principal

fen = Tk()
fen.title("Prototype jeu arkanoid.")
fen.bind("<Left>", mouvementraquettegauche)
fen.bind("<Right>", mouvementraquettedroit)


# Création du canvas

can = Canvas(fen, bg='white', height=HAUTEUR_ECRAN, \
width=LARGEUR_ECRAN)
sprites = PhotoImage(file='spritesyoshi3.gif')
images = [subimage(28*i, 0, 28*(i+1), 31) for i in range(6)]
for i in range(8):
    can.create_image(xyoshis[i], yyoshis[i], image=images[numimages[i]])
updateyoshi()
can.pack()
dessin()

fen.mainloop()
