# -*- coding: utf-8 -*-
"""English version of the story (same structure as historia.py).

The game uses this file when the language is set to ENGLISH in the settings menu.
If you change the story in historia.py, update the same entries here.
"""

INTRO_JUEGO = {
    "titulo": "DUNMORE ASSEMBLY CO. // SECTOR B",
    "lineas": [
        "Good morning. Monday, October 18th, 1982.",
        "",
        "You have been hired as night guard for five nights,",
        "until the plant closes for good: Saturday the 23rd, 6:00 AM.",
        "",
        "Your job: watch the cameras and make sure no one enters the security office.",
        "The entertainment units have been disconnected since March.",
        "If you hear noises, ignore them. It's an old plant.",
        "",
        "Shift: 12:00 AM to 6:00 AM. Do not leave the office.",
        "",
        "                                  E. Varela, Plant Manager",
    ],
}

TITULOS_NOCHE = {
    1: "MONDAY, OCTOBER 18, 1982",
    2: "TUESDAY, OCTOBER 19, 1982",
    3: "WEDNESDAY, OCTOBER 20, 1982",
    4: "THURSDAY, OCTOBER 21, 1982",
    5: "FRIDAY, OCTOBER 22, 1982 // LAST NIGHT",
    6: "SATURDAY, OCTOBER 30, 1982 // OVERTIME",
}

DIALOGOS_NOCHES = {
    1: [
        "--- INCOMING TRANSMISSION: SHIFT SUPERVISION (NIGHT 1) ---",
        "Hello? Can you hear me? Good. Welcome to the Dunmore plant. I'm calling from supervision.",
        "That office used to belong to the plant manager. It's the only one with its own exit, that's why it has a blast door.",
        "On your left, the blast door [A key]. If you see Penny at the door, close it.",
        "On your right, the shutter: HOLD THE BUTTON DOWN if you see Rusty Bunny at the glass.",
        "If Barnaby comes down the hallway, blind him with the flashlight [F]. Don't keep it on too long: it overheats.",
        "Above you [W] is the air vent. Sealing it [SPACE] cuts off your air. Use it sparingly.",
        "If something fails, the panel [M] reboots turbines and cameras. Oh, and if you hear breathing behind the door... close it.",
        "They're old units. They move a little at night. It's nothing personal. Good night.",
    ],
    2: [
        "--- INCOMING TRANSMISSION: SHIFT SUPERVISION (NIGHT 2) ---",
        "You're still there. Good. The last guard didn't come back for the second night. Quit, I guess.",
        "Silas was the maintenance unit. It learned to crawl into the air ducts.",
        "On the duct map you have an AUDIO LURE: use it to draw it away from the office.",
        "And right-clicking a duct closes its gate. If it passes through there, it goes back to the start.",
        "Night vision [V] freezes them while you watch, but the IR battery doesn't last long.",
        "If you hear knocking on the ceiling, it's Silas at the vent. Look up and seal it in time.",
        "Several technicians quit back in March. Lots of paperwork. Doesn't matter. Good night.",
    ],
    3: [
        "--- INCOMING TRANSMISSION: SHIFT SUPERVISION (NIGHT 3) ---",
        "Starting tonight, the backup generator in CAM_08 is losing voltage.",
        "Hold down the coil button in CAM_08 so it doesn't run out.",
        "If the coil hits zero, the office lights fail and Rusty runs much faster.",
        "Rusty was from the warehouse... I mean, the warehouse unit. They calibrated it there.",
        "If you find old tapes around the plant, don't listen to them. They're company property.",
        "Don't ask about March. Good night.",
    ],
    4: [
        "--- PLAYING ARCHIVED TAPE // 03-MAR-1982 // 02:52 AM ---",
        "'This is Walter Ibarra, night shift foreman. If anyone hears this...'",
        "'Varela locked the emergency exits with new padlocks this afternoon. Says it's because of theft.'",
        "'Boiler three is over pressure and he won't let us shut the furnaces down. There's an order to fill.'",
        "'Marta went to close the valves. Tomás is in the ducts. Rubén went for the master key.'",
        "'If this goes wrong, let it be known it was Varela. Let it be known we didn't qu...'",
        "--- [CUT] --- Sorry. That tape shouldn't have been in the system. Keep an eye on the coil.",
    ],
    5: [
        "--- FINAL TRANSMISSION // PRIVATE LINE ---",
        "You heard the tape. So there's no point pretending anymore. This is Ernesto Varela.",
        "I signed the order to keep the furnaces on. I changed the locks. There was an order. There were deadlines.",
        "They're not looking for you. They're looking for this office. The exit. They're looking for me.",
        "Tonight they're all awake. Charge the coil, use the lure, close everything.",
        "At 6:00 the plant gets sealed forever. With them inside. And what happened in March, too.",
        "Hold on until six. After that, nobody has to know anything.",
    ],
    6: [
        "--- INCOMING TRANSMISSION: DISTRICT ATTORNEY, INDUSTRIAL CRIMES DIVISION ---",
        "This is Inspector Ledesma. Thank you for taking one more night. The plant gets demolished on Monday.",
        "We need someone to guard the sector until we remove the evidence. Just tonight.",
        "Going through the inventory we found something in the basement: a 'Unit 0'. The first prototype.",
        "According to the papers, Varela calibrated it himself. For the owners' demonstration.",
        "The other units are still powered on. We don't know why. Or why Unit 0 is no longer in the basement.",
        "A technician said something strange: that Unit 0 'only moves when nobody is watching it'.",
        "If you find it on the cameras, don't take your eyes off it. And if it reaches the hallway, stare at it until it backs off.",
        "Good luck. I mean it.",
    ],
}

CINTAS = {
    1: {
        "titulo": "TAPE 1 OF 4 // 03-MAR-1982 // 02:41 AM",
        "personaje": "WALTER IBARRA, FOREMAN",
        "intro": [
            "The conveyor belts never stop: Varela won't let the line shut down.",
            "Walter wants to record a message on the tape recorder in the back office.",
            "Cross the belts without getting hit by the boxes. The belts drag you along.",
        ],
        "objetivo": "REACH THE TAPE RECORDER",
        "pista": "Something glints beside one of the belts...",
        "outro": [
            "WALTER: 'This is Walter Ibarra. If anyone hears this...'",
            "He recorded everything he knew. He hid the tape in the security system.",
            "Forty minutes later, Barnaby's servos moved on their own for the first time.",
        ],
        "prueba": "W. IBARRA'S TIME CARD",
        "prueba_detalle": "Clock in: 10:00 PM. Clock out: (blank).",
    },
    2: {
        "titulo": "TAPE 2 OF 4 // 03-MAR-1982 // 02:58 AM",
        "personaje": "MARTA PEÑA, WELDER",
        "intro": [
            "Boiler three is out of control. The pressure keeps rising.",
            "Close the three valves IN ORDER (1, 2, 3) before it explodes.",
            "Watch out for the steam vents: they push you back and raise the pressure.",
        ],
        "objetivo": "CLOSE VALVES 1 - 2 - 3",
        "pista": "There's a letterhead paper on the desk in the back...",
        "outro": [
            "The valves closed. The boiler room door didn't: it had a new padlock.",
            "Marta waited by the furnaces.",
            "Months later they found Penny in the same spot. Intact. Warm.",
        ],
        "prueba": "INTERNAL MEMO SIGNED BY E. VARELA",
        "prueba_detalle": "'DO NOT SHUT DOWN THE FURNACES UNDER ANY CIRCUMSTANCES. FILL THE ORDER.'",
    },
    3: {
        "titulo": "TAPE 3 OF 4 // 03-MAR-1982 // 03:06 AM",
        "personaje": "TOMÁS SILVA, VENTILATION TECHNICIAN",
        "intro": [
            "Smoke fills Sector B. Tomás goes into the ducts to start the turbine.",
            "It's dark: you can only see what your flashlight shows.",
            "The fans spin on and off. Don't cross while they're running.",
        ],
        "objetivo": "START THE EXHAUST TURBINE",
        "pista": "There's a rolled-up blueprint in some dead-end duct...",
        "outro": [
            "The turbine started and the smoke began to clear.",
            "Tomás followed the air to the exit grate. It was welded shut from the outside.",
            "Silas never came down from the ducts again.",
        ],
        "prueba": "SECTOR B EVACUATION PLAN",
        "prueba_detalle": "All four emergency exits are crossed out by hand. Signed: E.V.",
    },
    0: {
        "titulo": "TAPE 0 // 02-MAR-1982 // 23:50",
        "personaje": "ERNESTO VARELA, PLANT MANAGER",
        "intro": [
            "This time you are Ernesto Varela, the plant manager.",
            "The Holloway Parks order ships tomorrow. Nobody leaves until it's done.",
            "Change the padlocks on all four exits without the night shift seeing you.",
        ],
        "objetivo": "CHANGE THE 4 PADLOCKS AND RETURN TO YOUR OFFICE",
        "pista": "Someone left a piece of paper in the tool room...",
        "outro": [
            "Varela closed the last padlock and put the keys in his desk.",
            "He slept in the office that night. The furnaces stayed on.",
            "Three hours later, none of the four exits would open.",
        ],
        "prueba": "LOCKSMITH RECEIPT",
        "prueba_detalle": "'4 security padlocks. Paid in cash. E. Varela. No invoice.'",
    },
    4: {
        "titulo": "TAPE 4 OF 4 // 03-MAR-1982 // 03:15 AM",
        "personaje": "RUBÉN 'RUSTY' ORTIZ, WAREHOUSE",
        "intro": [
            "The master key opens the warehouse emergency exit.",
            "It's in the management archive. Someone is patrolling the archive with a flashlight.",
            "Don't let him see you. Grab the key and go back to the door.",
        ],
        "objetivo": "GRAB THE KEY AND RETURN TO THE EXIT",
        "pista": "One of the archive drawers was left half open...",
        "outro": [
            "Rubén reached the exit with the master key.",
            "The key didn't fit. Varela had changed the padlock that same afternoon.",
            "He pounded on the glass until dawn. Rusty still does.",
        ],
        "prueba": "NIGHT SHIFT PAYROLL",
        "prueba_detalle": "Four names crossed out with the note: 'RESIGNED. DO NOT REPORT.'",
    },
}

FINAL_NORMAL = {
    "periodico": {
        "cabecera": "THE INDUSTRIAL CHRONICLE",
        "fecha": "SATURDAY, OCTOBER 23, 1982  //  MORNING EDITION",
        "titular": "DUNMORE PLANT CLOSES ITS DOORS",
        "bajada": "MANAGEMENT SEALS SECTOR B AND DISMANTLES THE LINES",
        "articulo": [
            "Dunmore Assembly closed its Sector B",
            "plant this morning after years of losses",
            "and repeated electrical failures.",
            "",
            "Plant manager Ernesto Varela stated",
            "that 'no one was ever injured in the",
            "plant's history' and that the",
            "entertainment units will be destroyed.",
            "",
            "The last night guard could not be",
            "reached by this newspaper.",
        ],
        "pie_foto": "Mechanical units confined in Sector B.",
        "sello": "CASE CLOSED",
    },
    "titulo": "ENDING: CASE CLOSED",
    "lineas": [
        "You survived all five nights.",
        "At 6:00 AM the blast doors sealed shut. With them inside.",
        "The tapes never left the plant. Nobody asked about March.",
        "",
        "But at 3 AM, in Sector B, four units are still looking for the exit.",
        "",
        "(There's evidence you didn't find. Check the 1982 ARCHIVE in the menu.)",
    ],
}

FINAL_VERDADERO = {
    "periodico": {
        "cabecera": "THE INDUSTRIAL CHRONICLE",
        "fecha": "MONDAY, OCTOBER 25, 1982  //  SPECIAL EDITION",
        "titular": "THE TRUTH ABOUT SECTOR B",
        "bajada": "FOUR WORKERS DIED IN MARCH. PLANT MANAGER ARRESTED",
        "articulo": [
            "A night guard handed over to the police",
            "four pieces of evidence found at Dunmore:",
            "a time card, a memo, a blueprint",
            "and a falsified payroll.",
            "",
            "Walter Ibarra, Marta Peña, Rubén Ortiz and",
            "Tomás Silva did not resign: they died on",
            "March 3rd, locked in on the orders of",
            "Ernesto Varela, now under arrest.",
            "",
            "Their families can finally say goodbye.",
        ],
        "pie_foto": "Ernesto Varela, leaving the courthouse.",
        "sello": "CASE REOPENED",
    },
    "titulo": "TRUE ENDING: END OF SHIFT",
    "lineas": [
        "You survived all five nights. And you took the evidence with you.",
        "",
        "On Sunday, the police opened the emergency exits of Sector B.",
        "Barnaby, Penny, Rusty and Silas were sitting in front of the open door.",
        "Powered down. For the first time since March.",
        "",
        "Walter, Marta, Rubén and Tomás finished their shift.",
        "",
        "THANK YOU FOR PLAYING.",
    ],
}

FRASES_ALUCINACION = [
    "FINISH THE SHIFT",
    "THE EXITS WERE LOCKED",
    "VARELA KNEW",
    "WE DIDN'T QUIT",
    "WHY DIDN'T THEY OPEN?",
    "03-MAR-1982 // 03:15 AM",
]

FINAL_NOCHE6 = {
    "titulo": "OVERTIME",
    "lineas": [
        "6:00 AM. The sun came in through the Sector B window.",
        "",
        "Unit 0 was standing in the hallway, facing the office.",
        "Motionless. Like someone waiting for permission to leave.",
        "",
        "On Monday, the bulldozers tore down the Dunmore plant.",
        "In the basement they found a chair facing four dead monitors.",
        "",
        "There's no one left on shift.",
    ],
}

LLAMADA_EQUIVOCADA = [
    "--- INCOMING TRANSMISSION: UNKNOWN ORIGIN ---",
    "...hello? Walter? Is that you? The line is really bad...",
    "...the boiler room door won't open. I tried the key and it doesn't fit...",
    "...it's so hot in here, Walter. So hot...",
    "...if you see Varela tell him to open up. Tell him we're still here...",
    "--- [LINE DISCONNECTED] ---",
]

CINTA_SECRETA = {
    "titulo": "TAPE 0 // 02-MAR-1982 // 11:40 PM // E. VARELA'S PERSONAL RECORDER",
    "lineas": [
        "'Note to self. Tomorrow the Holloway Parks order arrives.'",
        "'If it doesn't ship on time, the owners close Sector B and I lose my plant.'",
        "'The night shift has been taking tools home. I'm changing the locks.'",
        "'The emergency exits too. Nobody leaves until the order is done.'",
        "'The furnaces stay on. The boiler can hold one more night.'",
        "'...One more night. What could go wrong.'",
        "",
        "--- END OF TAPE ---",
    ],
}

CREDITOS = [
    ("FNAF: INDUSTRIAL SECTOR (1982)", "titulo"),
    ("", ""),
    ("IDEA, DESIGN AND DIRECTION", "seccion"),
    ("alan4352", "nombre"),
    ("", ""),
    ("PROGRAMMING", "seccion"),
    ("alan4352", "nombre"),
    ("", ""),
    ("ART AND SPRITES", "seccion"),
    ("alan4352", "nombre"),
    ("", ""),
    ("STORY", "seccion"),
    ("Dunmore Assembly Co. and the night shift of March 3rd, 1982", "nombre"),
    ("", ""),
    ("IN MEMORY OF", "seccion"),
    ("Walter Ibarra  //  Marta Peña  //  Rubén Ortiz  //  Tomás Silva", "nombre"),
    ("(fictional characters)", "nota"),
    ("", ""),
    ("MADE WITH", "seccion"),
    ("Python and Pygame", "nombre"),
    ("", ""),
    ("Inspired by Five Nights at Freddy's, by Scott Cawthon.", "nota"),
    ("This is a non-profit fan game.", "nota"),
    ("", ""),
    ("", ""),
    ("THANK YOU FOR PLAYING", "titulo"),
]
