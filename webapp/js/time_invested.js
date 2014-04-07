var full_interviewer_array = null;

window.onload = function()
{
    var header_bar = d3.select(".header-bar");
    var progress_indicator = d3.select("#progress_indicator");
    var header_bar = d3.select(".header-bar");
    var progress_indicator_style = getComputedStyle(progress_indicator.node());
    var header_bar_style = getComputedStyle(header_bar.node());
    header_bar.insert("div", ":first-child").
        style("position", "absolute").
        attr("id", "progress-indicator-container").
        html(progress_indicator.
            attr("hidden", null).
            style("margin-left", (parseInt(header_bar_style.width) - parseInt(progress_indicator_style.width))/2 + "px").
            style("margin-top", (parseInt(header_bar_style.height) - parseInt(progress_indicator_style.height))/2 - parseInt(header_bar_style.paddingTop) + "px").
            node().outerHTML);
    make_ajax_request("/api/time_invested", on_interviewer_data_receipt, null);
}

function on_interviewer_data_receipt(received_data)
{
    var interviewer_array = [];
    var colors = get_colors(Object.keys(received_data.interviewers).length);
    var color_index = 0;
    for (var interviewer_email in received_data.interviewers)
    {
        var interviewer = received_data.interviewers[interviewer_email];
        total_time_invested = 0;
        for (var i = 0; i < received_data.time_invested.length; i++)
        {
            num_secs_invested_that_week = received_data.time_invested[i].investment[interviewer_email];
            if (num_secs_invested_that_week)
            {
                total_time_invested += num_secs_invested_that_week;
            }
        }
        // Value of interest has to be in minutes
        interviewer['value_of_interest'] = total_time_invested/60;
        interviewer['color'] = colors[color_index++];
        interviewer_array.push(interviewer);
    }
    interviewer_array.sort(function (interviewer_a, interviewer_b)
    {
        return interviewer_b.value_of_interest - interviewer_a.value_of_interest;
    });
    full_interviewer_array = interviewer_array;
    var rank = 0;
    for (var i = 0; i < full_interviewer_array.length; i++)
    {
        full_interviewer_array[i].rank = rank++;
    }

    d3.select("#progress-indicator-container").remove();
    
    update_interviewer_list(interviewer_array);
    set_up_interviewer_search();
    set_up_stacked_line_graph(interviewer_array, received_data.time_invested);
}

function interpolate(value, max, dimension)
{
    return (value/max)*dimension;
}

function set_up_stacked_line_graph(interviewer_array, time_invested_array)
{
    var graph = d3.select("#graph");
    var viewBox_width = graph.attr('viewBox').split(/\s+/)[2];
    var viewBox_height = graph.attr('viewBox').split(/\s+/)[3];
    var max_value = 0;
    for (var i = 1; i < interviewer_array.length; i++)
    {
        for (var j = 0; j < time_invested_array.length; j++)
        {
            var to_add = time_invested_array[j].investment[interviewer_array[i - 1].email] === null? 0 : time_invested_array[j].investment[interviewer_array[i - 1].email];
            if (time_invested_array[j].investment[interviewer_array[i].email] === undefined)
            {
                time_invested_array[j].investment[interviewer_array[i].email] = 0;
            }
            time_invested_array[j].investment[interviewer_array[i].email] += to_add;
            if (i == interviewer_array.length - 1 && max_value < time_invested_array[j].investment[interviewer_array[i].email])
            {
                max_value = time_invested_array[j].investment[interviewer_array[i].email];
            }
        }
    }
    interviewer_array.reverse();
    var paths_group = d3.select("#paths").selectAll("path").data(interviewer_array);
    var num_weeks = Object.keys(time_invested_array).length;
    var initial_path_def = "M 0 0 ";
    for (var i = 0; i < num_weeks; i++)
    {
        initial_path_def += "L " + interpolate(i, num_weeks - 1, viewBox_width) + " " + 0 + " ";
    }
    initial_path_def += 'L ' + viewBox_width + ' 0 z';
    paths_group.enter().append('path').
        attr('fill', function(interviewer)
        {
            return interviewer.color.get_css();
        }).
        attr('d', function(interviewer)
        {
            var path_def = "M 0 " + viewBox_height + " ";
            for (var i = 0; i < num_weeks; i++)
            {
                path_def += 'L ' + interpolate(i, num_weeks - 1, viewBox_width) + ' ' + (viewBox_height - interpolate(time_invested_array[i].investment[interviewer.email], max_value, viewBox_height)) + ' ';
            }
            path_def += 'L ' + viewBox_width + ' ' + viewBox_height + ' z';
            return path_def;
        });
}

function handle_cell_mouse_event(cell_data)
{
}
