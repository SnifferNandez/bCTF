$('document').ready(function() {
    update_events();
    setInterval(events, 15000); // Update scores every 15 seconds

})

function populate_events(){
    var scoresURL = "/api/events/";
    $.getJSON( scoresURL, function( data ) {
        $.each( data.events, function( key, val ) {
            feed_events(val);
        });
    });
}

function clean_events() {
    $('#events').empty();
}

function feed_events(element) {
    $('#events').append(
        `
        <li><span style="color:red">[${element.time}]</span> 
        -> <a href="/accounts/profile/${element.team_id}">${element.team}</a> ha resuelto 
        <a href="/challenges/#${element.challenge}">${element.challenge}</a>!
        </li>
        `
    )
}

function update_events() {
    clean_events();
    populate_events();
}


///////////////////////////////////////
///////////////////////////////////////
///////////////////////////////////////
///////////////////////////////////////
///////////////BSidesCo////////////////
///////////////////////////////////////
///////////////////////////////////////
///////////////////////////////////////
///////////////////////////////////////
///////////////////////////////////////
///////////////////////////////////////