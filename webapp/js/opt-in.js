var last_received_opt_in_timestamp = null;
var known_opt_ins = {};

window.onload = function()
{
    synchronize_with_server();
    setInterval(function()
    {
        synchronize_with_server();
    }, 5000);
}

function handle_ajax_error(error_string)
{
    alert(error_string);
}

function configure_table_cell(opt_in)
{
    var cell = opt_in['table_cell']
    cell.className = "chosen_" + ((Math.floor(Math.random()*100)%4) + 1);
    cell.innerHTML = opt_in['nickname'];
}

function get_table_cell_for_row_and_column(row, column)
{
    return document.getElementsByTagName("tr")[row].getElementsByTagName("td")[column];
}

function get_table_cell(phone_number)
{
    var num_rows = document.getElementsByTagName("tr").length;
    var num_columns = document.getElementsByTagName("tr")[0].getElementsByTagName("td").length;
    var start_row = parseInt(phone_number.slice(0, 5))%num_rows;
    var start_column = parseInt(phone_number.slice(5))%num_columns;
        
    var row = start_row;
    var column = start_column;
    var cell = null;
    do
    {
        cell = get_table_cell_for_row_and_column(row, column)
        if (column === (num_columns - 1))
        {
            row = (row + 1)%num_rows;
        }
        column = (column + 1)%num_columns;
    }
    while (cell.className.indexOf("chosen_") === 0 &&
           (row != start_row || column != start_column));
    return cell;
}

function update_opt_in_table(data)
{
    if (!data || data.length == 0)
        return;
    
    var last_ts = last_received_opt_in_timestamp;
    for (var i = 0; i < data.length; i++)
    {
        var opt_in = data[i];
        var phone_number = opt_in['phone_number'];
        var known_opt_in = known_opt_ins[phone_number];
        if (!known_opt_in)
        {
            known_opt_in = {};
            known_opt_in['table_cell'] = get_table_cell(phone_number);
        }
        for (var key in opt_in)
        {
            known_opt_in[key] = opt_in[key];
        }
        configure_table_cell(known_opt_in);
        known_opt_ins[phone_number] = known_opt_in;
        last_ts = opt_in['created'];
    }
    last_received_opt_in_timestamp = last_ts;
}

function synchronize_with_server()
{
    var opt_in_list_url = '/api/opt_in_list';
    if (last_received_opt_in_timestamp == null)
    {
        last_received_opt_in_timestamp = Math.round(new Date().getTime()/1000)
    }
    opt_in_list_url += '?date=' + last_received_opt_in_timestamp;
    make_ajax_request(opt_in_list_url, update_opt_in_table, handle_ajax_error);
}
