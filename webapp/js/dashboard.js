var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
var days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
var focused_candidate_name;
var last_avatar_refresh_ts;
var min_date = new Date(1370502000000); // June 6th, 2013
var current_date = null;
var expanded_interviews = {};

window.onload = function()
{
    go_to_hash(false);
    setInterval(function()
	{
        synchronize_with_server(false);
	}, 10000);
    window.history.replaceState(date_to_hash(current_date), '');
}

window.onhashchange = function()
{
    go_to_hash(true);
}

function has_class(element, cls)
{
    return (' ' + element.className + ' ').indexOf(' ' + cls + ' ') > -1;
}

function build_content_from_template(script_id, data, target_container_id)
{   
    var templateSource = document.getElementById(script_id);
    var template= Handlebars.compile(templateSource.innerHTML);
    var built_html = template(data);
    var final_html = built_html + templateSource.outerHTML;
    document.getElementById(target_container_id).innerHTML = final_html;
}

function handle_interview_session_size_change(tableviewcell_element, expand, interview_id)
{
    var content_element = tableviewcell_element.children[0];
    var content_height = content_element.clientHeight;

    setTimeout(function()
    {
        tableviewcell_element.style.height = ((expand)? content_height + "px": getComputedStyle(tableviewcell_element)['minHeight']);
        if (expand)
        {
            expanded_interviews[interview_id] = tableviewcell_element.style.height;
        }
    }, 10);
}

function handle_interview_click(tableviewcell_element, interview_id)
{
    var needs_expand = false;
    if (expanded_interviews[interview_id] == null)
    {
        needs_expand = true;
    }
    else
    {
        tableviewcell_element.className = tableviewcell_element.className.replace(/\s*?expanded/g, "");
        delete expanded_interviews[interview_id];
    }
    handle_interview_session_size_change(tableviewcell_element, needs_expand, interview_id);
}

function score_string(score_float)
{
    if (typeof score_float !== 'number')
        return score_float
    else if (score_float == -1)
        return '-';
    var score_int = Math.round(score_float);
    var modifier_string = '';
    if ((score_float - score_int) > 0)
    {
        modifier_string = '+';
    }
    else if ((score_float - score_int) < 0)
    {
        modifier_string = '-';
    }
    return '' + score_int + modifier_string;
}
    
function button_is_active(button_class)
{
    return (button_class.indexOf("inactive_button") === -1 &&
            button_class.indexOf("active_button") !== -1);
}

function rename_all_descendants(root_node, postfix)
{
    root_node.setAttribute('id', root_node.id + postfix);
    var children = root_node.children;
    for (var i = 0; i < children.length; i++)
    {
        rename_all_descendants(children[i], postfix);
    }
}

function do_animate_increment_date(new_date)
{
    flip_pages(document.getElementById('candidate_list_page'), 'from_right', function ()
    {
        set_date(new_date);
    });
}

function increment_date(clicked_button_class)
{
    if (button_is_active(clicked_button_class))
    {
        location.hash = date_to_hash(new Date(current_date.getFullYear(), current_date.getMonth(), current_date.getDate() + 1));
    }
}

function do_animate_decrement_date(new_date)
{
    flip_pages(document.getElementById('candidate_list_page'), 'from_left', function ()
    {
        set_date(new_date);
    });
}

function decrement_date(clicked_button_class)
{
    if (button_is_active(clicked_button_class))
    {
        location.hash = date_to_hash(new Date(current_date.getFullYear(), current_date.getMonth(), current_date.getDate() - 1));
    }
}

function get_date_button_class(inactive_condition)
{
    var result_class = 'non_selectable ';
    if (inactive_condition)
    {
        result_class += 'inactive_button';
    }
    else
    {
        result_class += 'active_button';
    }
    return result_class;
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
    var tableview = document.getElementById('candidate_list_tableview');
    tableview.innerHTML = document.getElementById('candidates_handlebars').outerHTML;
    current_date = new_date;
    var day_after = new Date(new_date.getFullYear(), new_date.getMonth(), new_date.getDate() + 1);
    document.getElementById('date_ff').className = get_date_button_class(day_after > get_max_supported_date());

    var day_before = new Date(new_date.getFullYear(), new_date.getMonth(), new_date.getDate() - 1);
    document.getElementById('date_rw').className = get_date_button_class(day_before < min_date);
    synchronize_with_server(false);
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
    var result_date = new Date(data['date']*1000);
    if (result_date.getTime() != current_date.getTime())
    {
        // This result is for the wrong date
        return;
    }

    Handlebars.registerHelper('list', function(candidates, options)
    {
        var out = "";
        var candidateHTML;
        for (var i = 0, length = candidates.length; i < length; i++)
        {
            candidate_dict = candidates[i];
            if (candidate_dict["status"] == "failure")
            {
                candidate_dict["status_symbol"] = new Handlebars.SafeString("&#9785;"); // Sad Face
            }
            else
            {
                candidate_dict["status_symbol"] = new Handlebars.SafeString("&#9786;"); // Happy Face
            }
            candidateHTML = options.fn(candidate_dict);
            out = out + candidateHTML;
        }
        return out;
    });
    build_content_from_template('candidates_handlebars', data, 'candidate_list_tableview');
}

function get_interview_progress(interview)
{
    var now = new Date().getTime();
    var start_time = new Date(interview['start_time']).getTime();
    var end_time = new Date(interview['end_time']).getTime();
    var result = (now - start_time)/(end_time - start_time);
    return Math.max(0, Math.min(1, result));
}
        
function get_time_string_for_date(date)
{
    var hours = date.getHours();
    var am_or_pm = "AM";
    if (hours > 12)
    {
        hours -= 12;
        am_or_pm = "PM";
    }
    var minutes = date.getMinutes();
    if (minutes < 10)
    {
        minutes = "0" + minutes.toString();
    }
    return hours.toString() + ":" + minutes.toString() + am_or_pm;
}

function number_to_adj(number)
{
    var adj = "";
    switch (number)
    {
        case "1":
            adj = "1st";
            break;
        case "2":
            adj = "2nd";
            break;
        case "3":
            adj = "3rd";
            break;
        default:
            adj = "";
            break;
    }
    return adj;
}

function get_room_string_for_code(room_code)
{
    var match = room_code.match(/^([123])- (.*)$/, room_code);
    var room_string = "";
    if (match && match.length >= 3)
    {
        room_string = "<strong>" + match[2] + "</strong> (" + number_to_adj(match[1]) + " floor)";
    }
    else
    {
        room_string = room_code;
    }
    return new Handlebars.SafeString(room_string);
}

function update_candidate_detail_ui(data)
{
    if (typeof data == 'string')
    {
        data = JSON.parse(data);
    }
    if (focused_candidate_name != data['candidate_name'])
    {
        // this data is for the wrong candidate
        return;
    }

    if (!data['interviews'] || data['interviews'].length == 0)
    {
        // Nothing to display for this homie.
        switch_to_candidate_list_page();
        return;
    }
    for (var i = 0; i < data['interviews'].length; i++)
    {
        interview = data['interviews'][i];
        var use_avatar = interview['interviewer']['avatar_url'] != null;
        interview['interviewer']['use_avatar'] = use_avatar;
        if (use_avatar)
        {
            data['interviews'][i]['interviewer']['avatar_url'] += '?ts=' + last_avatar_refresh_ts;
        }
    }
    var now = new Date();
    var interviews_array = data['interviews'];
    data['status'] = 'In Progress';
    if (now < new Date(interviews_array[0]['start_time']))
    {
        data['status'] = 'Starting Soon';
    }
    else if (now > new Date(interviews_array[interviews_array.length - 1]['end_time']))
    {
        data['status'] = 'Finished';
    }
    build_content_from_template('candidate_info_handlebars', data, 'candidate_info');
    Handlebars.registerHelper('list', function(interviews, options)
    {
        var out = "";
        for (var i = 0, length = interviews.length; i < length; i++)
        {
            interview = interviews[i];

            if (expanded_interviews[interview.id])
            {
                interview['cell_height'] = expanded_interviews[interview.id];
            }
            var interview_progress = get_interview_progress(interview);
            if (interview_progress != 1 && interview_progress != 0)
            {
                interview['progress'] = (interview_progress*100).toString() + "%";
            }
            interview['start_time'] = get_time_string_for_date(new Date(interview['start_time']));
            interview['end_time'] = get_time_string_for_date(new Date(interview['end_time']));
            interview['room'] = get_room_string_for_code(interview['room']);
        
            // Abbreviate last names.
            interviewer_name = interview['interviewer']['name'];
            interview['interviewer']['name'] = interviewer_name.replace(/ ([A-Z])\S*$/, " $1.");
            interview['interviewer']['initials'] = (interviewer_name.charAt(0) + interviewer_name.split(/\s/).pop().charAt(0)).toUpperCase();

            if (!interview['cultural_score'])
            {
                interview['cultural_score'] = '';
            }
            else if (interview['cultural_score'] >= 0 && interview['cultural_score'] <= 2)
            {
                interview['cult_failure'] = true;
            }

            if (interview['is_coffee_break'])
            {
                interview['technical_score'] = 'N/A';
            }
            else if (!interview['technical_score'])
            {
                interview['technical_score'] = '';
            }
            else if (interview['technical_score'] >= 0 && interview['technical_score'] <= 2) 
            {
                interview['tech_failure'] = true;
            }
            interview['technical_score'] = score_string(interview['technical_score']);
            interview['cultural_score'] = score_string(interview['cultural_score']);
            out = out + options.fn(interview);
        }
        return out;
    });
    build_content_from_template('interviews_handlebars', data, 'interviews_list_tableview');
}

function update_candidate_detail_ui_initially(data)
{
    last_avatar_refresh_ts = new Date().getTime();
    update_candidate_detail_ui(data);
}

function handle_ajax_error(error_string)
{
    alert(error_string);
}

function switch_to_candidate_list_page()
{
    location.hash = date_to_hash(current_date);
}

function do_switch_to_candidate_list_page()
{
    focused_candidate_name = null;
    dismiss_modal_page();
    synchronize_with_server(false);
}

function switch_to_candidate_detail_page(candidate_name)
{
    location.hash = date_to_hash(current_date) + '/' + encode_hash_component(candidate_name);
}

function do_switch_to_candidate_detail_page(candidate_name)
{
    focused_candidate_name = candidate_name;
    build_content_from_template('candidate_info_handlebars', {'candidate_name' : focused_candidate_name}, 'candidate_info');
    // Remove all of the stale information from last time we looked at the detail page.
    var handlebars = document.getElementById('interviews_handlebars');
    var interview_list_tableview = document.getElementById('interviews_list_tableview');
    interview_list_tableview.innerHTML = '';
    interview_list_tableview.appendChild(handlebars);
    var transition_finished_callback = function()
    {
        synchronize_with_server(true);
    }
    if (is_current_page_candidate_detail())
    {
        transition_finished_callback();
    }
    else
    {
        present_page_modally(document.getElementById('candidate_detail_page'), transition_finished_callback);
    }
}

function synchronize_with_server(initial)
{
    if (is_current_page_candidate_list())
    {
	                make_ajax_request("/api/candidate_list?date=" + Math.floor(current_date.getTime()/1000), update_candidate_list_ui, handle_ajax_error);
    }
    else if(focused_candidate_name != null)
    {
        ui_update_callback = (initial)? update_candidate_detail_ui_initially: update_candidate_detail_ui;
        make_ajax_request("/api/candidate_detail?candidate_name=" + encodeURIComponent(focused_candidate_name) + "&date=" + Math.floor(current_date.getTime()/1000), ui_update_callback, handle_ajax_error);
    }
}

