from ursina import *
import random
import math


class MoteurPhysique:

    GRAVITE = -20

    @staticmethod
    def integrer_mouvement(entite, direction, dt, terrain):

        entite.vy += MoteurPhysique.GRAVITE * dt
        entite.vy = max(entite.vy, -60) 
        dx = direction.x * dt
        dy = entite.vy * dt
        
        dz = direction.z * dt

        position = entite.entity.position

        entite.entity.position += Vec3(dx, dy, dz)
        hit = entite.entity.intersects(ignore=[entite.entity])

        if hit.hit:
            entite.entity.position = position

            entite.entity.x += dx
            hit_x = entite.entity.intersects(ignore=[entite.entity])
            if hit_x.hit:
                entite.entity.x = position.x

            entite.entity.y += dy
            hit_y = entite.entity.intersects(ignore=[entite.entity])
            if hit_y.hit:
                entite.entity.y = position.y
                entite.vy = 0

            entite.entity.z += dz
            hit_z = entite.entity.intersects(ignore=[entite.entity])
            if hit_z.hit:
                entite.entity.z = position.z

        if entite.entity.position.y < -2:
            entite.entity.position = Vec3(position.x, 6, position.z)
            entite.vy = 0

    @staticmethod
    def gerer_collisions_sol(entite):
        if entite.vy > 0.5:
            entite.air = True
            return

        origine = entite.entity.position + Vec3(0, entite.taille / 2, 0)

        hit = raycast(
            origine,
            Vec3(0, -1, 0),
            distance=entite.taille / 2 + 0.1,
            ignore=[entite.entity]
        )

        if hit.hit:
            entite.air = False
            entite.vy = 0
            entite.entity.y = hit.world_point.y
        else:
            entite.air = True


class ChunkManager:

    def __init__(self, taille_chunk=50, distance=1, nb_chunk=20):
        self.chunk_size = taille_chunk
        self.distance = distance
        self.nb_chunk = nb_chunk
        self.chunks = {}
        self.chunks_static = {}
        self.last_chunk = None
        

        for x in range(-nb_chunk, nb_chunk):
            for z in range(-nb_chunk, nb_chunk):
                self.chunks[(x, z)] = []
                self.chunks_static[(x, z)] = []

    def pos_to_chunk(self, x, z):
        return (int(x // self.chunk_size), int(z // self.chunk_size))

    def proche(self, pcx, pcz, cx, cz):
        return abs(cx - pcx) <= self.distance and abs(cz - pcz) <= self.distance

    def init_static(self, entites):
        for e in entites:
            cle = self.pos_to_chunk(e.x, e.z)
            if cle in self.chunks_static:
                self.chunks_static[cle].append(e)

    def enregistrer(self, entite):
        cle = self.pos_to_chunk(entite.entity.x, entite.entity.z)
        entite.chunk_actuel = cle
        if cle in self.chunks:
            self.chunks[cle].append(entite)

    def supprimer(self, entite):
        cle = getattr(entite, 'chunk_actuel', None)
        if cle in self.chunks and entite in self.chunks[cle]:
            self.chunks[cle].remove(entite)

    def maj_entite(self, entite):
        if not hasattr(entite, 'chunk_actuel'):
            self.enregistrer(entite)
            return

        nou = self.pos_to_chunk(entite.entity.x, entite.entity.z)
        an = entite.chunk_actuel

        if nou == an:
            return

        if an in self.chunks:
            self.chunks[an].remove(entite)
        if nou in self.chunks:
            self.chunks[nou].append(entite)

        entite.chunk_actuel = nou

    def activer_dynamiques(self, pcx, pcz):
        for (cx, cz), entites in self.chunks.items():
            proche = self.proche(pcx, pcz, cx, cz)
            for e in entites:
                if e.entity and not e.entity.is_empty():
                    e.entity.enabled = proche

    def activer_statiques(self, pcx, pcz):
        for (cx, cz), entites in self.chunks_static.items():
            proche = self.proche(pcx, pcz, cx, cz)
            for e in entites:
                if e and not e.is_empty():
                    e.enabled = proche

    def chunks_actifs(self, joueur):
        pcx, pcz = self.pos_to_chunk(joueur.x, joueur.z)
        if (pcx, pcz) == self.last_chunk:
            return
        self.last_chunk = (pcx, pcz)
        self.activer_dynamiques(pcx, pcz)
        self.activer_statiques(pcx, pcz)


class CycleJourNuit:

    DUREE_JOUR = 120  

    def __init__(self):
        self.sky = Sky()
        self.lumiere = DirectionalLight()
        self.lumiere.look_at(Vec3(1, -1, 1))
        self.heure = 0.0  

    def update(self):
        self.heure = (self.heure + time.dt / self.DUREE_JOUR) % 1.0
        t = self.heure

        if t < 0.5:
            luminosite = t * 2
        else:
            luminosite = 1 - (t - 0.5) * 2

        c = lerp(Color(0.02, 0.02, 0.1, 1), color.white, luminosite)
        scene.ambient_light = c
        self.lumiere.color = c
        self.sky.color = lerp(Color(0.02, 0.02, 0.1, 1), color.cyan, luminosite)


class MoteurChimique:
    timer = 0
    meteo = None

    @staticmethod
    def init_meteo():
        if MoteurChimique.meteo is None:
            MoteurChimique.meteo = CycleJourNuit()

    @staticmethod
    def update():
        MoteurChimique.timer += time.dt
        if MoteurChimique.meteo is not None:
            MoteurChimique.meteo.update()