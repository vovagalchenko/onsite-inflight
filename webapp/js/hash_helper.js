function date_to_hash(date)
{
    return '#' + date.getFullYear() + '-' + month_string_from_index(date.getMonth()) + '-' +  date_string_from_date(date.getDate());
}

function month_string_from_index(month_index)
{
    var int_string = (month_index + 1).toString(10);
    return ('00' + int_string).substr(-2);
}

function date_string_from_date(date)
{
    var date_string = date.toString(10);
    return ('00' + date_string).substr(-2);
}

function encode_hash_component(hash_component)
{
    return encodeURIComponent(hash_component).replace(/%20/g, "+");
}

function decode_hash_component(encoded_hash_component)
{
    return decodeURIComponent(encoded_hash_component.replace(/\+/g, "%20"));
}

function get_max_supported_date()
{
    var now = new Date();
    return now.setDate(now.getDate() + 7);
}

function go_to_hash(animate_date_switch)
{
    var new_hash = window.location.hash;
    if (!new_hash)
        new_hash = date_to_hash(new Date());
    var date_to_set = null;
    var candidate_name = null;
    new_hash = new_hash.replace(/^#/, '');
    var path_components = new_hash.split('/');
    var hash_is_invalid = false;
    if (path_components.length >= 1)
    {
        var date = path_components[0];
        var date_match = date.match(/(\d\d\d\d)-(\d\d)-(\d\d)/);
        if (date_match && date_match.length == 4)
        {
            date_to_set = new Date(date_match[1], date_match[2] - 1, date_match[3]);
            if (date_to_set < min_date || date_to_set > get_max_supported_date())
            {
                hash_is_invalid = true;
            }
        }
        else
        {
            hash_is_invalid = true;
        }

        if (path_components.length == 2 && path_components[1].length > 0)
        {
            candidate_name = decode_hash_component(path_components[1]);
        }
        else if (path_components.length > 2)
        {
            hash_is_invalid = true;
        }
    }

    if (hash_is_invalid)
    {
        location.hash = date_to_hash(new Date());
    }
    else
    {
        if (!date_to_set || !current_date || (date_to_set.getTime() != current_date.getTime()))
        {
            if (animate_date_switch && !candidate_name)
            {
                if ((current_date - date_to_set) > 0)
                    do_animate_decrement_date(date_to_set);
                else if ((date_to_set - current_date) > 0)
                    do_animate_increment_date(date_to_set);
            }
            else
            {
                set_date(date_to_set);
            }
        }
        if (candidate_name)
        {
            do_switch_to_candidate_detail_page(candidate_name);
        }
        else if (!is_current_page_candidate_list())
        {
            do_switch_to_candidate_list_page();
        }
    }
}
