# 3D-game-les-aux-loup-

A game I made for the **Trophée NSI** competition with another friend. The main drawback of the project is the lack of optimization, but it was a great opportunity to learn about 3D game development, AI behaviors, physics, and procedural game systems.

## 🎮 About the Game

**3D-game-les-aux-loup-** is a 3D survival game where you play as a wolf trying to survive in a wild environment. You must manage your hunger, fight predators, hunt animals, collect food, and explore the map.

### Features

* 🐺 Play as a wolf
* 🌲 Large 3D forest environment
* 🦌 Wildlife with different behaviors:

  * Rabbits
  * Deer
  * Otters
  * Bears
* 🧠 Animal AI:

  * Passive wandering
  * Escape behavior
  * Aggressive predators
* ❤️ Health, stamina, and hunger system
* 🍎 Apple collection and food management
* 🌅 Day/Night cycle
* 📦 Chunk system for loading nearby entities
* 🎥 Third-person camera
* ⚔️ Combat system with animations

## 🛠️ Built With

* **Python**
* **Ursina Engine**
* **Panda3D**
* Custom physics engine
* Custom chunk loading system

## 🎮 Controls

| Key             | Action        |
| --------------- | ------------- |
| **ZQSD / WASD** | Move          |
| **Mouse**       | Look around   |
| **Shift**       | Sprint        |
| **Space**       | Jump          |
| **Left Click**  | Attack        |
| **F**           | Eat an apple  |
| **P**           | Quit the game |

## 📁 Project Structure

```text
main.py          # Main game loop
moteur.py        # Physics engine, chunk manager and day/night cycle
data/            # Models, terrain and assets
sources/         # Additional game resources
```

## ⚠️ Known Issues

* The game is **not well optimized**.
* AI pathfinding is relatively simple.
* Some assets and animations are still placeholders.
* Performance may decrease when many entities are loaded.

## 🚀 Future Improvements

* Better optimization
* Improved AI with real pathfinding
* Sound effects and music
* Better combat system
* Save system
* More animals and biomes
* Multiplayer support (maybe!)

## 👥 Authors

Developed by two students for the **Trophée NSI** competition.

## 📜 License

This project is intended for educational purposes.
