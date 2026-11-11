sets = {
    
    "unlimited": [ # 2 pull rate tabs (regular, unlimited)
        "neo-destiny",
        "neo-revelation",
        "neo-discovery",
        "neo-genesis",
        "gym-challenge",
        "gym-heroes",
        "team-rocket",
        "fossil",
        "jungle",
        ],

    "shadowless": [ # 3 pull rate tabs (regular, unlimited, shadowless)
        "base-set",
        ],

    "nobooster": [ # No Booster Box tab
        "30th-celebration",
        "ascended-heroes",
        "black-bolt",
        "white-flare",
        "prismatic-evolutions",
        "shrouded-fable",
        "paldean-fates",
        "151",
        "crown-zenith",
        "pokemon-go",
        "celebrations",
        "shining-fates",
        "champions-path",
        "hidden-fates",
        "detective-pikachu",
        "dragon-majesty",
        "shining-legends",
        "generations",
        "double-crisis",
        "dragon-vault",
        ],
}

import json

for i in sets.keys():
    with open(f"{i}.json", "w") as f:
        json.dump(sets[i], f)