#!/usr/bin/python3
#-*- coding:utf-8 -*-

class Rect:
    "Classe dont hérite la plupart des autres classes"
    global can, HAUTEUR_CANVAS, LARGEUR_CANVAS

    def __init__(self, x=0, y=0, w=0, h=0, dx=0, dy=0, color='green'):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.dx = dx
        self.dy = dy
        self.color = color
        self.s = can.create_rectangle(self.x,self.y,(self.x+self.w), (self.y+self.h), fill=color)

    def draw(self):
        global can
        can.coords(self.s, self.x, self.y, self.x+self.w, self.y+self.h)

    def move(self):
        self.x = self.x + self.dx
        self.y = self.y + self.dy
        self.draw()


class Balle(Rect):
    "Classe modélisant la/les balles"

    def __init__(self, x=0, y=0, r=0, dx=0, dy=0, color='red'):
        Rect.__init__(self, x, y, r, r, dx, dy, color)
        self.collisions=[]


    def ajoutCollision(self, impact='GAUCHE'):
        if impact in ['GAUCHE', 'DROITE', 'HAUT', 'BAS']\
                  and impact not in self.collisions:
            self.collisions.append(impact)


    def calculCollision(self):
        if 'HAUT' in self.collisions and 'BAS' in self.collisions:
            self.collision('GAUCHE')
        elif 'GAUCHE' in self.collisions and 'DROITE' in self.collisions:
            self.collision('HAUT')
        else:
            if len(self.collisions) == 1:
                self.collision(self.collisions[0])
            elif len(self.collisions) == 2:
                if 'HAUT' in self.collisions and 'DROITE' in self.collisions:
                    self.collision('HAUTDROITE')
                elif 'HAUT' in self.collisions and 'GAUCHE' in self.collisions:
                    self.collision('HAUTGAUCHE')
                elif 'BAS' in self.collisions and 'DROITE' in self.collisions:
                    self.collision('BASDROITE')
                else:
                    self.collision('BASGAUCHE')
        self.collisions=[]


    def collision(self, impact='GAUCHE'):
        if impact == 'GAUCHE' or impact == 'DROITE':
            self.dx = -self.dx                 # symetrie d'axe celle des ordonnées
        elif impact == 'HAUT' or impact =='BAS':
            self.dy = -self.dy                 # symetrie d'axe celle des abscisses
        elif impact == 'HAUTGAUCHE' or impact == 'BASDROITE':
            c = self.dx
            self.dx = -self.dy                
            self.dy = -c                      
        elif impact == 'BASGAUCHE' or impact == 'HAUTDROITE':
            c = self.dx
            self.dx = self.dy                  
            self.dy = c


    def collisionRaquette(self, deviation=0):
        self.collisions = []
        v = sqrt(self.dx**2 + self.dy**2)  # norme du vecteur vitesse
        theta = pi/6 + deviation*4*pi/6
        self.dx = v*cos(theta)
        self.dy = -v*sin(theta)

    def move(self):
        self.calculCollision()
        Rect.move(self)




class Barre(Rect):
    "Classe modélisant la/les raquettes"
    global flagdepart
    def __init__(self, x=0, y=0, w=0, h=0, color='blue'):
        Rect.__init__(self, x, y, w, h, 0, 0, color) 
    
    def move(self):
        Rect.move(self)
        self.dx = 0

    def collision(self, balle):
        xballe = balle.x + balle.dx
        yballe = balle.y + balle.dy
        if (yballe+balle.h) > self.y and (xballe+balle.w)>self.x \
        and xballe<(self.x+self.w):
            deviation = (self.x+self.w-(xballe+balle.w/2))/(self.w+balle.w)
            balle.collisionRaquette(deviation)

    def deplacementgauche(self, event):
        if self.x>10 and flagdepart:
            self.dx = self.dx - 10

    def deplacementdroite(self, event):
        if (self.x+10+self.w)<LARGEUR_CANVAS and flagdepart:
            self.dx = self.dx + 10

class Brique(Rect):
    "Classe modélisant la/les briques"
    global ajouterAnimation
    couleurs=['yellow','orange','maroon','purple','green']
    def __init__(self, x=0, y=0, w=0, h=0, pv=1):
        Rect.__init__(self, x, y, w, h)
        self.pv = 1

    def move(self):
        global can
        if self.pv > 0:
            Rect.draw(self)

    def collision(self, balle):
        if self.pv >= 1:
            xballe = balle.x + balle.dx                             # on prévoit une collision future
            yballe = balle.y + balle.dy
            if (xballe+balle.w)>self.x and xballe<(self.x+self.w) \
               and (yballe+balle.h)>self.y and yballe<(self.y+self.h):
                if yballe < self.y and balle.dy>0:                          # si la balle est au dessus
                    balle.ajoutCollision('BAS')
                elif (yballe+balle.h) > self.y+self.h and balle.dy < 0:              #sinon si la balle est en-dessous
                    balle.ajoutCollision('HAUT')
                if xballe < self.x and balle.dx>0:                                  # si la balle est à gauche
                    balle.ajoutCollision('DROITE')
                elif (xballe+balle.w) > (self.x+self.w) and balle.dx<0:              #sinon si la balle est a droite
                    balle.ajoutCollision('GAUCHE')
                self.enleverVie()

    def enleverVie(self):
        self.pv -= 1
        can.delete(self.s)
        self.s=can.create_rectangle(self.x, self.y, self.x+self.w, self.y+self.h,\
        fill=Brique.couleurs[(self.pv-1)])
        if self.pv == 0:
            self.die()

    def die(self):
        can.delete(self.s)
        enleverBrique(self)
        ajouterAnimation(self.x, self.y, self.w, self.h)


class Mur(Rect):
    "Classe modélisant les murs"

    def __init__(self, position='GAUCHE'):
        global HAUTEUR_CANVAS, LARGEUR_CANVAS
        if position == 'GAUCHE':
            Rect.__init__(self, 0, 0, 0, HAUTEUR_CANVAS, 0, 0, color=None)
        elif position == 'DROITE':
            Rect.__init__(self, LARGEUR_CANVAS, 0, 0, HAUTEUR_CANVAS, 0, 0, color=None)
        elif position == 'HAUT':
            Rect.__init__(self, 0, 0, LARGEUR_CANVAS, 0, 0, 0, color=None)
        else:
            Rect.__init__(self, 0, HAUTEUR_CANVAS, LARGEUR_CANVAS, 0, 0, 0, color=None)
        self.position = position

    def draw(self):
        pass

    def move(self):
        pass

    def collision(self, balle):
        xballe = balle.x + balle.dx
        yballe = balle.y + balle.dy
        if self.position == 'GAUCHE' and xballe<0:
            balle.ajoutCollision('GAUCHE')
        elif self.position == 'DROITE' and (xballe+balle.w)>self.x:
            balle.ajoutCollision('DROITE')
        elif self.position == 'HAUT' and yballe<0:
            balle.ajoutCollision('HAUT')
        elif self.position == 'BAS' and (yballe+balle.h)>self.y:
            balle.ajoutCollision('BAS')


#----------- CLASSES ANIMATIONS ----------------------


class Masque:
    "Classe gérant l'affichage graphique d'un ElemAnim \
(le déplacement est géré dans la classe Animation )"
    global can, detruireSurface
    def __init__(self, x, y, w, h , nbframes=50, couleur='green'):
        self.color = couleur
        self.surfaces = []
        self.nbframes = nbframes
        self.surfaces.append(can.create_rectangle(x, y, x+w, y+h, outline=self.color, fill=self.color))

    def draw(self, x, y, w, h):
        if self.nbframes:
            self.nbframes -= 1
            self.bougerSurfaces(x, y, w, h)
            if self.nbframes == 0:
                self.detruireSurfaces()
            
    def bougerSurfaces(self, x, y, w, h):
        for surface in self.surfaces:
            can.coords(surface, x, y, x+w, y+h)
 
    def detruireSurfaces(self):
        for surface in self.surfaces:
            detruireSurface(surface)
        self.surfaces = []
            
    def die(self):
        self.detruireSurfaces()


class Contour(Masque):
    " Affiche le rectangle puis un rectangle par dessus de couleur celle d'arrière plan \
et de dimension inférieure afin de laisser voir les contours du rectangle en dessous"
    global can, fen, detruireSurface, COULEUR_ARRIERE_PLAN, TEMPS_FRAME
    def __init__(self, x, y, w, h, nbframes=50, color='green'):
        Masque.__init__(self, x, y, w, h, nbframes, color)
        self.detruireSurfaces()
        self.surfaces.append(can.create_rectangle(x, y, x+w, y+h, outline=self.color,  fill=self.color))
        self.surfaces.append(can.create_rectangle(x+1, y+1, x+w-1, y+h-1, outline = self.color, fill = COULEUR_ARRIERE_PLAN))


    def bougerSurfaces(self, x, y, w, h):
        can.coords(self.surfaces[0], x, y, x+w, y+h)
        can.coords(self.surfaces[1], x+1, y+1, x+w-1, y+h-1)



class FeuArtifice(Masque):
    "Affiche des lignes dans le rectangle à la manière d'un feu d'artifice"
    global can, fen, detruireSurface, TEMPS_FRAME
    def __init__(self, x, y, w, h, nbframes=50, color='green'):
        Masque.__init__(self, x, y, w, h, nbframes, color)
        self.detruireSurfaces()
        self.nblignes = 14
        self.nbframesmax = self.nbframes
        self.theta = 2*pi/self.nblignes
        self.longueurTrait = 10
        self.vitesse = 30 + randrange(70)
        x1 = x + w/2
        y1 = y + h/2
        for i in range(self.nblignes):
            x2 = x1 + self.longueurTrait*cos(i*self.theta)
            y2 = y1 - self.longueurTrait*sin(i*self.theta)
            self.surfaces.append(can.create_line(x1, y1, x2, y2, fill=color, width=2))

    def bougerSurfaces(self, x, y, w, h):
        x0, y0 = x + w/2, y + h/2
        self.nbframes -= 1
        for i in range(self.nblignes):
            x1 = x0 + ((self.nbframesmax-self.nbframes)*cos(i*self.theta)*self.vitesse)//100
            y1 = y0 - ((self.nbframesmax-self.nbframes)*sin(i*self.theta)*self.vitesse)//100
            x2 = x1 + self.longueurTrait*cos(i*self.theta)
            y2 = y1 - self.longueurTrait*sin(i*self.theta)
            can.coords(self.surfaces[i], x1, y1, x2, y2)


class Herisson(Masque):
    "Affiche des lignes dans le rectangle à la manière d'un hérisson"
    global can, fen, detruireSurface, TEMPS_FRAME
    def __init__(self, x, y, w, h, nbframes=50, color='green'):
        Masque.__init__(self, x, y, w, h, nbframes,color)
        self.detruireSurfaces()
        self.nblignes = 8
        self.theta = 2*pi/8
        self.longueurTrait = 5
        x1 = x + w/2
        y1 = y + h/2
        for i in range(self.nblignes):
            x2 = x1 + self.longueurTrait*cos(i*self.theta)
            y2 = y1 - self.longueurTrait*sin(i*self.theta)
            self.surfaces.append(can.create_line(x1, y1, x2, y2, fill=color))

    def bougerSurfaces(self, x, y, w, h):
        x0, y0 = x + w/2, y + h/2
        for i in range(self.nblignes):
            x1 = x0 + self.longueurTrait*cos(i*self.theta)
            y1 = y0 - self.longueurTrait*sin(i*self.theta)
            can.coords(self.surfaces[i], x0, y0, x1, y1)


class Trainee(Masque):
    "Affiche une trainée de rectangle "
    global can, fen, detruireSurface, TEMPS_FRAME
    def __init__(self, x, y, w, h, nbframes=50, color='green'):
        Masque.__init__(self, x, y, w, h, nbframes, color)
        self.phantomes = []
        self.detruireSurfaces()
        self.nbrectangles = 12
        self.coordonnees = []
        for i in range(self.nbrectangles):
            self.surfaces.append(can.create_rectangle(x+(w/4), y+(h/4), x+(3*w/4), y+(3*h/4), fill=self.color, outline=self.color))
            self.coordonnees.append((x, y))
            if i%2 == 0:
                width = (w/2) + (i+1)*w/(2*self.nbrectangles)
                self.phantomes.append(can.create_rectangle(x+(w/2)-(width/2), y, width, h, fill='white', outline='white'))


    def bougerSurfaces(self, x, y, w, h):
        self.coordonnees.append((x, y))
        self.coordonnees = self.coordonnees[1:]
        for i in range(self.nbrectangles):
            width = (w/2) + (i+1)*w/(2*self.nbrectangles)
            x1 = self.coordonnees[i][0]+(w/2)-(width/2)
            y1 = self.coordonnees[i][1]
            x2 = self.coordonnees[i][0]+(w/2)+(width/2) 
            y2 = self.coordonnees[i][1]+h
            can.coords(self.surfaces[i], x1, y1, x2, y2)
            if i%2 == 0:
                can.coords(self.phantomes[i//2], x1, y1, x2, y2)
       

    def detruireSurfaces(self):
        Masque.detruireSurfaces(self)
        for phantome in self.phantomes:
            detruireSurface(phantome)
        self.phantomes = []


class Tornade(Masque):
    "Affiche une tornade "
    def __init__(self, x, y, w, h, nbframes=50, color='green'):
        Masque.__init__(self, x, y, w, h, nbframes, color)
        self.detruireSurfaces()
        self.rayon = 30
        self.x = x+(w//2) -(self.rayon//2)
        self.y = y+(h//2) -(self.rayon//2)
        self.decalage = 5
        self.couleurs=['grey','orange','white']
        for i in range(3):
            theta = (pi/6)+i*2*pi/3
            xcercle = self.x + cos(theta)*self.decalage
            ycercle = self.y - sin(theta)*self.decalage
            self.surfaces.append(can.create_oval(xcercle, ycercle, xcercle+self.rayon, ycercle+self.rayon, fill=self.couleurs[i], outline=self.couleurs[i]))

    def bougerSurfaces(self, x, y, w, h):
        j = (self.nbframes//2)%3
        self.x = x+(w//2)-(self.rayon//2)
        self.y = y+(h//2)-(self.rayon//2)
        for i in range(3):
            theta = (pi/6)+((j+i)%3)*2*pi/3
            xcercle = self.x + cos(theta)*self.decalage
            ycercle = self.y - sin(theta)*self.decalage
            can.coords(self.surfaces[i], xcercle, ycercle, xcercle+self.rayon, ycercle+self.rayon)


class Particules(Masque):
    "affiche des particules de feu qui disparaissent peu à peu"
    def __init__(self, x, y, w, h, nbframes=50, color='green'):
        Masque.__init__(self, x, y, w, h, nbframes, color)
        self.nbframes = 100
        self.detruireSurfaces()
        self.rcarre = 5
        self.nbcarres = 0
        self.numeros = []
        self.x = x + (w//2) -(self.rcarre//2)
        self.y = y + (h//2) -(self.rcarre//2)
        self.ajouterSurface(1)
        self.ajouterSurface(6)
        self.ajouterSurface(2)
        self.ajouterSurface(3)
        self.ajouterSurface(4)
        self.ajouterSurface(8)
        self.ajouterSurface(24)        
        self.ajouterSurface(18)        
        self.ajouterSurface(19)        
        self.ajouterSurface(12)        
        self.ajouterSurface(16)        
        self.ajouterSurface(22)   
        self.ajouterSurface(10)
        self.ajouterSurface(11)
        self.ajouterSurface(21)
        self.ajouterSurface(41)
        self.ajouterSurface(14)
        self.ajouterSurface(46)
        self.ajouterSurface(30)        
        self.ajouterSurface(34)        
        self.ajouterSurface(28)        
        self.ajouterSurface(54)        
        self.ajouterSurface(36)        
        self.ajouterSurface(62)        
        self.pas = self.nbframes//(self.nbcarres)

    def ajouterSurface(self, n):
        pos = self.position(n)
        self.surfaces.append(can.create_rectangle(pos[0], pos[1], pos[0]+self.rcarre, pos[1]+self.rcarre, fill='red', outline='red'))
        self.nbcarres += 1
        self.numeros.append(n)

    def deplacement(self, n):
        if n == 0:
            retour = "RIEN"
        elif n == 1:
            retour = "DEBUT"
        else:
            numcouche = 0
            nbcarre = 1
            while nbcarre<n:
                numcouche += 1
                nbcarre += 8*numcouche
            if n == nbcarre:
                retour = "FIN"
            elif n > (nbcarre-(2*numcouche)):
                retour = "HAUT"
            elif n > (nbcarre-(4*numcouche)):
                retour = "GAUCHE"
            elif n > (nbcarre-(6*numcouche)):
                retour = "BAS"
            else:
                retour = "DROITE"
        return retour


    def position(self, n):
        x = self.x
        y = self.y
        for i in range(n):
            dep = self.deplacement(i)
            if dep == "DEBUT":
                x -= self.rcarre
                y -= self.rcarre
            elif dep == "FIN":
                x -= self.rcarre
                y -= 2*self.rcarre
            elif dep == "DROITE":
                x += self.rcarre
            elif dep == "BAS":
                y += self.rcarre
            elif dep == "GAUCHE":
                x -= self.rcarre
            elif dep == "HAUT":
                y -= self.rcarre
        return (x,y)


    def bougerSurfaces(self, x, y, w, h):
        if self.nbframes%self.pas == 0:
            if self.nbcarres-2 > 0:
                can.delete(self.surfaces[self.nbcarres-1])
                can.delete(self.surfaces[self.nbcarres-2])
                self.surfaces = self.surfaces[:(self.nbcarres-2)]
                self.numeros = self.numeros[:(self.nbcarres-2)]
                self.nbcarres -=2
            elif self.nbcarres > 0:
                can.delete(self.surfaces[self.nbcarres-1])
                self.surfaces = self.surfaces[:(self.nbcarres-1)]
                self.numeros = self.numeros[:(self.nbcarres-1)]
                self.nbcarres -= 1

        for i in range(self.nbcarres):
            pos = self.position(self.numeros[i])
            can.coords(self.surfaces[i], pos[0], pos[1], pos[0]+self.rcarre, pos[1]+self.rcarre)


class ElemAnim(Rect):
    global detruireSurface
    "Elément d'une animation"
    global can
    def __init__(self, x, y, w, h, dx, dy, nbframes=50, m=Masque, couleur='orange'):
        Rect.__init__(self, x, y, w, h, dx, dy)
        can.delete(self.s)
        self.nbframes = nbframes
        self.masque = m(x,y,w,h,self.nbframes, couleur)
        self.affichage = True

    def draw(self):
        if self.affichage:
            self.masque.draw(self.x, self.y, self.w, self.h)

    def die(self):
        self.masque.die()

        
class Animation(Rect):
    "Animation contenant des ElemAnim et gérant leurs déplacements, \
le graphisme des ElemAnim ne depend pas de l'animation mais des masques \
associés"
    global can, enleverAnimation, MASQUE

    def __init__(self, x, y, w, h, m=None):
        Rect.__init__(self, x, y, w, h)
        can.delete(self.s)
        self.animations=[]
        self.nbframes = 50
        if m == None:
            self.masque = MASQUE
        self.ajouterElemAnim(x, y, w, h, 0, 0)

    def move(self):
        if self.nbframes > 0:
            self.nbframes -= 1
            self.draw()
        else:
            self.die()

    def draw(self):
        for elem in self.animations:
            elem.move()

    def die(self):
        for elem in self.animations:
            elem.die()
        enleverAnimation(self)

    def ajouterElemAnim(self, x, y, w, h, dx, dy, couleur='orange', nbframes=None):
        if nbframes == None:
            self.animations.append(ElemAnim(x, y, w, h, dx, dy, self.nbframes, self.masque, couleur))   
        else:
            self.animations.append(ElemAnim(x, y, w, h, dx, dy, nbframes, self.masque, couleur))   


    
class AnimationCirculaire(Animation):
    def __init__(self, x, y, w, h, couleur1=None, couleur2=None, m=None):
        Animation.__init__(self, x, y, w, h, m)
        self.animations[0].die()
        self.nbanimations = 6
        self.animations.remove(self.animations[0])
        if couleur1 != None and couleur2 != None:
            self.couleurs = [couleur1, couleur2]
        else:
            i = randrange(2)
            if i:
                self.couleurs=['orange', 'yellow']
            else:
                self.couleurs=['#0033CC', '#33CC00']
            
        for i in range(self.nbanimations):
            nc = i%(self.nbanimations//2)    #numero de la colonne
            nl = i//(self.nbanimations//2)   #numero de la ligne
            width = w/4
            height = h/4
            xelem = x + w/2 - width/2
            yelem = y + h/2 - height/2
            theta=(pi/self.nbanimations)+i*pi/(self.nbanimations//2)
            v = 1
            if nl == 0:
                self.ajouterElemAnim(xelem, yelem, width, height, \
                                     v*cos(theta), -v*sin(theta), \
                                     self.couleurs[i%2])
            else:
                self.ajouterElemAnim(xelem, yelem, width, height, \
                                     -v*cos(theta), -v*sin(theta), \
                                     self.couleurs[i%2])


class AnimationSpirale(Animation):
    def __init__(self, x, y, w, h, couleur1=None, couleur2=None, m=None):
        Animation.__init__(self, x, y, w, h, m)
        self.animations[0].die()
        self.nbanimations = 6
        self.animations.remove(self.animations[0])
        if couleur1 != None and couleur2 != None:
            self.couleurs = [couleur1, couleur2]
        else:
            i = randrange(2)
            if i:
                self.couleurs=['orange', 'yellow']
            else:
                self.couleurs=['#0033CC', '#33CC00']
            
        for i in range(self.nbanimations):
            nc = i%(self.nbanimations//2)    #numero de la colonne
            nl = i//(self.nbanimations//2)   #numero de la ligne
            width = w/4
            height = h/4
            xelem = x + w/2 - width/2
            yelem = y + h/2 - height/2
            theta=(pi/self.nbanimations)+i*2*pi/(self.nbanimations)
            v = 1
            if nl == 0:
                self.ajouterElemAnim(xelem, yelem, width, height, \
                                     v*cos(theta), -v*sin(theta), \
                                     self.couleurs[i%2])
            else:
                self.ajouterElemAnim(xelem, yelem, width, height, \
                                     -v*cos(theta), -v*sin(theta), \
                                     self.couleurs[i%2])

    def move(self):
        if self.nbframes > 0:
            self.nbframes -= 1
            for element in self.animations:
                theta = 4*pi/180
                xvecteur = element.x+(element.w/2) - (self.x+self.w/2)
                yvecteur = element.y+(element.h/2) - (self.y+self.h/2)
                dxvecteur = element.dx
                dyvecteur = element.dy
                element.x = cos(theta)*xvecteur + sin(theta)*yvecteur + self.x + self.w/2 - element.w/2
                element.y = cos(theta)*yvecteur - sin(theta)*xvecteur + self.y + self.h/2 - element.h/2
                element.dx = cos(theta)*dxvecteur + sin(theta)*dyvecteur
                element.dy = cos(theta)*dyvecteur - sin(theta)*dxvecteur
            self.draw()
        else:
            self.die()


class AnimationHasard(Animation):
    def __init__(self, x, y, w, h, couleur='green', m=None):
        Animation.__init__(self, x, y, w, h, m)
        self.animations[0].die()
        self.nbanimations = 5
        self.nbframes = 100
        self.nbframesanim = self.nbframes//2
        self.ecartframesanim = (self.nbframes-self.nbframesanim)//(self.nbanimations-1)
        self.compteurframes = 0
        self.coordonnees = []
        self.couleurs=['#99FF66','#FFCC33','#33FF00','#6600FF', '#00CCFF']
        self.animations.remove(self.animations[0])
        self.nbpasx = 10
        self.nbpasy = 2
        self.color = couleur
        self.welem = self.w//self.nbpasx
        self.helem = self.h//self.nbpasy
        for i in range(self.nbanimations):
            xelem = self.x + randrange(self.nbpasx)*self.w//self.nbpasx
            yelem = self.y + randrange(self.nbpasy)*self.h//self.nbpasy
            self.coordonnees.append((xelem, yelem))
        coords = self.coordonnees[0]
        self.ajouterElemAnim(coords[0], coords[1], self.welem, self.helem, 0, 0, self.color, self.nbframesanim)
        self.coordonnees = self.coordonnees[1:]
        

    def draw(self):
        self.compteurframes += 1
        if self.compteurframes == self.ecartframesanim:
            self.compteurframes = 0
            if len(self.coordonnees):
                coords = self.coordonnees[0]
                self.ajouterElemAnim(coords[0], coords[1], self.welem, self.helem, 0, 0, self.couleurs[randrange(5)], self.nbframesanim)
                self.coordonnees = self.coordonnees[1:]
        for elem in self.animations:
            elem.move()


#-----------------------------------------------------
#               Jeu
#-----------------------------------------------------



if __name__ == "__main__":
    from tkinter import *
    from math import *
    from random import randrange

    fen = Tk()
    fen.title("Prototype jeu arkanoid.")
    
    #--------- VARIABLES GLOBALES -----------
    HAUTEUR_CANVAS = 500
    LARGEUR_CANVAS = 500
    COULEUR_ARRIERE_PLAN = 'white'
    TEMPS_FRAME = 20
    MASQUE = Particules              # choix : Masque, Contour, FeuArtifice, Herisson, Trainee
    ANIMATION = Animation    # choix : Animation, AnimationCirculaire, AnimationSpirale, AnimationHasard
    can = Canvas(fen, bg=COULEUR_ARRIERE_PLAN, height=HAUTEUR_CANVAS, width=LARGEUR_CANVAS)
    flagdepart = False

    #--------- ELEMENTS DE JEU --------------

    briques = []
    largeur_colonne = LARGEUR_CANVAS/6
    largeur_ligne = HAUTEUR_CANVAS/30
    for i in range(16):
        n = i%4+1               # numero colonne
        m = (i//4)+1            # numero ligne
        briques.append(Brique(n*largeur_colonne, (3+2*m)*largeur_ligne, largeur_colonne-10, largeur_ligne+10))

    balle = Balle(245,440,10, 2, -3)

    murs = []
    murs.append(Mur('GAUCHE'))
    murs.append(Mur('DROITE'))
    murs.append(Mur('HAUT'))
    murs.append(Mur('BAS'))

    raquette = Barre(225, 450, 50, 10)

    animations = []

    #--------- Fonctions de jeu -------------

    def depart(event):
        global flagdepart
        if not flagdepart:
            flagdepart = True
            boucle()

    def enleverBrique(brique):
        if brique in briques:
            briques.remove(brique)

    def ajouterAnimation(x, y, w, h):
        animations.append(ANIMATION(x, y, w, h))

    def enleverAnimation(anim):
        if anim in animations:
            animations.remove(anim)

    def boucle():
        for brique in briques:
            brique.collision(balle)
        for mur in murs:
            mur.collision(balle)
        raquette.collision(balle)

        raquette.move()
        balle.move()
        for anim in animations:
            anim.move()
        fen.after(TEMPS_FRAME, boucle)

    def detruireSurface(s):
        can.delete(s)

    #---------- PROGRAMME -------------

    fen.bind("<Return>", depart)
    fen.bind("<Left>", raquette.deplacementgauche)
    fen.bind("<Right>", raquette.deplacementdroite)


    for brique in briques:
        brique.draw()

    raquette.draw()
    balle.draw()

    can.pack()
    fen.mainloop()
