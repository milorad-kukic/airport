CYAN = 'CYAN'
RED = 'RED';
GREEN = 'GREEN';
BLUE = 'BLUE';

cyan_airliner = {
  call_sign: CYAN,
  type: 'AIRLINER',
  state: 'PARKED',
  known: true
}

red_airliner = {
  call_sign: RED,
  type: 'AIRLINER',
  state: 'PARKED',
  known: false
}

green_private = {
  call_sign: GREEN,
  type: 'PRIVATE',
  state: 'PARKED',
  known: false
}

blue_airliner = {
  call_sign: BLUE,
  type: 'AIRLINER',
  state: 'AIRBORNE',
  known: false
}



actions = [
    {
        description: "RED aircraft that was not know to the system takes off",
        url: '/api/' + red_airliner.call_sign + '/intent/',
        aircraft: red_airliner,
        method: 'intent',
        data: {
            type: red_airliner.type,
            state: red_airliner.state,
            intent: "TAKE_OFF",
        },
        after: function() {
            red_airliner.state = 'TAKE_OFF'
            red_airliner.known = true;
        }
    },

    {
        description: "CYAN wants to take off, but RED is on the runway",
        url: '/api/' + cyan_airliner.call_sign + '/intent/',
        aircraft: cyan_airliner,
        method: 'intent',
        data: {
            state: "TAKE_OFF",
        },
        after: function() {
        }
    },

    {
        description: "RED aircraft signals that is airborne",
        url: '/api/' + red_airliner.call_sign + '/intent/',
        aircraft: red_airliner,
        method: 'intent',
        data: {
            state: "AIRBORNE",
        },
        after: function() {
            red_airliner.state = 'AIRBORNE'
        }
    },

    {
        description: "RED aircraft sends its location",
        url: '/api/' + red_airliner.call_sign + '/location/',
        aircraft: red_airliner,
        method: 'location',
        data: {
            type: "AIRLINER",
            longitude: "20.455516172478386",
            latitude: "44.82128505247063",
            altitude: 2800,
            heading: 220
        },
        after: function() {
            red_airliner.loc = {
                type: "AIRLINER",
                longitude: "20.455516172478386",
                latitude: "44.82128505247063",
                altitude: 2800,
                heading: 220
            }
        }
    },

    {
        description: "GREEN aircraft that was not know to the system takes off",
        url: '/api/' + green_private.call_sign + '/intent/',
        aircraft: green_private,
        method: 'intent',
        data: {
            type: green_private.type,
            state: green_private.state,
            intent: "TAKE_OFF",
        },
        after: function() {
            green_private.state = "TAKE_OFF";
            green_private.known = true;
        }
    },

    {
        description: "GREEN aircraft takes of and becomes AIRBORNE",
        url: '/api/' + green_private.call_sign + '/intent/',
        aircraft: green_private,
        method: 'intent',
        data: {
            state: "AIRBORNE",
        },
        after: function() {
            green_private.state = "AIRBORNE";
        }
    },

    {
        description: "BLUE aircraft that was not know to the system APPROACHES",
        url: '/api/' + blue_airliner.call_sign + '/intent/',
        aircraft: blue_airliner,
        method: 'intent',
        data: {
            type: blue_airliner.type,
            state: blue_airliner.state,
            intent: "APPROACH",
        },
        after: function() {
            blue_airliner.state = "APPROACH";
            blue_airliner.known = true;
        }
    },

    {
        description: "RED tries to APPROACH, but blue is already approaching",
        url: '/api/' + red_airliner.call_sign + '/intent/',
        aircraft: red_airliner,
        method: 'intent',
        data: {
            state: "APPROACH",
        },
        after: function() {
            red_airliner.state = 'AIRBORNE'
        }
    },

    {
        description: "BLUE lands",
        url: '/api/' + blue_airliner.call_sign + '/intent/',
        aircraft: blue_airliner,
        method: 'intent',
        data: {
            state: "LANDED",
        },
        after: function() {
            blue_airliner.state = 'LANDED'
        }
    },

    {
        description: "RED send invalid request by accident",
        url: '/api/' + red_airliner.call_sign + '/intent/',
        aircraft: red_airliner,
        method: 'intent',
        data: {
            state: "TAKE_OFF",
        },
        after: function() {
        }
    },

    {
        description: "RED aproaches for landing",
        url: '/api/' + red_airliner.call_sign + '/intent/',
        aircraft: red_airliner,
        method: 'intent',
        data: {
            state: "APPROACH",
        },
        after: function() {
            red_airliner.state = "APPROACH";
        }
    },

    {
        description: "GREEN aircraft tries to approach but RED is already approaching",
        url: '/api/' + green_private.call_sign + '/intent/',
        aircraft: green_private,
        method: 'intent',
        data: {
            state: "APPROACH",
        },
        after: function() {
        }
    },

    {
        description: "GREEN aircraft sends its location",
        url: '/api/' + green_private.call_sign + '/location/',
        aircraft: green_private,
        method: 'location',
        data: {
            type: "PRIVATE",
            longitude: "20.455516172478386",
            latitude: "44.82128505247063",
            altitude: 3670,
            heading: 250
        },
        after: function() {
            green_private.loc = {
                type: "AIRLINER",
                longitude: "20.455516172478386",
                latitude: "44.82128505247063",
                altitude: 3670,
                heading: 250
            }
        }
    },

    {
        description: "RED wants to land but runway is taken or no parking places",
        url: '/api/' + red_airliner.call_sign + '/intent/',
        aircraft: red_airliner,
        method: 'intent',
        data: {
            state: "LANDED",
        },
        after: function() {
        }
    },

    {
        description: "GREEN aircraft accidentaly sends invalid request (status instead of state).",
        url: '/api/' + green_private.call_sign + '/intent/',
        aircraft: green_private,
        method: 'intent',
        data: {
            status: "APPROACH",
        },
        after: function() {
        }
    },

    {
        description: "SIMULATION FINISHED",
        url: "",
        data: ""
    }

];

