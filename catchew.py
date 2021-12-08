import json, pickle, os, pprint

pokemon_db = []

print("loading pokemon database...")
with open("pokemondataset.json", "r") as pokemon_f:
    for line in pokemon_f:
        pokemon_db.append(json.loads(line))

box = []
coverage_map = {}

class CoverageEntry:
    """entry into coverage map"""
    genders = []
    egg_group = ""
    is_masuda = False
    pokemon = []
    
    def __init__(self, genders, egg_group, is_masuda, pokemon_name):
        self.genders = genders
        self.egg_group = egg_group
        self.is_masuda = is_masuda
        self.pokemon = pokemon_name

    def pretty(self):
        return f"{self.egg_group}: have {'M & F' if len(self.genders) > 1 else self.genders[0]}. {'is masuda' if self.is_masuda else ''}"

if os.path.isfile("box.dill"):
    print("loading box.dill")
    with open("box.dill", "rb") as box_f:
        box = pickle.load(box_f)
    
    print("loading coverage.dill")
    with open("coverage.dill", "rb") as coverage_f:
        coverage_map = pickle.load(coverage_f)

def update_coverage():
    global pokemon_db, box, coverage_map
    
    for pokemon in box:
        pokemon_name = pokemon.split("!")[0].lower()
        pokemon_gender = pokemon.split("!")[1].upper()
        pokemon_region = pokemon.split("!")[2].upper()
        for pokemon_dex in [x for x in pokemon_db if pokemon_name in x["name"].lower()]:
            for egg_group in pokemon_dex["egg_groups"]:
                if egg_group not in coverage_map.keys():
                    coverage_map[egg_group] = CoverageEntry([pokemon_gender], egg_group, (pokemon_region != "ENG"), [pokemon])
                else:
                    if pokemon not in coverage_map[egg_group].pokemon:
                        coverage_map[egg_group].pokemon.append(pokemon)
                    if pokemon_gender not in coverage_map[egg_group].genders:
                        coverage_map[egg_group].genders.append(pokemon_gender)
                    if pokemon_region != "ENG":
                        coverage_map[egg_group].is_masuda = True

def capture(argstring, dry):
    global box, pokemon_db
    
    argstring_parts = argstring.split("!")
    search = argstring_parts[0].lower()
    gender = argstring_parts[1].upper()
    region = argstring_parts[2].upper()

    if gender != "M" and gender != "F":
        if not dry:
            print (f"Invalid gender {gender}!")
        return False

    valid_regions = ["JPN", "ENG", "FRA", "GER", "ITA", "SPA", "KOR", "CHI"]
    if region not in valid_regions:
        if not dry:
            print (f"Invalid region {region}!")
        return False
    
    candidates = [x for x in pokemon_db if search in x["name"].lower()]
    if len(candidates) == 0:
        if not dry:
            print(f"I can't find the pokemon {search}")
    elif len(candidates) > 1:
        if not dry:
            print(f"Be more specific. (matched candidates {[x['name'] for x in candidates]}")
    else:
        if not dry:
            print(f"Matched {[x['name'] for x in candidates]}.")
            box.append(f"{candidates[0]['name']}!{gender}!{region}")
            print(f"Added {gender} {[x['name'] for x in candidates]} with region {region} to the box.")
        return True

def release(argstring, dry):
    global box

    argstring_parts = argstring.split("!")
    search = argstring_parts[0].lower()
    gender = argstring_parts[1].upper()
    region = argstring_parts[2].upper()

    valid_genders = ["M", "F", "N"]
    if gender not in valid_genders:
        if not dry:
            print (f"Invalid gender {gender}!")
        return False

    valid_regions = ["JPN", "ENG", "FRA", "GER", "ITA", "SPA", "KOR", "CHI"]
    if region not in valid_regions:
        if not dry:
            print (f"Invalid region {region}!")
        return False
    
    candidates = [x for x in box if search in x.lower()]
    if len(candidates) == 0:
        if not dry:
            print(f"I can't find the pokemon {gender} {search} with region {region}.")
    elif len(candidates) > 1:
        if not dry:
            print(f"Be more specific. (matched candidates {candidates}")
    else:
        if not dry:
            print(f"Matched {candidates}")
            del box[box.index(candidates[0])]
            print(f"Released {gender} {candidates} with region {region} from the box.")
        return True
    
def trade(argstring, dry):
    argstring_parts = argstring.split("!!")
    pokemon_leaving = argstring_parts[0]
    pokemon_arriving = argstring_parts[1]

    possible = release(pokemon_leaving, True) and capture(pokemon_arriving, True)
    if possible:
        release(pokemon_leaving, False)
        capture(pokemon_arriving, False)
        return True
    else:
        print("Trade invalid!")

def coverage(argstring, dry):
    global coverage_map
    update_coverage()
    for entry in coverage_map.values():
        print(entry.pretty())
    return True

def possible_internal(argstring, dry):
    global pokemon_db, coverage_map, box

    argstring_parts = argstring.split("!")
    search = argstring_parts[0].lower()

    found = False
    for pokemon in box:
        if f"{search}!f" in pokemon.lower():
            #print (f"{search}: {pokemon}")
            found = True

    if not found:
        if not dry:
            print(f"I can't find the female pokemon {search} in your box")
        return False, False
    
    candidates = [x for x in pokemon_db if search in x["name"].lower()]
    if len(candidates) == 0:
        if not dry:
            print(f"I can't find the pokemon {search}")
    elif len(candidates) > 1:
        if not dry:
            print(f"Be more specific. (matched candidates {[x['name'] for x in candidates]}")
    else:
        if not dry:
            print(f"Matched {[x['name'] for x in candidates]}.")

        possible = False
        masuda = False
        recommended_pokemon = ""
        recommend_locked = False
        for egg_group in candidates[0]["egg_groups"]:
            for entry in coverage_map.values():
                if egg_group not in entry.egg_group:
                    continue

                if len(entry.genders) > 1:
                    possible = True
                
                if not recommend_locked:
                    recommended_pokemon = entry.pokemon
                
                if entry.is_masuda:
                    masuda = True
                    recommend_locked = True
                
                if "undiscovered" in entry.egg_group:
                    possible = False
                    masuda = False
        if not dry:
            recommended_pokemon = [x for x in recommended_pokemon if "M" in x]
            print(f"Breeding a {search} is {'possible' if possible else 'impossible'}. ", end='')
            if possible:
                 print(f"{'And it is Masuda!' if masuda else ''} Recommended parents include {recommended_pokemon}")
            else:
                print("")
        return possible, masuda

def possible(argstring, dry):
    return possible_internal(argstring, dry)[0]

def all_possible(argstring, dry):
    global pokemon_db
    for pokemon in pokemon_db:
        p, m = possible_internal(pokemon["name"], True)
        if p:
            print(f"Possible: {pokemon['name']}{'*' if m else ''}")
    return True

def list_groups(argstring, dry):
    global box, pokemon_db
    
    search = argstring.lower()
    
    candidates = [x for x in pokemon_db if search in x["name"].lower()]
    if len(candidates) == 0:
        if not dry:
            print(f"I can't find the pokemon {search}")
    elif len(candidates) > 1:
        if not dry:
            print(f"Be more specific. (matched candidates {[x['name'] for x in candidates]}")
    else:
        if not dry:
            print(f"Matched {[x['name'] for x in candidates]}.")
            print(f"Egg groups: {[x['egg_groups'] for x in candidates]}")
            print(f"Egg cycles: {[x['egg_cycles'] for x in candidates]}")
        return True

def view(argstring, dry):
    print(box)
    return True

def save(argstring, dry):
    with open("box.dill", "wb") as box_f:
        pickle.dump(box, box_f)
    with open("coverage.dill", "wb") as coverage_f:
        pickle.dump(coverage_map, coverage_f)
    return True

def stop(argstring, dry):
    global should_exit
    should_exit = True
    return True

def usage(argstring, dry):
    global commands
    for command in commands.keys():
        print(f"{command}: {commands[command].__name__}")
    return True

def clear_all(argstring, dry):
    global box, coverage_map
    box = []
    coverage_map = {}
    save(argstring, dry)
    print("Alright, if you insist...")
    return True

commands = {"ca": capture,
            "re": release,
            "tr": trade,
            "co": coverage,
            "po": possible,
            "ap": all_possible,
            "lg": list_groups,
            "vi": view,
            "sa": save,
            "q!": stop,
            "h": usage,
            "help": usage,
            "?": usage,
            "clear-all-data-yes-i-mean-to-do-this": clear_all}

should_exit = False
while not should_exit:
    command = input("> ")

    real_command = command.split(" ")[0]
    argstring = ""
    
    if len(command.split(" ")) > 1:
        argstring = command.split(" ")[1]
    
    if real_command in commands.keys():
        #try:
        if commands[real_command](argstring, False):
            print("Success!")
            update_coverage()
        else:
            print("Command failed!")
        #except Exception as err:
        #    print(f"Command failed. ({type(err).__name__})")
    else:
        print("I'm sorry, I don't understand.")
