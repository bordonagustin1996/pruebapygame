from random import randint

import pygame

ANCHO, ALTO = 800, 600
RESOLUCION = (ANCHO, ALTO)
RESPAWN = 3000

class Personaje:
    def __init__(self, imagen, velocidad=1, dimensiones=(80, 80), posx=randint(0,ANCHO), posy=randint(0,ALTO)):
        self.imagen = pygame.transform.scale(pygame.image.load(imagen),dimensiones)
        self.posicion = self.imagen.get_rect()
        self.posicion.centerx = posx
        self.posicion.centery = posy
        self.velocidad = velocidad

    def dibujar(self, pantalla):
        pantalla.blit(self.imagen, self.posicion)

    def mover_arriba(self):
        if self.posicion.top > 0:
            self.posicion.centery -= self.velocidad

    def mover_derecha(self):
        if self.posicion.right < ANCHO:
            self.posicion.centerx += self.velocidad

    def mover_abajo(self):
        if self.posicion.bottom < ALTO:
            self.posicion.centery += self.velocidad

    def mover_izquierda(self):
        if self.posicion.left > 0:
            self.posicion.centerx -= self.velocidad

    def detectar_colision(self,lista_personajes):
        c = 0
        for personaje in lista_personajes:
            if self.posicion.top <= personaje.posicion.bottom and self.posicion.bottom >= personaje.posicion.top \
             and self.posicion.right >= personaje.posicion.left and self.posicion.left <= personaje.posicion.right:
                return c
            c+=1
        return -1


class Nave(Personaje):
    def __init__(self):
        super(Nave, self).__init__("Imagenes/spaceship.png", velocidad=5, posx= int(ANCHO/2),posy=ALTO)
        self.lista_disparos= []
        #self.sonido_disparo = pygame.mixer.Sound("Sonidos/disparos.mp3")

    def dibujar(self, pantalla):
        super(Nave, self).dibujar(pantalla)
        for dis in reversed(self.lista_disparos):
            if dis.posicion.top <= 0:
                self.lista_disparos.remove(dis)
            dis.movimiento()
            dis.dibujar(pantalla)



    def disparar(self):
        self.lista_disparos.append(Disparo(self.posicion.centerx,self.posicion.centery))
        #pygame.mixer.Sound.play(self.sonido_disparo)


class Enemigo(Personaje):
    def __init__(self, hardcore = False):
        if hardcore:
            imagen="Imagenes/skull.png"

        else:
            imagen="Imagenes/enemy.png"

        super(Enemigo, self).__init__(imagen,posy=randint(0,int(ALTO/2)),velocidad=1)
        if hardcore:
            self.velocidad=5

        self.destino = (randint(0+self.posicion.width, ANCHO-self.posicion.width), randint(0+self.posicion.height, ALTO-self.posicion.height))
        self.hardcore = hardcore
        self.esta_vivo = True

    def movimiento(self):#MOVIMIENTO ALEATORIO
        x = randint(0, 2000000)
        if 0 <= x < 500000:
            self.mover_arriba()
        if 500000 <= x < 1000000:
            self.mover_derecha()
        if 1000000 <= x < 1500000:
            self.mover_abajo()
        if 1500000 <= x < 2000000:
            self.mover_izquierda()

    def movimiento_trayectoria(self): # MOVIMIENTO CON DIRECCION EN UN PUNTO
        if self.posicion.centerx == self.destino[0] and self.posicion.centery == self.destino[1]:
            self.destino = (randint(0+int(self.posicion.width/2)+1, ANCHO-int(self.posicion.width/2)-1),
                            randint(0+int(self.posicion.height/2)+1, ALTO-int(self.posicion.height/2)-1))
        else:
            if self.posicion.centerx < self.destino[0]:
                self.mover_derecha()
            elif self.posicion.centerx > self.destino[0]:
                self.mover_izquierda()
            if self.posicion.centery < self.destino[1]:
                self.mover_abajo()
            elif self.posicion.centery > self.destino[1]:
                self.mover_arriba()

    def actualizar_destino(self, destino):
        self.destino = destino

    def dibujar(self, pantalla):

        if not self.esta_vivo:
            pantalla.blit(pygame.transform.scale(pygame.image.load("Imagenes/explosion.png"),(self.posicion.width,self.posicion.height)),self.posicion)
        else:
            super(Enemigo, self).dibujar(pantalla)

    def morir(self):

        self.esta_vivo = False
        self.hora_muerte = pygame.time.get_ticks()


class Disparo(Personaje):
    def __init__(self, posx, posy):
        super(Disparo, self).__init__("Imagenes/bullet.png",dimensiones=(20, 20),velocidad=8)
        self.posicion.centerx = posx
        self.posicion.centery = posy

    def movimiento(self):
        self.mover_arriba()


if __name__ == '__main__':


    pygame.init() # INICIALIZAR PYGAME
    pygame.font.init()  # you have to call this at the start,
    # if you want to use this module.
    myfont = pygame.font.SysFont('Arial', 30)
    imagen = pygame.image.load("Imagenes/spaceship.png")#CARGAR UNA IMAGEN
    pantalla = pygame.display.set_mode(RESOLUCION)#INICIALIZAR PANTALLA
    corriendo = True#ACA DECLARAMOS
    pygame.display.set_caption("SORETITOS")#NOMBRE DEL JUEGO O VENTANA
    pygame.display.set_icon(imagen)#ICONO DEL PROGRAMA ESCALADO A X RES (MAS CHICA)
    nave = Nave()#CREAR UNA NAVE
    lista_enemigos = [Enemigo() for _ in range(5)] #CREAR UNA LISTA DE ENEMIGOS
    lista_enemigos = []
    ultimo_score = 0
    for _ in range(5):#CREAMOS UNA LISTA DE ENEMIGOS
        lista_enemigos.append(Enemigo())#ACA LOS AGREGAMOS A LA LISTA

    #TECLAS MOVIMIENTO POR DEFECTO VIENE EN FALSE
    w_bandera = False
    d_bandera = False
    s_bandera = False
    a_bandera = False

    reloj = pygame.time.Clock()#INICIALIZAR RELOJ , LIMITAMOS LOS FPS
    ultimo_enemigo = pygame.time.get_ticks()#DEVUELVE EL TIEMPO EN MS DESDE QUE SE EJECUTA EL PROGRAMA
    enemigos_muertos = []#LISTA DE ENEMIGOS MUERTOS , INICIALIZA EN 0
    score = 10# PUNTAJE ARRANCA EN 0

    while corriendo:#BUCLE PRINCIPAL
        for evento in pygame.event.get():#DEVUELVE EVENTO QUE REALIZA EL USUARIO W,A,S,D
            if evento.type == pygame.QUIT:#CERRAR VENTANA CON LA CRUZ
                corriendo = False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:#CERRAMOS CON LA TECLA ESCAPE
                corriendo = False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_w:#MOVEMOS CON LA W
                w_bandera = True
            if evento.type == pygame.KEYUP and evento.key == pygame.K_w:#CUANDO NO ESTAMOS APRETANDO
                w_bandera = False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_d:#" D
                d_bandera = True
            if evento.type == pygame.KEYUP and evento.key == pygame.K_d:#" D
                d_bandera = False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_s:# " S
                s_bandera = True
            if evento.type == pygame.KEYUP and evento.key == pygame.K_s:#...
                s_bandera = False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_a:
                a_bandera = True
            if evento.type == pygame.KEYUP and evento.key == pygame.K_a:
                a_bandera = False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:#DISPARO CON SPACE
                pygame.mixer.music.load("Sonidos/disparos.wav")#CARGAMOS EL SONIDO DE PEDO(LITERAL)
                pygame.mixer.music.play(1)
                nave.disparar()#LLAMAMOS AL METODO DISPARAR DE LA NAVE

        if ultimo_enemigo + RESPAWN <= pygame.time.get_ticks():#RESPAWN DEL ULTIMO ENEMIGO
            ultimo_enemigo = pygame.time.get_ticks()
            lista_enemigos.append(Enemigo(hardcore=True))#AGREGAMOS UN ENEMIGO NUEVO

        if w_bandera:#MOVIMIENTO DE LA NAVE
            nave.mover_arriba()
        if d_bandera:
            nave.mover_derecha()
        if s_bandera:
            nave.mover_abajo()
        if a_bandera:
            nave.mover_izquierda()

        #DIBUJAR LOS OBJETOS EN LA PANTALLA
        pantalla.fill((255, 255, 255))#PINTAR TODA LA PANTALLA DE COLOR R/ G/ B
        textsurface = myfont.render(f"Score: {score}", False, (0, 0, 0))#AGREGAMOS SUPERFICIE DE TEXTO SCORE
        pantalla.blit(textsurface,(0, 0))#.BLIT TE DIBUJA ALGO EN LA PANTALLA (QUE ES LO QUE DIBUJA , POSICION X, Y)
        if nave.detectar_colision(lista_enemigos)>=0:#CUANDO CHOCAMOS SE CIERRA
             corriendo= False #ACA CIERRA BUCLE


        nave.dibujar(pantalla)#
        for dis in reversed(nave.lista_disparos):#RECORREMOS DE ATRAS LA LISTA
            x = dis.detectar_colision(lista_enemigos)#DEVUELVE EL INDICE DE LA LISTA
            if x >= 0:
                v = lista_enemigos.pop(x)#SEGUN EL INDICE SACAMOS EL ELEMENTO DE LA LISTA
                v.morir()#
                if v.hardcore:
                    score +=5
                else:
                    score +=1
                enemigos_muertos.append(v)#AGREGAMOS AL ENEMIGO A LA LISTA DE ENEMIGOS MUERTOS
                nave.lista_disparos.remove(dis)#REMOVEMOS EL DISPARO

        for enemigo in reversed(enemigos_muertos):#DIBUJAMOS LA EXPLOSION
            enemigo.dibujar(pantalla)
            if enemigo.hora_muerte + 300 <= pygame.time.get_ticks():#DURACION DE LA EXPLOSION
                enemigos_muertos.remove(enemigo)


        for enemigo in lista_enemigos:#RECORREMOS LISTA DE ENEMIGOS
            if enemigo.hardcore:#SI ES HARDCORE
                enemigo.actualizar_destino((nave.posicion.centerx, nave.posicion.centery))#EL HARDCORE VA A LA POSICION DE LA NAVE
            enemigo.movimiento_trayectoria()#
            enemigo.dibujar(pantalla)


        if score % 20==0 and score > 0 and RESPAWN>500 and score - ultimo_score != 0:#RESPAWN
            RESPAWN -= 500
            ultimo_score = score



        pygame.display.update()#APLICAMOS TODOS LOS DIBUJOS

        reloj.tick(60)#LIMITA EL PROCESAMIENTO ¡¡MUY IMPORTANTE!!!
