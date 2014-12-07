var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
var days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
var current_date = null;
var expanded_interviews = {};
var candidates = null;
var roundup_date = null;
var dragging_cell = null;
var placeholder_cell = null;
var start_drag_cell_y = null;
var start_drag_y = null;
var num_outstanding_requests = 0;
state_enum = {
    CANDIDATE_SELECT : 0,
    ROUNDUP_SCHEDULE : 1,
    SCHEDULING : 2,
    DONE: 3
};
var current_state = state_enum.CANDIDATE_SELECT;

window.onload = function()
{
    var date = new Date();
//    date.setDate(date.getDate() - 1);
    make_ajax_request("/api/candidate_list?date=" + Math.floor(date.getTime()/1000), update_candidate_list_ui, handle_ajax_error);
    set_date(get_roundup_date());
}

window.onmousemove = handle_drag;
window.ontouchmove = handle_drag;

function handle_drag()
{
    if (!dragging_cell)
        return;
    event.preventDefault();
    var mouse_move_delta = mouseY(event) - start_drag_y;
    var delta = start_drag_cell_y + mouse_move_delta;
    dragging_cell.style.top = delta + "px";
    var cell_to_move = null;
    if (mouse_move_delta >= dragging_cell.clientHeight && (cell_to_move = next_visible_cell(dragging_cell)))
    {
        dragging_cell.parentNode.removeChild(cell_to_move);
        dragging_cell.parentNode.insertBefore(cell_to_move, placeholder_cell);
        start_drag_cell_y += dragging_cell.clientHeight;
        start_drag_y += dragging_cell.clientHeight;
        calculate_and_refresh_roundup_times();
    }
    else if (mouse_move_delta <= -dragging_cell.clientHeight && (cell_to_move = previous_visible_cell(placeholder_cell)))
    {
        dragging_cell.parentNode.removeChild(cell_to_move);
        dragging_cell.parentNode.insertBefore(cell_to_move, dragging_cell.nextSibling);
        start_drag_cell_y -= dragging_cell.clientHeight;
        start_drag_y -= dragging_cell.clientHeight;
        calculate_and_refresh_roundup_times();
    }
}

window.onmouseup = stop_dragging;
window.ontouchend = stop_dragging;

function next_visible_cell(cell)
{
    do
    {
        cell = cell.nextSibling;
    }
    while (cell && (!has_class(cell, "tableview-cell") || has_class(cell, "collapsed")));
    return cell;
}

function previous_visible_cell(cell)
{
    do
    {
        cell = cell.previousSibling;
    }
    while (cell && (!has_class(cell, "tableview-cell") || has_class(cell, "collapsed")));
    return cell;
}

function build_content_from_template(script_id, data, target_container_id)
{   
    var templateSource = document.getElementById(script_id);
    var template= Handlebars.compile(templateSource.innerHTML);
    var built_html = template(data);
    var final_html = built_html + templateSource.outerHTML;
    document.getElementById(target_container_id).innerHTML = final_html;
}

function start_dragging()
{
    if (current_state != state_enum.ROUNDUP_SCHEDULE || placeholder_cell != null)
    {
        return;
    }
    dragging_cell = get_clicked_tableviewcell(event);
    set_up_dragging_cell(dragging_cell);
    placeholder_cell = document.createElement('DIV');
    placeholder_cell.className = "tableview-cell";
    placeholder_cell.style.backgroundColor = "rgba(0, 0, 0, 0)";
    placeholder_cell.style.bottomBorder = "1px";
    placeholder_cell.id = "placeholder";
    dragging_cell.parentNode.insertBefore(placeholder_cell, dragging_cell);
    start_drag_y = mouseY(event);
}

function get_supported_property(property_array)
{
    var root = document.documentElement;
    for (var i = 0; i < property_array.length; i++)
    {
        if (property_array[i] in root.style)
        {
            return property_array[i];
        }
    }
}

function set_up_dragging_cell(cell)
{
    cell.className = cell.className.replace("transition", "");
    cell.style.position = "absolute";
    var cells = cell.parentNode.children;
    var num_visible_cells_above = 0;
    for (var indexOfCell = 0; indexOfCell < cells.length; indexOfCell++)
    {
        if (cells[indexOfCell] == cell)
            break;
        else if (!has_class(cells[indexOfCell], "collapsed"))
        {
            num_visible_cells_above++;
        }
    }
    start_drag_cell_y = num_visible_cells_above* cell.clientHeight;
    cell.style.top = (start_drag_cell_y - 1) +  "px";
    cell.style.zIndex = 1;
    var box_shadow_prop = get_supported_property(['boxShadow', 'MozBoxShadow', 'WebkitBoxShadow']);
    cell.style[box_shadow_prop] = "0 8px 6px -6px #AAAAAA";
}

function stop_dragging()
{
    if (current_state != state_enum.ROUNDUP_SCHEDULE || dragging_cell == null)
    {
        return;
    }
    tear_down_dragging_cell(dragging_cell);
    dragging_cell = null;
    start_dragging_y = null;
}

function tear_down_dragging_cell(cell)
{
    events = [
        'transitionend',
        'webkitTransitionEnd',
        'mozTransitionEnd',
        'oTransitionEnd'
    ];
    var animation_end_callback = function()
    {
        for (var i = 0; i < events.length; i++)
        {
            cell.removeEventListener(events[i], animation_end_callback, false);
        }
        cell.className = cell.className.replace("transition", "");
        placeholder_cell.parentNode.removeChild(placeholder_cell);
        placeholder_cell = null;
        cell.style.top = "0px";
        cell.style.position = "relative";
        var box_shadow_prop = get_supported_property(['boxShadow', 'MozBoxShadow', 'WebkitBoxShadow']);
        cell.style[box_shadow_prop] = "0px";
        cell.style.zIndex = 0;
    }
    for (var i = 0; i < events.length; i++)
    {
        cell.addEventListener(events[i], animation_end_callback, false);
    }
    cell.className += " transition";
    cell.style.top = start_drag_cell_y + "px";
}

function get_clicked_tableviewcell(event)
{
    var clickedElement = event.toElement || event.target;
    var tableviewcell = clickedElement;
    while (!has_class(tableviewcell, "tableview-cell") && tableviewcell.parentNode)
    {
        tableviewcell = tableviewcell.parentNode;
    }
    return tableviewcell;
}

function toggle_checkmark()
{
    if (current_state == state_enum.CANDIDATE_SELECT)
    {
        var tableviewcell = get_clicked_tableviewcell(event);
        var checkbox = tableviewcell.getElementsByClassName("checkbox")[0];
        if (checkbox.innerHTML.length == 0)
            checkbox.innerHTML = "&#x2713;";
        else
            checkbox.innerHTML = "";
    }
}

function set_date(new_date)
{
    if (!new_date)
    {
        new_date = new Date();
        // Round to the nearest second
        new_date = new Date(Math.floor(new_date.getTime()/1000) * 1000);
    }
    document.getElementById('date').innerHTML = days[new_date.getDay()] + ", " + months[new_date.getMonth()] + " " + new_date.getDate();
}

function check_authn(data)
{
    if (data["error"] == "authn_needed")
    {
        var authn_form = document.getElementById("authn_form");
        document.getElementById('saml_response_input').value = data["authn_request"];
        document.getElementById('saml_relay_state_input').value = (window.location.hash == null || window.location.hash.length == 0)? "dashboard" : window.location.hash;
        authn_form.submit();
        return true;
    }
    return false;
}

function update_candidate_list_ui(data)
{
    if (typeof data == 'string')
    {
        data = JSON.parse(data);
    }

    candidates = data["candidates"];
    Handlebars.registerHelper('list', function(candidates, options)
    {
        var out = "";
        var candidateHTML;
        for (var i = 0, length = candidates.length; i < length; i++)
        {
            candidate_dict = candidates[i];
            candidate_dict["candidate_index"] = i;
            candidateHTML = options.fn(candidate_dict);
            out = out + candidateHTML;
        }
        return out;
    });
    build_content_from_template('candidates_handlebars', data, 'candidate_list_tableview');
}

function get_roundup_date()
{
    if (!roundup_date)
    {
        var now = new Date();
        var num_days_to_add = 1;
        switch (now.getDay()) {
            case 5: // Friday - shoot for Monday
                num_days_to_add = 3;
                break;
            case 6: // Saturday - shoot for Monday
            case 1: // Monday - shoot for Wednesday
                num_days_to_add = 2;
                break;
        }
        roundup_date = now;
        roundup_date.setDate(now.getDate() + num_days_to_add);
    }
    roundup_date.setHours(10);
    roundup_date.setMinutes(30);
    return roundup_date;
}

function handle_major_button_clicked()
{
    if (current_state == state_enum.CANDIDATE_SELECT)
    {
        var tableviewcells = document.getElementById("candidate_list_tableview").getElementsByClassName("tableview-cell");
        var num_selected = 0;
        for (var i = 0; i < tableviewcells.length; i++)
        {
            var checkbox = tableviewcells[i].getElementsByClassName("checkbox")[0];
            checkbox.className = checkbox.className.replace("checkbox", "timebox");
            if (checkbox.innerHTML.length == 0)
            {
                tableviewcells[i].className += " collapsed";
            }
            else
            {
                num_selected++;
            }
            checkbox.innerHTML = "";
        }
        calculate_and_refresh_roundup_times();
        current_state = state_enum.ROUNDUP_SCHEDULE;
    }
    else if (current_state == state_enum.ROUNDUP_SCHEDULE)
    {
        
        var roundup_data = calculate_and_refresh_roundup_times();
        num_outstanding_requests = roundup_data.length;
        for (var i = 0; i < roundup_data.length; i++)
        {
            make_ajax_request("/api/schedule_roundup?candidate_name=" + encodeURIComponent(roundup_data[i].candidate_name) + "&start_date=" + roundup_data[i].start_date + "&length=" + roundup_data[i].length, handle_roundup_schedule_response, handle_ajax_error);
        }
        current_state = state_enum.SCHEDULING;
    }
    refresh_major_button();
}

function handle_roundup_schedule_response(data)
{
    if (data.status == "success")
    {
        num_outstanding_requests--;
        if (num_outstanding_requests == 0)
        {
            current_state = state_enum.DONE;
        }
    }
    else
    {
        num_outstanding_requests--;
        handle_ajax_error(JSON.stringify(data));
    }
    refresh_major_button();
}

function refresh_major_button()
{
    var button_text = "";
    if (current_state == state_enum.ROUNDUP_SCHEDULE)
    {
        button_text = "Schedule Roundups";
    }
    else if (current_state == state_enum.CANDIDATE_SELECT)
    {
        button_text = "Select Candidates";
    }
    else if (current_state == state_enum.SCHEDULING)
    {
        button_text = "Scheduling...";
    }
    else if (current_state == state_enum.DONE)
    {
        button_text = "Done";
    }
    var button_element = document.getElementsByClassName("major-button")[0];
    button_element.innerHTML = button_text;
}

function calculate_and_refresh_roundup_times()
{
    var tableviewcells = document.getElementById("candidate_list_tableview").getElementsByClassName("tableview-cell");
    var num_visible = 0;
    for (var i = 0; i < tableviewcells.length; i++)
    {
        if (!has_class(tableviewcells[i], "collapsed") && tableviewcells[i].id != "placeholder")
        {
            num_visible++;
        }
    }
    var roundup_start = get_roundup_date();
    var roundup_length = Math.min(15, 60/num_visible);
    var roundups = [];
    for (var i = 0; i < tableviewcells.length; i++)
    {
        if (!has_class(tableviewcells[i], "collapsed") && tableviewcells[i].id != "placeholder")
        {
            var timebox = tableviewcells[i].getElementsByClassName("timebox")[0];
            timebox.innerHTML = pad(roundup_start.getHours(), 2) + ":" + pad(roundup_start.getMinutes(), 2);
            roundups.push({
                'candidate_name' : candidates[tableviewcells[i].id].candidate_name,
                'start_date' : Math.floor(roundup_start.getTime()/1000),
                'length' : Math.floor(roundup_length)
            });
            roundup_start.setMinutes(roundup_start.getMinutes() + roundup_length);
        }
    }
    return roundups;
}

function handle_ajax_error(error_string)
{
    alert(error_string);
}

function has_class(element, cls)
{
    return (' ' + element.className + ' ').indexOf(' ' + cls + ' ') > -1; 
}

function mouseY(e)
{
    if (e.pageY)
    {
        return e.pageY;
    }
    if (e.clientY)
    {
        return e.clientY + (document.documentElement.scrollTop ?
        document.documentElement.scrollTop :
        document.body.scrollTop);
    }
    return null;
}

function pad(num, size)
{
    var s = num+"";
    while (s.length < size) s = "0" + s;
    return s;
}
