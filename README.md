# SmashUltimateInfoGenerator
Generates info.toml file based on the folder name

This is a simple tool written in python that generates an info.toml file for Smash Ultimate mods.

## Install requirements
```sh
pip install tomli_w
pip install Pillow
```

## How to use
1. Install python
2. Install above requirements with pip
3. Run main.py file
4. Load the directory of the mod file with files like fighter, sound, effect, ui, etc.
5. Make changes if necessary and click apply

## Done
* Search fighter/{name}/model/body for skin slots in use
* Search for effects, skin, voice, sfx, ui, motion, message in directory to show what is included within the info.toml description
* Renaming image files to preview.webp
* Automatically search what characters are included in the mod file
* Automatically fill in display name(e.g. Sonic C01 Shadow)
* Rename folder name (e.g. Fighter_Sonic[C01]_Shadow)

## To Do 
* Detect victory theme
* Detect camera
* Differentiate message(xmsbt)
* Currently searches model/body for slots. This needs to be fixed to cover everything under models
* Get author, version, and mod name from html?

## Disclaimer
* This tool only looks through what's included in the directory. Currently it cannot get the author and the version of the mod.
* character_names.csv contains all the names of the characters. I don't recommend changing the key column due to the fact that the script uses that value to see which characters are present. You are free to change the custom column. This column is the value that appears in the display name. 
