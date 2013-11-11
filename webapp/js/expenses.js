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

    var inputs = document.getElementsByTagName("input");
    for (var i = 0; i < inputs.length; i++)
    {
        inputs[i].addEventListener("keydown", on_key_down, true);
        inputs[i].addEventListener("keyup", on_key_up, true);
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
        query_string += inputs[i].id + "=" + parseInt(parseFloat(input_num)*100);
        if (i < inputs.length-1)
        {
            query_string += "&";
        }
    }
    make_ajax_request("/api/update_reimbursement?" + query_string, save_finished, handle_ajax_error, "POST");
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

function add_class(node, class_to_add)
{
    var re = new RegExp("(?:^|\\s)" + class_to_add + "(?!\\S)", "g");
    if (!has_class(node, class_to_add))
    {
        node.className += " " + class_to_add;
    }
}

function is_numeric(n)
{
  return !isNaN(parseFloat(n)) && isFinite(n);
}

var before_key_press_field_value = null;
function on_key_down(event)
{
    if (before_key_press_field_value != null)
    {
        event.preventDefault();
    }
    else
    {
        before_key_press_field_value = event.srcElement.value;
    }
}

function on_key_up(event)
{
    var changed_input = event.srcElement.value;
    if (changed_input === "")
    {
        changed_input = "0";
    }
    if (!is_numeric(changed_input) ||
        max_values[event.srcElement.id] < changed_input ||
        (changed_input.indexOf(".") !== -1 && changed_input.split(".")[1].length > 2))
    {
        event.srcElement.value = before_key_press_field_value;
    }
    before_key_press_field_value = null;
    refresh_total_reimbursement();
}

function remove_class(node, class_to_remove)
{
    var re = new RegExp("(?:^|\\s)" + class_to_remove + "(?!\\S)", "g");
    node.className = node.className.replace(re, '');
}

function has_class(node, class_to_check)
{
    var re = new RegExp("(?:^|\\s)" + class_to_check + "(?!\\S)", "g");
    return (node.className.match(re) != null);
}
