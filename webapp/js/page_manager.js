function rename_all_descendants(root_node, postfix)
{   
    root_node.setAttribute('id', root_node.id + postfix);
    var children = root_node.children;
    for (var i = 0; i < children.length; i++)
    {   
        rename_all_descendants(children[i], postfix);
    }   
}

var old_current_page = null;

function present_page_modally(page_to_present, animation_will_start_callback)
{
    page_to_present.setAttribute('class', 'page pre_modal');
    old_current_page = get_current_page();
    old_current_page.setAttribute('class', 'page');

    setTimeout(function ()
    {
        page_to_present.setAttribute('class', 'page transition current');
        animation_will_start_callback();
    }, 100);
}

function dismiss_modal_page()
{
    if (!old_current_page)
    {
        console.log('Attempting to dismiss a modal page, when there seems to be no page underneath the current one.');
        return;
    }
    var page_to_dismiss = get_current_page();
    page_to_dismiss.setAttribute('class', 'page transition pre_modal');
    old_current_page.setAttribute('class', 'page transition current');
}

function flip_pages(page_to_flip, direction, animation_will_start_callback)
{
    var page_to_flip_new = page_to_flip.cloneNode(true);
    rename_all_descendants(page_to_flip, '_out');
    var new_page_initial_position = null;
    var old_page_final_position = null;
    if (direction == 'from_right')
    {
        new_page_initial_position = 'next';
        old_page_final_position = 'previous';
    }
    else if (direction == 'from_left')
    {
        new_page_initial_position = 'previous';
        old_page_final_position = 'next';
    }
    page_to_flip_new.setAttribute('class', 'page ' + new_page_initial_position);
    page_to_flip.parentElement.appendChild(page_to_flip_new);

    var transition_finished_events = [
        'transitionend',
        'webkitTransitionEnd',
        'msTransitionEnd',
        'oTransitionEnd'
    ];
    var page_flip_end_handler = function()
    {
        this.parentElement.removeChild(this);
        for (var i = 0; i < transition_finished_events.length; i++)
        {
            this.removeEventListener(transition_finished_events[i], page_flip_end_handler);
        }
    };
    for (var i = 0; i < transition_finished_events.length; i++)
    {
        page_to_flip.addEventListener(transition_finished_events[i], page_flip_end_handler);
    }

    setTimeout(function()
    {
        page_to_flip.setAttribute('class', 'page transition ' + old_page_final_position);
        page_to_flip_new.setAttribute('class', 'page transition current');
        animation_will_start_callback();
    }, 100);
}

function get_current_page()
{
    var current_page = document.getElementsByClassName('page current');
    if (!current_page || current_page.length != 1)
    {
        // There should be exactly one current_page at any given time.
        return null;
    }
    return current_page[0];
}

function is_current_page_candidate_list()
{
    return does_current_page_have_id_prefix('candidate_list_page');
}

function is_current_page_candidate_detail()
{
    return does_current_page_have_id_prefix('candidate_detail_page');
}

function does_current_page_have_id_prefix(id_prefix)
{
    var current_page = get_current_page();
    return current_page != null && current_page.id.indexOf(id_prefix) === 0;
}
