var max_values = [];

function on_load()
{
    make_ajax_request("/api/reimbursements", initialize_ui, handle_ajax_error);
}

function build_content_from_template(script_id, data, target_container_id)
{   
    var templateSource = document.getElementById(script_id);
    var template= Handlebars.compile(templateSource.innerHTML);
    var built_html = template(data);
    var final_html = built_html + templateSource.outerHTML;
    document.getElementById(target_container_id).innerHTML = final_html;
}

function initialize_ui(data)
{
    if (typeof data == 'string')
    {
        data = JSON.parse(data);
    }
    Handlebars.registerHelper('list', function(reimbursements, options)
    {
        var out = "";
        var reimbursementHTML;
        for (var i = 0; i < reimbursements.length; i++)
        {
            reimbursement = reimbursements[i];
            reimbursement.value = data.employee[reimbursement.id]/100;
            if (reimbursement.value === 0)
            {
                reimbursement.value = "";
            }
            max_values[reimbursement.id] = reimbursement.max_amount/100;
            reimbursementHTML = options.fn(reimbursement);
            out = out + reimbursementHTML;
        }
        return out;
    });
    build_content_from_template("handlebars-template", data, "expenses-form");

    var fields = document.getElementsByClassName("field");
    for (var i = 0; i < fields.length; i++)
    {
        fields[i].addEventListener("mouseout", field_mouseout, true);
    }

    var inputs = document.getElementsByTagName("input");
    for (var i = 0; i < fields.length; i++)
    {
        inputs[i].addEventListener("keydown", process_input_modify, true);
        inputs[i].addEventListener("keyup", refresh_total_reimbursement, true);
    }
    refresh_total_reimbursement();
}

function handle_ajax_error(error_string)
{
    alert(error_string);
}

function refresh_total_reimbursement()
{
    var inputs = document.getElementsByTagName("input");
    var total = 0;
    for (var i = 0; i < inputs.length; i++)
    {
        to_add = parseFloat(inputs[i].value);
        if (!isNaN(to_add))
        {
            total += to_add;
        }
    }
    document.getElementById("total-reimbursement").innerHTML = "$" + total.toFixed(2);
}

function save(save_button)
{
    add_class(save_button, "disabled");
    redraw(save_button);
    var inputs = document.getElementsByTagName("input");
    query_string = "";
    for (var i = 0; i < inputs.length; i++)
    {
        input_num = parseFloat(inputs[i].value);
        if (isNaN(input_num))
        {
            input_num = 0;
        }
        query_string += inputs[i].id + "=" + parseInt(input_num)*100;
        if (i < inputs.length-1)
        {
            query_string += "&";
        }
    }
    make_ajax_request("/api/update?" + query_string, save_finished, handle_ajax_error);
}

function redraw(node_to_redraw)
{
    var prev_display = node_to_redraw.style.display;
    node_to_redraw.style.display = "none";
    node_to_redraw.offsetHeight;
    node_to_redraw.style.display = prev_display;
}

function save_finished(data)
{
    remove_class(document.getElementById("save-button"), "disabled");
    if (data.error)
    {
        alert(data.error);
    }
    else
    {
        alert("Thanks");
    }
}

function process_input_modify(event)
{
    var keycode = event.keyCode;
    if (event.shiftKey)
    {
        event.preventDefault();
        return;
    }
    if (keycode == 8 || keycode == 9) // backspace and tab are always allowed
        return;
    // Don't accept input that isn't
    if ((keycode > 57 || keycode < 48)  // a number
        && keycode != 190)              // a period
    {
        event.preventDefault();
        return;
    }
    
    var input_so_far = event.srcElement.value;
    var input_type = event.srcElement.id;
    var value_to_be = input_so_far + String.fromCharCode(keycode);
    // Make sure the number
    if(input_so_far.match(/\./g) && keycode === 190 ||                              // is valid
       input_so_far.length == 0 && keycode === 48 ||                                // doesn't have leading zeros
       parseFloat(value_to_be) > max_values[input_type] ||                          // is less than the allowed maximum
       (value_to_be.indexOf(".") !== -1 && value_to_be.split(".")[1].length > 2))   // doesn't have precision greater than 2

    {
        event.preventDefault();
        return;
    }
    
}

function field_mouseover(node)
{
    var to_fade_out = node.parentNode.getElementsByClassName("field-value");
    for (var i = 0; i < to_fade_out.length; i++)
    {
        remove_class(to_fade_out[i], "fade-in");
        add_class(to_fade_out[i],  "fade-out");
    }
    remove_class(node.parentNode, "no-overlay");
    add_class(node.parentNode, "info-overlay");

    var to_fade_in = node.parentNode.getElementsByClassName("detail");
    for (var i = 0; i < to_fade_in.length; i++)
    {
        remove_class(to_fade_in[i], "fade-out");
        add_class(to_fade_in[i], "fade-in");
    }
}

function field_mouseout(event)
{
    var node  = event.toElement || event.relatedTarget;
    if (node == null || node.parentNode == this || node == this)
        return;
    node = event.fromElement;
    if (!has_class(node, "field"))
    {
        node = node.parentNode;
    }
    var value_nodes = node.getElementsByClassName('field-value');
    for (var i = 0; i < value_nodes.length; i++)
    {
        remove_class(value_nodes[i], "fade-out");
        add_class(value_nodes[i], "fade-in");
    }
    remove_class(node, "info-overlay");
    add_class(node, "no-overlay");

    var to_fade_out = node.getElementsByClassName("detail");
    for (var i = 0; i < to_fade_out.length; i++)
    {
        remove_class(to_fade_out[i], "fade-in");
        add_class(to_fade_out[i], "fade-out");
    }
}

function remove_class(node, class_to_remove)
{
    var re = new RegExp("(?:^|\\s)" + class_to_remove + "(?!\\S)", "g");
    node.className = node.className.replace(re, '');
}

function add_class(node, class_to_add)
{
    var re = new RegExp("(?:^|\\s)" + class_to_add + "(?!\\S)", "g");
    if (!has_class(node, class_to_add))
    {
        node.className += " " + class_to_add;
    }
}

function has_class(node, class_to_check)
{
    var re = new RegExp("(?:^|\\s)" + class_to_check             + "(?!\\S)", "g");
    return (node.className.match(re) != null);
}
