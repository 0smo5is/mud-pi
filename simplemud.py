#!/usr/bin/env python

"""A simple Multi-User Dungeon (MUD) game. Players can talk to each
other, examine their surroundings and move between rooms.

Some ideas for things to try adding:
    * More rooms to explore
    * An 'emote' command e.g. 'emote laughs out loud' -> 'Mark laughs
        out loud'
    * A 'whisper' command for talking to individual players
    * A 'shout' command for yelling to players in all rooms
    * Items to look at in rooms e.g. 'look fireplace' -> 'You see a
        roaring, glowing fire'
    * Items to pick up e.g. 'take rock' -> 'You pick up the rock'
    * Monsters to fight
    * Loot to collect
    * Saving players accounts between sessions
    * A password login
    * A shop from which to buy items

author: Mark Frimston - mfrimston@gmail.com
"""
import time

# import the MUD server class
from mudserver import MudServer

# My WIP attempt at adding items
Items = {
    "Toilet Plunger": {
       "description": "An old Toilet Plunger.",
       "damage": "1",
       "attackspeed": "1",
       "attacktype": "Melee",
    }
}

# structure defining the rooms in the game. Try adding more rooms to the game!
rooms = {
    "Rusty Whistle": {
        "description": "You're in the Rusty Whistle, a cozy tavern " +
        "warmed by an open fire.",
        "exits": {"outside": "Tavern Entrance", "washroom": "Washroom"},
        "items": {},
    },
    "Tavern Entrance": {
        "description": "You're standing outside the Rusty Whistle. " +
        "It's raining.",
        "exits": {"inside": "Rusty Whistle", "alley": "Dark Alley"},
        "items": {},
    },
    "Washroom": {
        "description": "This is the Rusty Whistle's bathroom.",
        "exits": {"tavern": "Rusty Whistle"},
        "items": {"plunger": "Toilet Plunger"},
    },
    "Dark Alley": {
        "description": "A dark alley leading north, beside the Rusty Whistle.",
        "exits": {"entrance": "Tavern Entrance"},
        "items": {},
    },
    "Dimly lit Shop": {
        "description": "Mysterious Goods Vendor",
        "exits": {"ally": "Dark Alley"},
        "items": {},
    },

}

# stores the players in the game
players = {}

# start the server
mud = MudServer()

# main game loop. We loop forever (i.e. until the program is terminated)
while True:

    # pause for 1/5 of a second on each loop, so that we don't constantly
    # use 100% CPU time
    time.sleep(0.2)

    # 'update' must be called in the loop to keep the game running and give
    # us up-to-date information
    mud.update()

    # go through any newly connected players
    for id in mud.get_new_players():

        # add the new player to the dictionary, noting that they've not been
        # named yet.
        # The dictionary key is the player's id number. Start them off in the
        # 'Tavern' room.
        # Try adding more player stats - level, gold, inventory, etc
        players[id] = {
            "name": None,
            "room": "Rusty Whistle",
            "weapon": "Fist",
            "armor": "Cloth Clothing",
            "gold": "0",
            "backpack": "Empty",
            }

        # send the new player a prompt for their name ('\r\n' for telnet)
        mud.send_message(id, "Welcome to my untitled MUD!\r\n" +
                         "Forked from Frimkron/mud-pi @ 0smo5is/mud-pi\r\n" +
                         "What is your name?")

    # go through any recently disconnected players
    for id in mud.get_disconnected_players():

        # if for any reason the player isn't in the player map, skip them and
        # move on to the next one
        if id not in players:
            continue

        # go through all the players in the game
        for pid, pl in players.items():
            # send each player a message to tell them about the diconnected
            # player
            mud.send_message(pid, "{} quit the game".format(
                             players[id]["name"]))

        # remove the player's entry in the player dictionary
        del(players[id])

    # go through any new commands sent from players
    for id, command, params in mud.get_commands():

        # if for any reason the player isn't in the player map, skip them and
        # move on to the next one
        if id not in players:
            continue

        # if the player hasn't given their name yet, use this first command as
        # their name
        if players[id]["name"] is None:
            players[id]["name"] = command

            # go through all the players in the game
            for pid, pl in players.items():

                # send each player a message to tell them about the new player
                mud.send_message(pid, "{} entered the game".format(
                                 players[id]["name"]))

            # send the new player a welcome message
            mud.send_message(id, "Welcome to the game, {}. ".format(
                             players[id]["name"]) +
                             "Type 'commands' for a list of commands.")

            # send the new player the description of their current room
            mud.send_message(id, rooms[players[id]["room"]]["description"])

        # each of the possible commands is handled below. Try adding new
        # commands to the game!

        # 'help' command
        elif command in ("commands", "help"):

            # send the player back the list of possible commands
            mud.send_message(id, "Commands:")
            mud.send_message(id, "  say(/) <message>  - Says something out " +
                                 "loud, e.g. 'say Hello'")
            mud.send_message(id, "  look(l)           - Examines the " +
                                 "surroundings, e.g. 'look'")
            mud.send_message(id, "  go(g) <exit>      - Moves through the " +
                                 "exit specified, e.g. 'go outside'")
            mud.send_message(id, "  equip(e) <item>   - Equips an item ")
            mud.send_message(id, "  inventory(i)      - Check inventory ")

        # 'say' command
        elif command in ("say", "/"):
            # go through every player in the game
            for pid, pl in players.items():
                # if they're in the same room as the player
                if players[pid]["room"] == players[id]["room"]:
                    # send them a message telling them what the player said
                    mud.send_message(pid, "{} says: {}".format(
                                     players[id]["name"], params))

        # 'look' command
        elif command in ("look", "l", "ls"):

            # stores items in room
            it = params.lower()
            # store the player's current room
            rm = rooms[players[id]["room"]]

            # send the player back the description of their current room
            mud.send_message(id, rm["description"])

            if rm["items"] != {}:
                mud.send_message(id, "There is a {} here.".format(
                                 rm["items"][it]))

            playershere = []
            # go through every player in the game
            for pid, pl in players.items():
                # if they're in the same room as the player
                if players[pid]["room"] == players[id]["room"]:
                    # add their name to the list
                    playershere.append(players[pid]["name"])

            # send player a message containing the list of players in the room
            mud.send_message(id, "Players here: {}".format(
                             ", ".join(playershere)))

            # send player a message containing the list of exits from this room
            mud.send_message(id, "Exits are: {}".format(
                             ", ".join(rm["exits"])))

        # 'go' command
        elif command in ("go", "g"):
            # store the exit name
            ex = params.lower()
            # store the player's current room
            rm = rooms[players[id]["room"]]

            # if the specified exit is found in the room's exits list
            if ex in rm["exits"]:
                # go through all the players in the game
                for pid, pl in players.items():
                    # if player is in the same room and isn't the player
                    # sending the command
                    if players[pid]["room"] == players[id]["room"] \
                          and pid != id:
                        # send them a message telling them that the player
                        # left the room
                        mud.send_message(pid, "{} left via exit '{}'".format(
                                         players[id]["name"], ex))

                # update the player's current room to the one the exit leads to
                players[id]["room"] = rm["exits"][ex]
                rm = rooms[players[id]["room"]]

                # go through all the players in the game
                for pid, pl in players.items():
                    # if player is in the same (new) room and isn't the player
                    # sending the command
                    if players[pid]["room"] == players[id]["room"] \
                          and pid != id:
                        # send them a message telling them that the player
                        # entered the room
                        mud.send_message(pid, "{} arrived via '{}'".format(
                                         players[id]["name"], ex))

                # send the player a message telling them where they are now
                mud.send_message(id, "You arrive at '{}'".format(
                             players[id]["room"]))

            # the specified exit wasn't found in the current room
            else:
                # send back an 'unknown exit' message
                mud.send_message(id, "Unknown exit '{}'".format(ex))

        # equip command
        elif command in ("equip", "e"):
            # stores items in room
            it = params.lower()
            # store the player's current room
            rm = rooms[players[id]["room"]]
            if it in rm["items"]:
                players[id]["weapon"] = rm["items"][it]
                mud.send_message(id, "You have equipped '{}'".format(it))
            else:
                mud.send_message(id, "Could not find '{}' in '{}'".format(
                                 it, players[id]["room"]))

        # inventory command
        elif command in ("inventory", "i"):
            # send message about inventory
            mud.send_message(id, "Weapon: {} Armor: {} Gold: {} " +
                             "Backpack: {}".format(players[id]["weapon", "armor", "gold", "backpack"]))

        # some other, unrecognised command
        else:
            # send back an 'unknown command' message
            mud.send_message(id, "Unknown command '{}'".format(command))
