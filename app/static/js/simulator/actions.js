RED = 'RE2408';
GREEN = 'GR1234';
BLUE = 'BL0013';

red_airliner = {
  call_sign: RED,
  type: 'AIRLINER',
  state: 'PARKED',
  known: false
}

green_airliner = {
  call_sign: GREEN,
  type: 'AIRLINER',
  state: 'PARKED',
  known: false
}

blue_private = {
  call_sign: BLUE,
  type: 'PRIVATE',
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
            longitude: "",
            latitude: "",
            altitude: 2800,
            heading: 220
        },
        after: function() {
        }
    },

    {
        description: "GREEN aircraft that was not know to the system takes off",
        url: '/api/' + green_airliner.call_sign + '/intent/',
        aircraft: green_airliner,
        method: 'intent',
        data: {
            type: green_airliner.type,
            state: green_airliner.state,
            intent: "TAKE_OFF",
        },
        after: function() {
            green_airliner.state = "TAKE_OFF";
            green_airliner.known = true;
        }
    },

    {
        description: "GREEN aircraft takes of and becomes AIRBORNE",
        url: '/api/' + green_airliner.call_sign + '/intent/',
        aircraft: green_airliner,
        method: 'intent',
        data: {
            state: "AIRBORNE",
        },
        after: function() {
            green_airliner.state = "AIRBORNE";
        }
    },

    {
        description: "BLUE aircraft that was not know to the system APPROACHES",
        url: '/api/' + blue_private.call_sign + '/intent/',
        aircraft: blue_private,
        method: 'intent',
        data: {
            type: blue_private.type,
            state: blue_private.state,
            intent: "APPROACH",
        },
        after: function() {
            blue_private.state = "APPROACH";
            blue_private.known = true;
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
        url: '/api/' + blue_private.call_sign + '/intent/',
        aircraft: blue_private,
        method: 'intent',
        data: {
            state: "LANDED",
        },
        after: function() {
            blue_private.state = 'LANDED'
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
        url: '/api/' + green_airliner.call_sign + '/intent/',
        aircraft: green_airliner,
        method: 'intent',
        data: {
            state: "APPROACH",
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
