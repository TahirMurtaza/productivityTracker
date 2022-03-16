function getUserData(id) {
    $('#formeditUser').attr('action', '/edituser/' + id);
    $.ajax({
        url: "/edituser/" + id,
        success: function(res) {
            $('input[name="username"]').val(res.username);
            $('input[name="email"]').val(res.email);
            $('input[name="phone"]').val(res.phone);
        }
    });
}

function getTackerData(id) {
    $('#options').hide();
    // if id != 0 then edit tracker
    if (id != 0) {
        // change form action route
        $('#Tracker').attr('action', '/edittracker/' + id);
        // change form title
        $('#tracker_title').html('Edit Tracker');
        // change button value
        $('#tracker_btn').html('Update');
        $.ajax({
            url: "/edittracker/" + id,
            success: function(res) {
                console.log(res)

                // show options only if multiple_choices selected
                if (res.tracker_value == 'Multiple_choices') {
                    $('#options').show();
                    $('input[name="options"]').val(res.options);
                }

                $('input[name="name"]').val(res.name);
                $('textarea[name="description"]').val(res.description);
                $('select[name="tracker_type"]').val(res.tracker_type);

            }
        });

    } else {
        console.log("add tracker")

        // Add tracker if id = 0

        // change form action route
        $('#Tracker').attr('action', '/addtracker');
        // reset form
        $('#Tracker').find("input[type=text], textarea").val("");

        // change form title
        $('#tracker_title').html('Add Tracker');
        // change button value
        $('#tracker_btn').html('Add');
    }

}

function getTackerLogsData(id) {

    // if id != 0 then edit tracker
    if (id != 0) {
        // change form action route
        $('#TrackerLogs').attr('action', '/edittrackerlog/' + id);
        // change form title
        $('#trackerlogs_title').html('Edit Tracker Log');
        // change button value
        $('#trackerlogs_btn').html('Update');
        $.ajax({
            url: "/edittrackerlog/" + id,
            success: function(res) {

                if (res.tracker_value == 2) {
                    $('#mcq_select').val(res.value);
                } else {

                    $('input[name="value"]').val(res.value);
                }
                $('textarea[name="notes"]').val(res.notes);
                $('select[name="tracker_id"]').val(res.tracker_id);
            }
        });

    } else {
        console.log("add tracker")

        // Add tracker if id = 0

        // change form action route
        $('#TrackerLogs').attr('action', '/addtrackerlog');
        // reset form
        $('#TrackerLogs').find("input[type=text], textarea").val("");

        // change form title
        $('#trackerlogs_title').html('Add Tracker Log');
        // change button value
        $('#trackerlogs_btn').html('Add');

    }

}

// onchange tracker values in tracker modal
function selectTracker(tracker) {
    if (tracker.value == "Multiple_choices") {
        $('#options').show();
    } else {
        $('#options').hide();
    }
}



$(function() {
    $(".alert").fadeOut(5000);
});