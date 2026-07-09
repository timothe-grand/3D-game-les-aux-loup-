from ursina import *
from ursina.shaders import basic_lighting_shader
from ursina.shaders import unlit_shader
from direct.actor.Actor import Actor as PandaActor
import ast
import random
import math
from moteur import *
from panda3d.core import loadPrcFileData
loadPrcFileData('', 'load-file-type p3assimp')

LARGEUR = 1000
LONGUEUR = 1000
GRAVITE = -15

ENTITES_PAR_TYPE = 10  
SEUIL_RESPAWN_TYPE = 5 

ANIMAL_POSITIONS = {
    'bear': [
        (-0.99, 3, 42.58), (-49.31, 3, 34.32), (-17.19, 3, 142.65), (20.06, 3, 82.59),
        (-56.17, 3, 159.58), (-5.24, 3, 166.06), (24.39, 3, 160.91), (-54.34, 3, 255.61)
    ],
    'deer': [
        (-46.66, 3, -18.86), (-14.61, 3, 132.01), (10.15, 3, 88.79), (-35.41, 3, 160.77),
        (-9.26, 3, 226.45), (20.23, 3, 151.29), (-40.15, 3, 229.96), (-5.66, 3, 251.6),
        (21.37, 3, 231.97), (-53.51, 3, 319.66), (-4.93, 3, 337.03), (18.78, 3, 314.89)
    ],
    'loutre': [
        (-10.94, 3, 154.06), (28.96, 3, 51.48), (-31.29, 3, 196.29), (0.31, 3, 155.67),
        (8.3, 3, 160.13), (-50.48, 3, 247.24), (7.55, 3, 306.7), (29.14, 3, 291.95),
        (-32.98, 3, 361.89), (1.02, 3, 328.4), (27.33, 3, 319.04), (-10.53, 3, 42.17)
    ],
    'rabbit': [
        (12.24, 3, 38.12), (-45.98, 3, 158.47), (-19.6, 3, 197.06), (23.53, 3, 184.62),
        (-44.95, 3, 286.87), (-10.59, 3, 261.14), (28.7, 3, 221.07), (-34.14, 3, 300.91),
        (-5.9, 3, 362.64), (26.89, 3, 353.44), (-0.16, 3, 77.28), (-47.37, 3, 14.96)
    ]
}

ANIMAL_COUNTS = {
    'bear': 5,
    'deer': 12,
    'loutre': 12,
    'rabbit': 14,
}

ANIMAL_CONFIGS = {
    'bear': {
        'hp': 60,
        'taille': 4,
        'vitesse_marche': 5,
        'vitesse_fuite': 6,
        'entity_scale': 0.2,
        'model_path': 'data/model/Blackbear.glb',
        'model_scale': (0.5, 0.5, 0.5),
        'model_hpr': (0, 0, 0),
    },
    'deer': {
        'hp': 40,
        'taille': 4,
        'vitesse_marche': 5,
        'vitesse_fuite': 6,
        'entity_scale': 1.5,
        'model_path': 'data/model/Deer.glb',
        'model_scale': (1, 1, 1),
        'model_hpr': (0, 0, 0),
    },
    'loutre': {
        'hp': 25,
        'taille': 4,
        'vitesse_marche': 5,
        'vitesse_fuite': 6,
        'entity_scale': 0.2,
        'model_path': 'data/model/otter.glb',
        'model_scale': (0.5, 0.5, 0.5),
        'model_hpr': (0, 0, 0),
    },
    'rabbit': {
        'hp': 10,
        'taille': 1,
        'vitesse_marche': 3,
        'vitesse_fuite': 7,
        'entity_scale': 2,
        'model_path': 'data/model/Rabbit.glb',
        'model_scale': (1, 1, 1),
        'model_hpr': (0, 0, 0),
    },
}

class AnimationController:

    ALIAS = {
        'idle':   ['Idle', 'idle', 'IDLE', 'Stand', 'stand', 'Survey',
                   'Idle_2', 'Idle_Headlow', 'Idle_2_HeadLow',
                   'Armature|Idle', 'AnimalArmature|Idle',
                   'CharacterArmature|Idle', 'CharacterArmature|Idle_Neutral',
                   'ArmatureAction', 'mixamo.com', 'Bunny|Bunny_idle'],
        'walk':   ['Walk', 'walk', 'WALK', 'Walking', 'Trot',
                   'Armature|Walk', 'Armature|Trot',
                   'AnimalArmature|Walk', 'CharacterArmature|Walk',
                   'Bunny|Bunny_walk'],
        'run':    ['Run', 'run', 'RUN', 'Sprint', 'sprint', 'Gallop',
                   'Armature|Run', 'Armature|Sprint',
                   'AnimalArmature|Gallop', 'CharacterArmature|Run'],
        'jump':   ['Jump', 'jump', 'JUMP', 'Leap', 'leap',
                   'Jump_toIdle', 'Jump_ToIdle', 'Gallop_Jump',
                   'Armature|Jump', 'AnimalArmature|Jump_toIdle',
                   'AnimalArmature|Jump_ToIdle', 'AnimalArmature|Gallop_Jump'],
        'fall':   ['Fall', 'fall', 'FALL', 'Falling', 'falling',
                   'Gallop_Jump',
                   'AnimalArmature|Gallop_Jump', 'Jump_toIdle', 'Jump_ToIdle',
                   'AnimalArmature|Jump_toIdle', 'AnimalArmature|Jump_ToIdle',
                   'Armature|Fall'],
        'attack': ['Attack', 'attack', 'ATTACK', 'Bite', 'bite',
                   'Slash', 'slash', 'Attack_Headbutt', 'Attack_Kick',
                   'Armature|Attack', 'AnimalArmature|Attack',
                   'AnimalArmature|Attack_Headbutt',
                   'AnimalArmature|Attack_Kick',
                   'CharacterArmature|Sword_Slash'],
        'death':  ['Death', 'death', 'Die', 'die', 'Dead', 'dead',
                   'Armature|Death', 'AnimalArmature|Death',
                   'CharacterArmature|Death'],
    }

    def __init__(self, entity, model_path, scale=(1, 1, 1),
                 pos_offset=(0, 0, 0), hpr_offset=(0, 0, 0)):
        self.entity        = entity
        self.actor         = None
        self.current_anim  = None
        self.anim_map      = {}   

        try:
            self.actor = PandaActor(model_path)
            self.actor.reparentTo(entity)
            self.actor.setScale(*scale)
            self.actor.setPos(*pos_offset)
            if hpr_offset != (0, 0, 0):
                self.actor.setHpr(*hpr_offset)

            anims = self.actor.getAnimNames()

            for logical, variants in self.ALIAS.items():
                for v in variants:
                    if v in anims:
                        self.anim_map[logical] = v
                        break

            if anims:
                idle_fallback = self.anim_map.get('idle')
                if idle_fallback is None:
                    idle_fallback = next(
                        (anim for anim in anims if 'idle' in anim.lower()),
                        anims[0]
                    )

                walk_fallback = next(
                    (anim for anim in anims if 'walk' in anim.lower() or 'trot' in anim.lower()),
                    idle_fallback
                )
                run_fallback = next(
                    (anim for anim in anims if 'run' in anim.lower() or 'gallop' in anim.lower() or 'sprint' in anim.lower()),
                    walk_fallback
                )
                jump_fallback = next(
                    (anim for anim in anims if 'toidle' in anim.lower() or 'landing' in anim.lower()),
                    next(
                        (anim for anim in anims if 'jump' in anim.lower() and 'toidle' not in anim.lower()),
                        run_fallback
                    )
                )
                fall_fallback = next(
                    (anim for anim in anims if 'gallop_jump' in anim.lower()),
                    run_fallback
                )
                attack_fallback = next(
                    (anim for anim in anims if any(token in anim.lower() for token in ('attack', 'bite', 'slash', 'kick', 'headbutt'))),
                    idle_fallback
                )
                death_fallback = next(
                    (anim for anim in anims if any(token in anim.lower() for token in ('death', 'dead', 'die'))),
                    idle_fallback
                )

                self.anim_map.setdefault('idle', idle_fallback)
                self.anim_map.setdefault('walk', walk_fallback)
                self.anim_map.setdefault('run', run_fallback)
                self.anim_map.setdefault('jump', jump_fallback)
                self.anim_map.setdefault('fall', fall_fallback)
                self.anim_map.setdefault('attack', attack_fallback)
                self.anim_map.setdefault('death', death_fallback)

            self.play('idle')

        except Exception as exc:
            pass

    def play(self, name, loop=True, restart=False):
        if not self.actor:
            return
        actual = self.anim_map.get(name)
        if actual is None:
            return
        if self.current_anim == name and not restart:
            return
        self.current_anim = name
        if loop:
            self.actor.loop(actual)
        else:
            self.actor.play(actual)

    def play_once(self, name, then='idle'):
        if not self.actor:
            return
        actual = self.anim_map.get(name)
        if not actual:
            return
        self.current_anim = name
        self.actor.play(actual)
        try:
            duration = self.actor.getDuration(actual)
        except Exception:
            duration = 1.0
        invoke(self.play, then, delay=duration)

    def update_locomotion(self, vx, vz, vy=0, sprinting=False, in_air=False):
        if self.current_anim in ('attack', 'death'):
            return

        if in_air:
            self.play('jump' if vy >= 0 else 'fall', loop=False)
        elif vx * vx + vz * vz < 0.25:   
            self.play('idle')
        elif sprinting:
            self.play('run')
        else:
            self.play('walk')

    def set_shader(self, ursina_shader):
        if not self.actor:
            return
        try:
            if ursina_shader is None:
                self.actor.clearShader()
            else:
                p3d_shader = (getattr(ursina_shader, '_shader', None)
                              or getattr(ursina_shader, 'compiled', None)
                              or ursina_shader)
                self.actor.setShader(p3d_shader)
        except Exception:
            pass  

    def cleanup(self):
        if self.actor:
            self.actor.cleanup()


class camera_controller(Entity):
    def __init__(self):
        super().__init__()
        self.camera_pivot = Entity(parent=self, y=1.5)
        camera.parent = self.camera_pivot
        camera.fov = 70
        camera.position = (0, -0.2, -7)
        camera.rotation = (0, 0, 0)
        self.rotation_speed = Vec2(40, 40)
        self.rotation_y = 0

    def changer_fov(self, bool=False):
        camera.fov = 75 if bool else 70

    def update(self):
        self.rotation_y += mouse.velocity[0] * self.rotation_speed[1]
        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.rotation_speed[0]
        self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

    def rotation_getter(self):
        return Vec3(0, self.rotation_y + 180, 0)


class Entite:
    def __init__(self, hp, type, entity=None, taille=2, poid=40, terrain=None):
        self.vx = 0
        self.vy = 0
        self.vz = 0
        self.hp = hp
        self.type = type
        self.entity = entity
        self.taille = taille
        self.masse = poid
        self.air = False
        self.vitesse_max = 14
        self.sprint_multiplier = 1.5
        self.saut_force = 8
        self.terrain = terrain
        self.friction = 0.85
        self.chunk_actuel = (0, 0)


class barre:
    def __init__(self, couleur=color.red, offset=Vec3(0, 2.5, 0), truc=None, position=(0, 0)):
        self.truc = truc
        self.couleur = couleur
        self.offset = offset
        self.position = position
        self.barre = Entity(
            parent=camera.ui,
            model='quad',
            color=self.couleur,
            scale=(0.2, 0.025),
            position=position
        )

    def change_couleur(self, unite):
        if unite > 60:
            self.barre.color = color.green
        elif unite > 20:
            self.barre.color = color.yellow
        else:
            self.barre.color = color.red

    def update(self, unite):
        if self.truc == "hp":
            self.change_couleur(unite)
        ratio = max(0.001, unite / 100)
        self.barre.scale_x = 0.2 * ratio
        self.barre.x = self.position[0] + (self.barre.scale_x - 0.2) / 2


class Joueur(Entite):
    def __init__(self, x, y, z, terrain, hp=100):

        self.entite = Entity(position=(x, y, z))
        self.entite.collider = BoxCollider(
            self.entite,
            center=(0, 0.5, 0),
            size=(0.5, 0.8, 0.5)
        )

        self.barre_hp        = barre(couleur=color.red,       truc="hp",   position=(-0.3, 0.43))
        self.barre_endurance = barre(couleur=color.light_gray,             position=(-0.3, 0.38))
        self.barre_faim      = barre(couleur=color.yellow,    truc="faim", position=(-0.3, 0.33))
        Text(text="Vie",     parent=camera.ui, position=(-0.52, 0.435), scale=0.6, color=color.red)
        Text(text="Stamina", parent=camera.ui, position=(-0.52, 0.385), scale=0.6, color=color.light_gray)
        Text(text="Faim",    parent=camera.ui, position=(-0.52, 0.335), scale=0.6, color=color.yellow)
        self.texte_pommes = Text(
            text='Pommes : 0',
            parent=camera.ui,
            position=(-0.52, 0.285),
            scale=0.6,
            color=color.rgb(220, 60, 60)
        )
        self.cursor = Cursor(
            model=Mesh(
                vertices=[(-.5, 0, 0), (.5, 0, 0), (0, -.5, 0), (0, .5, 0)],
                triangles=[(0, 1), (2, 3)],
                mode='line',
                thickness=2
            ),
            scale=.02
        )
        super().__init__(hp, 'loup', self.entite, taille=2.5, terrain=terrain)

        self.anim_ctrl = AnimationController(
            self.entite,
            'data/model/loup2.glb',
            scale=(0.35, 0.4, 0.4)
        )

        self.terrain = terrain
        self.endurance = 100
        self.camera_controller = camera_controller()
        self.endurance_cooldown = -1
        self.endurance_cooldown_duree = 3
        self.en_cooldown = False
        self.faim = 100
        self.max_faim = 100
        self.nb_pommes = 0
        self._sprinting = False

    def faim_f(self, dt):
        if self.faim > 0:
            self.faim -= 1 * dt
        if self.faim <= 1:
            self.hp -= 5 * dt

    def _maj_ui_pommes(self):
        self.texte_pommes.text = f'Pommes : {self.nb_pommes}'

    def ajouter_pomme(self, quantite=1):
        self.nb_pommes += quantite
        self._maj_ui_pommes()

    def manger_pomme(self):
        if self.nb_pommes <= 0 or self.faim >= 100:
            return False
        self.nb_pommes -= 1
        self.faim = min(100, self.faim + 20)
        self._maj_ui_pommes()
        return True

    def mort(self):
        if self.hp <= 0:
            return True
        return False

    def update(self):
        dt = time.dt
        self.camera_controller.position = self.entity.position + Vec3(0, self.taille / 2, 0)
        self.faim_f(dt)
        self.barre_hp.update(self.hp)
        self.barre_endurance.update(self.endurance)
        self.barre_faim.update(self.faim)
        self.entity.rotation = self.camera_controller.rotation_getter()
        foward = camera.forward
        foward.y = 0
        right = camera.right
        right.y = 0
        if held_keys['z']:
            pass
        v = Vec3(0, 0, 0)
        if held_keys['w']:
            v += foward
        if held_keys['s']:
            v -= foward
        if held_keys['d']:
            v += right
        if held_keys['a']:
            v -= right

        if v.length() > 0:
            v = v.normalized() * self.vitesse_max
        else:
            self.vx *= self.friction
            self.vz *= self.friction

        self._sprinting = held_keys['shift'] and self.endurance > 0 and held_keys['w']
        if self._sprinting:
            self.camera_controller.changer_fov(True)
            self.endurance -= 30 * dt
            self.endurance = max(0, self.endurance)
            v *= self.sprint_multiplier
        else:
            if self.endurance <= 0.5 and not self.en_cooldown:
                self.endurance_cooldown = self.endurance_cooldown_duree
                self.en_cooldown = True
            self.endurance_cooldown -= dt
            if self.endurance_cooldown <= 0.5:
                self.en_cooldown = False
                if self.endurance < 100:
                    self.endurance += 20 * dt
                    self.endurance = min(100, self.endurance)
            self.camera_controller.changer_fov()

        if held_keys['space'] and not self.air:
            self.vy = self.saut_force
            self.air = True

        MoteurPhysique.integrer_mouvement(self, v, dt, self.terrain)
        MoteurPhysique.gerer_collisions_sol(self)

        self.anim_ctrl.update_locomotion(
            self.vx, self.vz,
            vy=self.vy,
            sprinting=self._sprinting,
            in_air=self.air
        )


def point_in_rect(other, entity):
    return (entity.entity.x <= other.entity.x <= entity.entity.x + entity.FOV_distance
            and entity.entity.y <= other.entity.y <= entity.entity.y + entity.taille + 3
            and entity.entity.z <= other.entity.z <= entity.entity.z + entity.FOV_distance)


class reaction:
    def __init__(self):
        self.timer = 0
        self.direction_random = Vec3(0, 0, 0)

    def passif(self, entite, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.timer = random.uniform(2, 4)
            self.direction_random = Vec3(
                random.uniform(-1, 1), 0, random.uniform(-1, 1)
            ).normalized()
        entite.vx = self.direction_random.x * entite.vitesse_marche
        entite.vz = self.direction_random.z * entite.vitesse_marche

    def fuite(self, entite, cible):
        direction_fuite = (entite.entity.position - cible.entity.position)
        if direction_fuite.length_squared() > 0:
            direction_fuite = direction_fuite.normalized()
            entite.vx = direction_fuite.x * entite.vitesse_fuite
            entite.vz = direction_fuite.z * entite.vitesse_fuite

    def aggresif(self, entite, cible, dt):
        direction = (cible.entity.position - entite.entity.position)
        if direction.length_squared() > 0:
            direction = direction.normalized()
            entite.vx = direction.x * entite.vitesse_fuite
            entite.vz = direction.z * entite.vitesse_fuite


class animaux(Entite):
    def __init__(self, hp, type, entity=None, taille=1, poid=40,
                 vitesse_marche=2, vitesse_fuite=6, numero=None,
                 model_path=None, model_scale=(1, 1, 1),
                 model_hpr=(0, 0, 0), spawn_index=None):
 
        super().__init__(hp, type, entity, taille, poid)
        self.type = type
        self.reaction = reaction()
        self.etat = "normal"
        self.vitesse_marche = vitesse_marche
        self.vitesse_fuite  = vitesse_fuite
        self.distance_peur  = 30
        self.ia_timer = random.uniform(0, 0.2)
        self.timer = 3
        self.numero = numero
        self.spawn_index = spawn_index
        self.en_mort = False
        self._current_shader = None  

        TYPES_AGRESSIFS = {'bear'}
        self.agressif             = type in TYPES_AGRESSIFS
        self.distance_agro        = 30    
        self.attaque_degats       = 10    
        self.attaque_cooldown_duree = 1.5  
        self._attaque_cooldown    = 0.0    
        self.portée               = 5

        self._pos_precedente      = None   
        self._timer_blocage       = 1.0    
        self._blocage_timer       = random.uniform(0, 1.0)
        self._deblocage_timer     = 0.0    



    def vision(self, joueur):
        distance = (joueur.entity.position - self.entity.position).length_squared()
        if self.agressif:
            if distance < self.distance_agro ** 2:
                self.etat = "agressif"
            else:
                self.etat = "normal"
        else:
            if distance < self.distance_peur ** 2:
                self.etat = "fuite"
            else:
                self.etat = "normal"

    def comportement(self, joueur, dt):
        if self.etat == "normal":
            self.reaction.passif(self, dt)
        elif self.etat == "fuite":
            self.reaction.fuite(self, joueur)
        elif self.etat == "agressif":
            self.reaction.aggresif(self, joueur, dt)
            
            if self._attaque_cooldown <= 0:
                distance = (joueur.entity.position - self.entity.position).length()
                if distance < self.portée:
                    self._attaque_cooldown = self.attaque_cooldown_duree
                    joueur.hp -= self.attaque_degats
                    

    def rotation_vers_mouvement(self, dt):
        direction = Vec3(self.vx, 0, self.vz)
        if direction.length() < 0.01:
            return
        direction = direction.normalized()
        angle = math.degrees(math.atan2(direction.x, direction.z)) + 180
        self.entity.rotation_y = lerp(self.entity.rotation_y, angle, dt * 5)

    def _verifier_blocage(self, dt):
        self._blocage_timer -= dt

        if self._deblocage_timer > 0:
            self._deblocage_timer -= dt
            
            if not self.air:
                self.vy = self.saut_force
                self.air = True
            direction = getattr(self, '_deblocage_dir', Vec3(0, 0, 1))
            self.vx = direction.x * self.vitesse_fuite
            self.vz = direction.z * self.vitesse_fuite
            return

        if self._blocage_timer <= 0:
            self._blocage_timer = 1.0
            pos_actuelle = Vec3(self.entity.x, 0, self.entity.z)

            if self._pos_precedente is not None:
                deplacement = (pos_actuelle - self._pos_precedente).length()
                if deplacement < 0.5 and self.etat == "agressif":
                    self._deblocage_timer = 1.2
                    angle = random.uniform(0, math.pi * 2)
                    self._deblocage_dir = Vec3(math.sin(angle), 0, math.cos(angle))

            self._pos_precedente = pos_actuelle

    def update(self, joueur, chunk=True):
        if chunk:
            dt = time.dt
            self._attaque_cooldown = max(0, self._attaque_cooldown - dt)
            self._verifier_blocage(dt)
            self.ia_timer -= dt
            if self.ia_timer <= 0:
                self.ia_timer = 0.15
                self.vision(joueur)
                if self._deblocage_timer <= 0:
                    self.comportement(joueur, dt)
            self.rotation_vers_mouvement(dt)
            MoteurPhysique.integrer_mouvement(
                self, Vec3(self.vx, self.vy, self.vz), dt, self.terrain
            )
            MoteurPhysique.gerer_collisions_sol(self)


class Tterrain:
    def __init__(self):
        self.sol = Entity(
            model='data/terrain2/TERRAIN.obj',
            collider='mesh',
            position=(0, -1, 0),
            scale=1,
            shader=unlit_shader
        )
        if self.sol.collider:
            self.sol.collider.visible = False

        water_texture = load_texture('data/terrain2/water_texture.png')

        w1_cx = (-107.8 + 179.7) / 2        
        w1_cz = (149.5  + 168.6) / 2      
        w1_sx = 179.7 - (-107.8)              
        w1_sz = 168.6 - 149.5               

        self.eau1 = Entity(
            model='quad',
            texture=water_texture,
            color=color.rgba(0, 120, 220, 200),
            position=(w1_cx, 3.0, w1_cz),
            rotation_x=90,
            scale=(w1_sx, w1_sz, 1),
            shader=unlit_shader,
        )

        w2_cx = (87.4 + 374.8) / 2            
        w2_cz = (11.9 + 299.4) / 2            
        w2_sx = 374.8 - 87.4                  
        w2_sz = 299.4 - 11.9                  

        self.eau2 = Entity(
            model='quad',
            texture=water_texture,
            color=color.rgba(0, 120, 220, 200),
            position=(w2_cx, 2.0, w2_cz),
            rotation_x=90,
            scale=(w2_sx, w2_sz, 1),
            shader=unlit_shader,
        )

        self.tree = []
        self.mur = []
        with open("sources/data/position.txt", "r") as f:
            self.tree_positions = ast.literal_eval(f.read())
        self.tree = []

        PINE_CENTER = Vec3(0.029, 1.35, 0)
        PINE_SIZE   = Vec3(0.75, 3.7, 0.75)

        for pos in self.tree_positions:
            s = random.uniform(1, 3)
            tree = Entity(
                model='pine.glb',
                scale=s,
                position=pos,
            )
            tree.collider = BoxCollider(
                tree,
                center=PINE_CENTER,
                size=PINE_SIZE
            )
            tree.collider.visible = False
            self.tree.append(tree)


class Objet(Entite):
    def __init__(self, entity, terrain, taille=1.5, hp=10, type='objet'):
        super().__init__(hp, type, entity=entity, taille=taille)
        self.terrain = terrain
        self.air = True

    def update(self, chunk=True):
        if chunk:
            dt = time.dt
            direction = Vec3(0, 0, 0)
            MoteurPhysique.integrer_mouvement(self, direction, dt, self.terrain)
            MoteurPhysique.gerer_collisions_sol(self)


class Pomme(Objet):
    def __init__(self, position, terrain):
        entity = Entity(
            model='sphere',
            color=color.rgb(210, 40, 40),
            position=position,
            scale=0.35,
            collider='box',
            shader=unlit_shader
        )
        Entity(
            parent=entity,
            model='cube',
            color=color.rgb(100, 70, 30),
            position=(0, 0.6, 0),
            scale=(0.08, 0.18, 0.08)
        )
        Entity(
            parent=entity,
            model='cube',
            color=color.rgb(70, 170, 70),
            position=(0.12, 0.52, 0),
            rotation_z=25,
            scale=(0.18, 0.05, 0.1)
        )
        super().__init__(entity, terrain, taille=0.5, hp=1, type='pomme')
        self.air = False

    def update(self, chunk=True):
        return


class MenuPrincipal:
    def __init__(self, on_jouer, on_quitter):
        self.visible = True
        self.elements = []

        self.fond = Entity(
            parent=camera.ui,
            model='quad',
            color=color.rgba(0, 0, 0, 200),
            scale=(2, 1),
            z=0.1
        )
        self.elements.append(self.fond)

        self.titre = Text(
            text='SURVIE',
            parent=camera.ui,
            origin=(0, 0),
            position=(0, 0.30),
            scale=5,
            color=color.rgb(200, 230, 255),
        )
        self.elements.append(self.titre)

        self.sous_titre = Text(
            text='Un monde sauvage vous attend...',
            parent=camera.ui,
            origin=(0, 0),
            position=(0, 0.18),
            scale=1.2,
            color=color.rgb(160, 200, 160),
        )
        self.elements.append(self.sous_titre)

        self.btn_jouer = Button(
            text='JOUER',
            parent=camera.ui,
            position=(0, 0.02),
            scale=(0.28, 0.07),
            color=color.rgb(30, 100, 30),
            highlight_color=color.rgb(50, 160, 50),
            pressed_color=color.rgb(20, 70, 20),
            text_color=color.black,
        )
        self.btn_jouer.on_click = on_jouer
        self.elements.append(self.btn_jouer)

        self.btn_quitter = Button(
            text='QUITTER',
            parent=camera.ui,
            position=(0, -0.10),
            scale=(0.28, 0.07),
            color=color.rgb(100, 30, 30),
            highlight_color=color.rgb(160, 50, 50),
            pressed_color=color.rgb(70, 20, 20),
            text_color=color.black,
        )
        self.btn_quitter.on_click = on_quitter
        self.elements.append(self.btn_quitter)

        self.hint = Text(
            text='ZQSD : déplacer  |  Espace : sauter  |  Shift : sprint  |  Clic gauche : attaquer  |  P : Fermer le jeu  |  F : manger les pommes',
            parent=camera.ui,
            origin=(0, 0),
            position=(0, -0.35),
            scale=0.8,
            color=color.rgb(120, 120, 120),
        )
        self.elements.append(self.hint)

        mouse.locked = False

    def cacher(self):
        for e in self.elements:
            e.enabled = False
        self.visible = False
        mouse.locked = True
        mouse.visible = False


class MenuMort:
    def __init__(self, on_rejouer, on_menu, on_quitter):
        self.visible = False
        self.elements = []

        self.fond = Entity(
            parent=camera.ui,
            model='quad',
            color=color.rgba(80, 0, 0, 180),
            scale=(2, 1),
            z=0.1,
            enabled=False
        )
        self.elements.append(self.fond)

        self.titre = Text(
            text='VOUS ÊTES MORT',
            parent=camera.ui,
            origin=(0, 0),
            position=(0, 0.28),
            scale=4,
            color=color.rgb(220, 30, 30),
            enabled=False
        )
        self.elements.append(self.titre)

        self.cause = Text(
            text='',
            parent=camera.ui,
            origin=(0, 0),
            position=(0, 0.14),
            scale=1.2,
            color=color.rgb(200, 160, 160),
            enabled=False
        )
        self.elements.append(self.cause)

        self.btn_rejouer = Button(
            text='RÉESSAYER',
            parent=camera.ui,
            position=(0, 0.00),
            scale=(0.28, 0.07),
            color=color.rgb(30, 80, 30),
            highlight_color=color.rgb(50, 140, 50),
            pressed_color=color.rgb(20, 60, 20),
            text_color=color.black,
            enabled=False
        )
        self.btn_rejouer.on_click = on_rejouer
        self.elements.append(self.btn_rejouer)

        self.btn_menu = Button(
            text='MENU PRINCIPAL',
            parent=camera.ui,
            position=(0, -0.10),
            scale=(0.28, 0.07),
            color=color.rgb(50, 50, 100),
            highlight_color=color.rgb(80, 80, 160),
            pressed_color=color.rgb(30, 30, 70),
            text_color=color.black,
            enabled=False
        )
        self.btn_menu.on_click = on_menu
        self.elements.append(self.btn_menu)

        self.btn_quitter = Button(
            text='QUITTER',
            parent=camera.ui,
            position=(0, -0.22),
            scale=(0.28, 0.07),
            color=color.rgb(100, 30, 30),
            highlight_color=color.rgb(160, 50, 50),
            pressed_color=color.rgb(70, 20, 20),
            text_color=color.black,
            enabled=False
        )
        self.btn_quitter.on_click = on_quitter
        self.elements.append(self.btn_quitter)

    def afficher(self, cause=''):
        self.cause.text = cause
        for e in self.elements:
            e.enabled = True
        self.visible = True
        mouse.locked = False
        mouse.visible = True

    def cacher(self):
        for e in self.elements:
            e.enabled = False
        self.visible = False
        mouse.locked = True
        mouse.visible = False


class Jeu:
    def __init__(self):
        mouse.visible = True
        self.terrain = Tterrain()
        self.chunk_manager = ChunkManager()
        self.joueur = Joueur(0, 200, 0, terrain=self.terrain.sol)
        self.objets = []
        self.mur = []
        self.mort_affiche = False
        self.menu_mort = MenuMort(
            on_rejouer=self.rejouer,
            on_menu=self.retour_menu,
            on_quitter=application.quit
        )
        self._cooldown_attaque = 0
        self._delai_attaque = 0.3

        self._chunk_manager_ready = False
        self.pos_squirel = []

        self.animaux = []
        self._spawn_tous_les_animaux()
        self._spawn_pommes_depart()

        for animal in self.animaux[:]:
            animal.terrain = self.terrain.sol

        self._reconstruire_entites_dynamiques()
        self.entite_stat = self.terrain.tree + self.mur
        self.chunk_manager.init_static(self.entite_stat)
        for e in self.entite:
            self.chunk_manager.enregistrer(e)
        self._chunk_manager_ready = True

    def _spawn_tous_les_animaux(self):
        spawn_index = 0
        for animal_type, count in ANIMAL_COUNTS.items():
            available_positions = ANIMAL_POSITIONS.get(animal_type, [])
            for i in range(count):
                pos_index = i % len(available_positions) if available_positions else 0
                position = available_positions[pos_index]
                self._creer_animal(animal_type, position, spawn_index)
                spawn_index += 1

    def _creer_animal(self, animal_type, position, spawn_index):
        config = ANIMAL_CONFIGS[animal_type]
        position = Vec3(position[0], position[1], position[2])

        animal_entity = Entity(
            model=config['model_path'],   # 🔥 modèle DIRECT
            position=position,
            scale=config['entity_scale'],
            collider='box',
            rotation=config['model_hpr']
        )

        animal = animaux(
            hp=config['hp'],
            type=animal_type,
            entity=animal_entity,
            taille=config['taille'],
            vitesse_marche=config['vitesse_marche'],
            vitesse_fuite=config['vitesse_fuite'],
            numero=spawn_index,
            spawn_index=spawn_index
        )

        animal.terrain = self.terrain.sol
        self.animaux.append(animal)

        if self._chunk_manager_ready:
            self.chunk_manager.enregistrer(animal)
            self._reconstruire_entites_dynamiques()

        return animal

    def _position_sur_sol(self, x, z, y_depart=250):
        hit = raycast(
            Vec3(x, y_depart, z),
            Vec3(0, -1, 0),
            distance=y_depart + 50,
            ignore=self.terrain.tree
        )
        if hit.hit:
            return Vec3(x, hit.world_point.y, z)
        return Vec3(x, 6, z)

    def _proche_arbre(self, x, z, distance_min=6):
        distance_min_carre = distance_min * distance_min
        for pos in self.terrain.tree_positions:
            if hasattr(pos, 'x'):
                px = pos.x
                pz = pos.z
            else:
                px = pos[0]
                pz = pos[2]
            dx = px - x
            dz = pz - z
            if dx * dx + dz * dz < distance_min_carre:
                return True
        return False

    def _trouver_spawn_proche(self, rayon_min, rayon_max, distance_arbres=6, essais=40):
        centre = self.joueur.entity.position
        for _ in range(essais):
            angle = random.uniform(0, math.tau)
            distance = random.uniform(rayon_min, rayon_max)
            x = centre.x + math.cos(angle) * distance
            z = centre.z + math.sin(angle) * distance
            if self._proche_arbre(x, z, distance_min=distance_arbres):
                continue
            return self._position_sur_sol(x, z)
        return self._position_sur_sol(centre.x + rayon_max, centre.z)

    def _creer_pomme(self, position):
        pomme = Pomme(position, self.terrain.sol)
        self.objets.append(pomme)
        if self._chunk_manager_ready:
            self.chunk_manager.enregistrer(pomme)
            self._reconstruire_entites_dynamiques()
        return pomme

    def _spawn_pommes_depart(self):
        for rayon_min, rayon_max in [(8, 18), (10, 22), (12, 25), (25, 45), (30, 55), (35, 65)]:
            position = self._trouver_spawn_proche(rayon_min, rayon_max, distance_arbres=3.5)
            position.y += 0.25
            self._creer_pomme(position)

    def _ramasser_pomme(self, pomme):
        if pomme not in self.objets:
            return
        self.joueur.ajouter_pomme()
        self.chunk_manager.supprimer(pomme)
        destroy(pomme.entity)
        self.objets.remove(pomme)
        self._reconstruire_entites_dynamiques()

    def _reconstruire_entites_dynamiques(self):
        self.entite = [self.joueur] + self.objets + self.animaux

    def _respawn_type_si_necessaire(self, animal_type):
        return

    def update(self):

        if not self.mort_affiche and self.joueur.mort():
            self.mort_affiche = True
            cause = 'Mort de faim' if self.joueur.faim <= 1 else 'Vous avez succombé à vos blessures'
            self.menu_mort.afficher(cause)
            return

        if self.mort_affiche:
            return

        self.joueur.update()
        # cooldown
        self._cooldown_attaque -= time.dt

        if held_keys['left mouse']:
            hit = raycast(
                camera.world_position,
                camera.forward,
                distance=50,
                ignore=[self.joueur.entity, *self.joueur.entity.children]
            )

            if hit.hit and hit.entity:
                for animal in self.animaux:
                    if hit.entity == animal.entity:
                        if self._cooldown_attaque <= 0:
                            self._cooldown_attaque = self._delai_attaque
                            self.joueur.anim_ctrl.play_once('attack', then='idle')

                            animal.entity.color = color.red
                            animal.entity.shader = unlit_shader

                            animal.hp -= 5

                            if animal.hp <= 0 and self.joueur.max_faim>self.joueur.faim:
                                self.joueur.faim += 20

                            break
        self.chunk_manager.chunks_actifs(self.joueur.entity.position)

        if held_keys['p']:
            application.quit()

        for obj in self.objets[:]:
            if not obj.entity.enabled:
                continue
            if obj.type == 'pomme':
                distance = (obj.entity.position - self.joueur.entity.position).length_squared()
                if distance < 2.8 ** 2:
                    self._ramasser_pomme(obj)
            else:
                obj.update()

        for animal in self.animaux[:]:
            if animal.hp <= 0:
                if not animal.en_mort:
                    animal.en_mort = True
                    animal.vx = 0
                    animal.vy = 0
                    animal.vz = 0
                    invoke(self._supprimer_animal, animal, delay=0.5)
                continue

            if not animal.entity.enabled:
                continue

            dist = (animal.entity.position - self.joueur.entity.position).length_squared()
            nouveau_shader = basic_lighting_shader if dist < 900 else unlit_shader

            animal.timer -= time.dt
            
            if animal._current_shader is not nouveau_shader and animal.timer <= 0:
                animal.timer = 0.5
                animal._current_shader = nouveau_shader
                animal.entity.shader = nouveau_shader

            animal.update(self.joueur)

        for e in self.entite:
            self.chunk_manager.maj_entite(e)

    def rejouer(self):
        self.menu_mort.cacher()
        scene.clear()
        global jeu
        jeu = Jeu()
        MoteurChimique.init_meteo()

    def retour_menu(self):
        self.menu_mort.cacher()
        scene.clear()
        global jeu, menu_principal
        jeu = None
        menu_principal = MenuPrincipal(
            on_jouer=demarrer_jeu,
            on_quitter=application.quit
        )

    def _supprimer_animal(self, animal):
        if animal not in self.animaux:
            return
        self.chunk_manager.supprimer(animal)
        destroy(animal.entity)
        self.animaux.remove(animal)
        self._reconstruire_entites_dynamiques()
        self._respawn_type_si_necessaire(animal.type)


app = Ursina()
window.vsync = False
application.target_frame_rate = 120
mouse.locked = False
mouse.visible = True

jeu = None
menu_principal = None


def demarrer_jeu():
    global jeu, menu_principal
    if menu_principal:
        menu_principal.cacher()
    jeu = Jeu()
    MoteurChimique.init_meteo()


menu_principal = MenuPrincipal(
    on_jouer=demarrer_jeu,
    on_quitter=application.quit
)


def update():
    if jeu is not None:
        if held_keys['alt']:
            mouse.locked = False if mouse.locked else True
            mouse.visible = not mouse.locked
        MoteurChimique.update()
        jeu.update()


def input(key):
    global jeu
    if jeu is None:
        return
    if key == 'p':
        application.quit()
    if key == 'f':
        jeu.joueur.manger_pomme()


app.run()