var simulation_started = false;
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function sendIntent(action) {
  key = $("#public_key").val();

  const csrftoken = getCookie('csrftoken');

  $.ajax({
      url: "/api/"+action.aircraft.call_sign+"/intent/", 
      type: "post",
      data: {
          public_key: key,
          state: action.data.state,
      },
      headers: {
        'X-CSRFToken': csrftoken
      },
      dataType: 'json',
      success: function(data){
        console.log('success');
      },
      error: function(error) {
        console.log('error')
      }
  });
}

function sendLocation(action) {
  key = $("#public_key").val();

  const csrftoken = getCookie('csrftoken');

  $.ajax({
      url: "/api/"+action.aircraft.call_sign+"/location/", 
      type: "post",
      data: {
          public_key: key,
          type: action.data.type,
          longitude: action.data.longitude,
          latitude: action.data.latitude,
          altitude: action.data.altitude,
          heading: action.data.heading
      },
      headers: {
        'X-CSRFToken': csrftoken
      },
      dataType: 'json',
      success: function(data){
        console.log('success');
      },
      error: function(error) {
        console.log('error')
      }
  });
}

function newAircraftIntent(callSign, type, state, intent) {
  key = $("#public_key").val();

  const csrftoken = getCookie('csrftoken');

  $.ajax({
      url: "/api/"+callSign+"/intent/", 
      type: "post",
      data: {
          public_key: key,
          type: type,
          state: state,
          intent: intent
      },
      headers: {
        'X-CSRFToken': csrftoken
      },
      dataType: 'json',
      success: function(data){
        console.log(data);
      }
  });
}


var next_action = 1;



function executeStep(step) {
    // Let's first check one success workflow!
    action = actions[step];
    if (action.aircraft.known) {
        if (action.method === 'intent') {
            sendIntent(action)
        } else if (action.method === 'location') {
            sendLocation(action);
        }
        action.after();
    } else {
        if (action.method === 'intent') {
          newAircraftIntent(
              actions[step].aircraft.call_sign, 
              actions[step].data.type,
              actions[step].data.state,
              actions[step].data.intent
          );
        }
        action.after();
    }
}

function drawImage(ctx, aircraft, x, y) {

  var angle = 0;
  var tr_pos_x = -30;
  var tr_pos_y = 10;

  if (aircraft.state === 'TAKE_OFF' || aircraft.state === 'LANDED') {
    angle = -Math.PI/2;
  } else if (aircraft.state === 'AIRBORNE') {
    angle = -Math.PI;
    tr_pos_x = -75;
    tr_pos_y = 50;
  }
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  // ctx.font = "40px Arial";
  ctx.fillText("\u2708", 0, 0);
  ctx.restore();

  if (aircraft.loc) {
    ctx.font = "10px Arial";
    ctx.fillText("lon: " + aircraft.loc.longitude, x + tr_pos_x, y + tr_pos_y);
    ctx.fillText("lat: " + aircraft.loc.latitude, x + tr_pos_x, y + tr_pos_y + 15);
  }
}

function drawParkingLine(ctx, y) {
  ctx.beginPath();
  ctx.moveTo(400, y);
  ctx.lineTo(500, y);
  ctx.lineWidth = 1;

  ctx.strokeStyle = 'gray';
  ctx.stroke();
}

function draw_aircrafts() {
  var canvas = document.getElementById("canvas");
  var ctx = canvas.getContext("2d");
    
  // CLEAR CANVAS
    ctx.clearRect(0, 0, canvas.width, canvas.height);

  // DRAW RUNWAY
  var img = document.getElementById("runway_image");
  ctx.drawImage(img, 200, 200);

  // DRAW PARKING
  ctx.font = "15px Arial";
  ctx.fillStyle = "black";
  ctx.fillText("Small Parking", 380, 20);
  for (i=0; i < 6; i++) {
    drawParkingLine(ctx, 40 + i * 25);
  }

  // PARKED AIRCRAFTS
  ctx.font = "30px Arial";
  for (i = 0; i < 3; i++) {
    ctx.fillText("\u2708", 430, 63 + i * 25);

  }

  // DRAW RED AIRCRAFT
  if (red_airliner.known) {
      var x = 0;
      var y = 0;
      if (red_airliner.state==="TAKE_OFF" || red_airliner.state==="LANDED") {
          x = 250;
          y = 250;
      } else if (red_airliner.state=="AIRBORNE") {
          x = 210;
          y = 40;
      } else if (red_airliner.state==="APPROACH") {
          x = 50;
          y = 150;
      }
      ctx.font = "40px Arial";
      ctx.fillStyle = "red";
      // ctx.fillText("\u2708", x, y);
      drawImage(ctx, red_airliner, x, y);
  }

  // DRAW GREEN AIRCRAFT
  if (green_airliner.known) {
      var x = 0;
      var y = 0;
      if (green_airliner.state==="TAKE_OFF" || green_airliner.state==="LANDED") {
          x = 250;
          y = 250;
      } else if (green_airliner.state==="AIRBORNE") {
          x = 300;
          y = 40;
      } else if (green_airliner.state==="APPROACH") {
          x = 50;
          y = 150;
      }
      ctx.font = "40px Arial";
      ctx.fillStyle = "green";
      drawImage(ctx, green_airliner, x, y);
  }

  // DRAW BLUE AIRCRAFT
  if (blue_private.known) {
      var x = 20;
      var y = 20;
      if (blue_private.state==="TAKE_OFF" || blue_private.state === "LANDED") {
          x = 250;
          y = 250;
      } else if (blue_private.state==="AIRBORNE") {
          x = 220;
          y = 60;
      } else if (blue_private.state==="APPROACH") {
          x = 50;
          y = 150;
      }
      ctx.fillStyle = "blue";
      ctx.font = "40px Arial";
      drawImage(ctx, blue_private, x, y);
  }

  // DRAW CYAN
  ctx.fillStyle = "cyan";
  ctx.font = "30px Arial";
  drawImage(ctx, cyan_private, 430, 138);
  
}

function refresh_screen() {
  if (simulation_started) {
    $('#public_key').prop('disabled', true);
    $('#start_simulation').prop('disabled', true);
    $('#next_step_btn').prop('disabled', false);
  } else {
    $('#public_key').prop('disabled', false);
    $('#start_simulation').prop('disabled', false);
    $('#next_step_btn').prop('disabled', true);
  }

  if (next_action >= 0) {
      $('#actions_table tr td').parents('tr').remove();
      $('#next_description').val(actions[next_action].description);
      $('#next_url').val(actions[next_action].url);
      $('#next_data').val(JSON.stringify(actions[next_action].data, null, 2));
  } else {
      $('#next_description').val("");
      $('#next_url').val("");
      $('#next_data').val("");
  }

  draw_aircrafts();
}

$("#start_simulation" ).click(function() {

  key = $("#public_key").val();
  const csrftoken = getCookie('csrftoken');

  red_airliner.state = 'PARKED';
  red_airliner.known = false;
  delete red_airliner.loc;

  green_airliner.state = 'PARKED';
  green_airliner.known = false;
  delete green_airliner.loc;

  blue_private.state = 'AIRBORNE';
  blue_private.known = false;
  delete blue_private.loc;

  $.ajax({
      url: "/api/simulation/start/", 
      type: "post",
      data: {
          public_key: key,
      },
      headers: {
        'X-CSRFToken': csrftoken
      },
      success: function(data){
          simulation_started = true;
          next_action = 0;  

          refresh_screen();
      },
      error: function(error) {
          alert("Couldn't start simulation! Check public key!")
          simulation_started = false;
          next_action = -1;

          refresh_screen();

      }
  });

});

$("#next_step_btn" ).click(function() {
  executeStep(next_action);
  next_action = next_action + 1;  

  if (actions[next_action].description === "SIMULATION FINISHED") {
      simulation_started = false;
  }

  refresh_screen();
});


$(document).ready(function(){
  document.getElementById("runway_image").style.visibility = "hidden";
});
