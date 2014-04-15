var full_interviewer_array = null;
var now = new Date();
var end_date = now;
end_date.setDate(now.getDate() - 1);
var num_days = 15*7 // 15 weeks
var start_date = new Date(end_date.getTime());
start_date.setDate(end_date.getDate() - num_days);

var scale_attributes = {};
var line_graph_data = [];
var ajax_supplied_data = null;

var max_width = null;
var prev_mouse_x = null;
var grip_kind_held = null;

var side_grip_size = 20;
var should_draw_bars = true;

window.onload = function()
{
    graph_bounding_rect = d3.select("#graph")[0][0].getBoundingClientRect();
    max_width = graph_bounding_rect.width + 2*side_grip_size;
    d3.select(".range-select-bar").style('width', max_width + "px");
    d3.select(".range-select-bar").style('padding-left', 0 + "px");

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
    make_ajax_request("/api/time_invested?num_days=" + num_days, on_interviewer_data_receipt, null);
}

window.onresize = function()
{
    old_max_width = max_width - 40;
    graph_bounding_rect = d3.select("#graph")[0][0].getBoundingClientRect();
    max_width = graph_bounding_rect.width + 2*side_grip_size;
    refresh_center_grip_to_focused_area();
}

window.onmouseup = function()
{
    // Clear the search
    d3.select(".interviewer-textfield").node().value = "";
    find_interviewer_mouseout_func();
    filter_interviewers();
    // Snap to closest discrete point
    final_padding = null;
    final_width = null;
    if (grip_kind_held === 'left')
    {
        left_padding = parseInt(d3.select(".range-select-bar")[0][0].style.paddingLeft);
        x_unit_width = (max_width - side_grip_size*2)/(scale_attributes.num_values - 1)
        padding_in_x_units = left_padding/x_unit_width;
        final_padding = Math.floor(padding_in_x_units) * x_unit_width;
        remainder = padding_in_x_units*x_unit_width - final_padding;
        if (remainder > x_unit_width/2)
        {   
            final_padding += x_unit_width;
        } 
        final_width = parseInt(document.getElementsByClassName('range-select-bar')[0].style.width) + (left_padding - final_padding);
    }
    else if (grip_kind_held === 'right')
    {
        bar_width = d3.select("#center-grip")[0][0].offsetWidth;
        x_unit_width = (max_width - side_grip_size*2)/(scale_attributes.num_values - 1)
        bar_width_in_x_units = bar_width/x_unit_width;
        final_width = Math.floor(bar_width_in_x_units) * x_unit_width;
        remainder = bar_width_in_x_units*x_unit_width - Math.floor(bar_width_in_x_units)*x_unit_width;
        if (remainder > x_unit_width/2)
        {
            final_width += x_unit_width;
        }
        final_width += side_grip_size*2;
    }
    else if (grip_kind_held === 'center')
    {
        left_padding = parseInt(d3.select(".range-select-bar")[0][0].style.paddingLeft);
        x_unit_width = (max_width - side_grip_size*2)/(scale_attributes.num_values - 1)
        padding_in_x_units = left_padding/x_unit_width;
        final_padding = Math.floor(padding_in_x_units) * x_unit_width;
        remainder = padding_in_x_units*x_unit_width - final_padding;
        if (remainder > x_unit_width/2)
        {
            final_padding += x_unit_width;
        }
    }
    var range_select_bar = d3.select(".range-select-bar");
    if (final_width !== null)
    {
        range_select_bar.style("width", final_width + "px");
    }
    if (final_padding !== null)
    {
        range_select_bar.style("padding-left", final_padding + "px");
    }
    refresh_focused_area_to_center_grip(true);
    prev_mouse_x = null;
    grip_kind_held = null;
}

window.onmousemove = function()
{
    if (grip_kind_held !== null)
    {
        new_mouse_x = mouse_x(event);
        delta_x = new_mouse_x - prev_mouse_x;
        prev_mouse_x = new_mouse_x;
        var old_padding = parseInt(document.getElementsByClassName('range-select-bar')[0].style.paddingLeft);
        if (grip_kind_held === 'left')
        {
            var newPadding = Math.max(Math.min(old_padding + delta_x, max_width - side_grip_size*2), 0);
            var padding_delta = newPadding - old_padding;
            var newWidth = Math.max(Math.min(parseInt(document.getElementsByClassName('range-select-bar')[0].style.width) - padding_delta, max_width), side_grip_size*2);
            d3.select(".range-select-bar").style('padding-left', newPadding + "px").style('width', newWidth + "px");
        }
        else if (grip_kind_held === 'right')
        {
            var newWidth = Math.max(Math.min(parseInt(document.getElementsByClassName('range-select-bar')[0].style.width) + delta_x,     max_width - old_padding), side_grip_size*2);
            d3.select(".range-select-bar").style('width', newWidth + "px");
        }
        else if (grip_kind_held === 'center')
        {
            var newPadding = Math.max(Math.min(parseInt(document.getElementsByClassName('range-select-bar')[0].style.paddingLeft) + delta_x, max_width - parseInt(document.getElementsByClassName('range-select-bar')[0].style.width)), 0);
            d3.select(".range-select-bar").style('padding-left', newPadding + "px");
        }
        refresh_focused_area_to_center_grip(false);
    }
}

function refresh_focused_area_to_center_grip(should_update_interviewer_list)
{
    grip_bounding_rect = document.getElementById("center-grip").getBoundingClientRect();
    graph_bounding_rect = document.getElementById("graph").getBoundingClientRect();
    var viewBox_width = get_graph_viewBox()[2];
    var left_x_bound = (grip_bounding_rect.left - graph_bounding_rect.left)*(viewBox_width/graph_bounding_rect.width);
    var right_x_bound = viewBox_width - (graph_bounding_rect.right - grip_bounding_rect.right)*(viewBox_width/graph_bounding_rect.width);
    refresh_focused_area(left_x_bound, right_x_bound, should_update_interviewer_list);
}

function refresh_center_grip_to_focused_area()
{
    grip_bounding_rect = document.getElementById("center-grip").getBoundingClientRect();
    graph_bounding_rect = document.getElementById("graph").getBoundingClientRect();
    var viewBox_width = get_graph_viewBox()[2];
    var left_border_x = d3.select("#left-border").attr("x1");
    var right_border_x = d3.select("#right-border").attr("x1");
    var left_border_screen_x = left_border_x*(graph_bounding_rect.width/viewBox_width);
    var right_border_screen_x = right_border_x*(graph_bounding_rect.width/viewBox_width);
    d3.select(".range-select-bar").
        style("padding-left", left_border_screen_x + "px").
        style("width", right_border_screen_x - left_border_screen_x + side_grip_size*2 + "px");
}

function handle_grip_mouse_down(grip_kind)
{
    if (grip_kind === 'left')
    {
        grip_kind_held = 'left';
    }
    else if (grip_kind === 'right')
    {
        grip_kind_held = 'right';
    }
    else if (grip_kind === 'center')
    {
        grip_kind_held = 'center';
    }
    else
    {
        console.log("unknown grip kind: " + grip_kind);
    }
    prev_mouse_x = mouse_x(event);
}

function mouse_x(e)
{
    if (e.pageX)
    {
        return e.pageX;
    }
    if (e.clientX)
    {
        return e.clientX + (document.documentElement.scrollTop? document.documentElement.scrollLeft : document.body.scrollLeft);
    }
    return null;
}

function pad(num, size)
{
    var s = num+"";
    while (s.length < size) s = "0" + s;
    return s;
}

function date_string(date)
{
    return date.getFullYear() + "-" + pad(date.getMonth() + 1, 2) + "-" + pad(date.getDate(), 2);
}

function on_interviewer_data_receipt(received_data)
{
    ajax_supplied_data = received_data;
    var time_spent = received_data['time_spent'];
    for (var date = new Date(start_date.getTime()); date.getTime() <= end_date.getTime(); date.setDate(date.getDate() + 1))
    {
        if (date.getDay() != 6 && date.getDay() != 0)
        {
            date_str = date_string(date);
            interview_data_for_date = time_spent[date_str];
            data_for_date = {
                'date' : new Date(date.getTime()),
                'time_spent' : 0
            };
            for (var key in interview_data_for_date)
            {
                data_for_date.time_spent += interview_data_for_date[key];
            }
            line_graph_data.push(data_for_date);
        }
    }
    d3.select("#progress-indicator-container").remove();

    scale_attributes = {
        'max_value' : 0,
        'num_values' : line_graph_data.length
    }
    for (var i = 0; i < line_graph_data.length; i++)
    {
        if (scale_attributes.max_value < line_graph_data[i].time_spent)
        {
            scale_attributes.max_value = line_graph_data[i].time_spent;
        }
    }
    
    line_graph_data
    set_up_line_graph(line_graph_data);
    refresh_focused_area(undefined, undefined, true);
    set_up_interviewer_search();
}

function interpolate(value, max, dimension)
{
    return (value/max)*dimension;
}

function get_graph_viewBox()
{
    var graph = d3.select("#graph");
    return graph.attr('viewBox').split(/\s+/);
}

function refresh_focused_area(left_border_x, right_border_x, should_update_interviewer_list)
{
    var graph_viewBox = get_graph_viewBox();
    var viewBox_width = graph_viewBox[2];
    var viewBox_height = graph_viewBox[3];
    var animate_left_border, animate_right_border = false;
    if (typeof left_border_x == 'undefined')
    {
        left_border_x = 0;
        animate_left_border = true;
    }
    if (typeof right_border_x == 'undefined')
    {
        right_border_x = viewBox_width;
        animate_right_border = true;
    }
    var left_border = d3.select("#left-border").
        attr('x1', left_border_x).
        attr('y1', viewBox_height).
        attr('x2', left_border_x);
    if (animate_left_border)
    {
        left_border = left_border.attr('y2', viewBox_height).transition();
    }
    left_border.attr('y2', 0);
    right_border = d3.select("#right-border").
        attr('x1', right_border_x).
        attr('y1', viewBox_height).
        attr('x2', right_border_x);
    if (animate_right_border)
    {
        right_border = right_border.attr('y2', viewBox_height).transition();
    }
    right_border.attr('y2', 0);
    d3.select("#focus-clip").select("rect").
        attr('x', left_border_x).
        attr('width', right_border_x - left_border_x);

    if (should_update_interviewer_list)
    {
        interviewer_array = [];
        var start_index = Math.round(left_border_x/(viewBox_width/(scale_attributes.num_values - 1)));
        var end_index = Math.round(right_border_x/(viewBox_width/(scale_attributes.num_values - 1)));
        interviewer_dict = {};
        for (var i = start_index; i <= end_index; i++)
        {
            date = line_graph_data[i].date;
            time_spent_for_date = ajax_supplied_data.time_spent[date_string(date)];
            for (var email in time_spent_for_date)
            {
                if (!(email in interviewer_dict))
                {
                    interviewer_dict[email] = 0;
                }
                interviewer_dict[email] += time_spent_for_date[email];
            }
        }
        for (var email in interviewer_dict)
        {
            interviewer = ajax_supplied_data.interviewers[email];
            interviewer['value_of_interest'] = (interviewer_dict[email]/60);
            interviewer_array.push(interviewer);
        }
        interviewer_array.sort(function(interviewer_a, interviewer_b)
        {
            return interviewer_b.value_of_interest - interviewer_a.value_of_interest;
        });
        for (var i = 0; i < interviewer_array.length; i++)
        {
            interviewer_array[i].rank = i;
        }
        full_interviewer_array = interviewer_array;
        update_interviewer_list(interviewer_array, true);
    }
}

function set_up_line_graph(line_graph_data)
{
    var graph_viewBox = get_graph_viewBox();
    var viewBox_width = graph_viewBox[2];
    var viewBox_height = graph_viewBox[3];
    var max_value = 0;
    var lines = [];
    var i = 0;
    var prev_point = null;
    points = interpolate(0, scale_attributes.num_values - 1, viewBox_width) + "," + viewBox_height;
    initial_points = points;
    for (var i = 0; i < line_graph_data.length; i++)
    {
        if (prev_point === null)
        {
            prev_point = [interpolate(i, scale_attributes.num_values - 1, viewBox_width), viewBox_height - interpolate(line_graph_data[i].time_spent, scale_attributes.max_value, viewBox_height)];
        }
        else
        {
            new_prev_point = [interpolate(i, scale_attributes.num_values - 1, viewBox_width), viewBox_height - interpolate(line_graph_data[i].time_spent, scale_attributes.max_value, viewBox_height)];
            lines.push([prev_point, new_prev_point]);
            prev_point = new_prev_point;
        }
        x_val = interpolate(i, scale_attributes.num_values - 1, viewBox_width).toString();
        points +=   " " + x_val + "," +
                    (viewBox_height - interpolate(line_graph_data[i].time_spent, scale_attributes.max_value, viewBox_height)).toString();
        initial_points += " " + x_val + "," + viewBox_height;
    }
    points += " " + viewBox_width + "," + viewBox_height;
    
    var major_line_graph= d3.select("#major_line_graph").selectAll("line").data(lines);
    major_line_graph.enter().append('line').
        attr('stroke', '#AAAAAA').
        attr('x1', function(line)
        {
            return line[0][0];
        }).
        attr('x2', function(line)
        {
            return line[1][0];
        }).
        attr('y1', viewBox_height).
        attr('y2', viewBox_height).
        style('opacity', 0);
    major_line_graph.
        transition().
        style('opacity', 1).
        attr('y1', function(line)
        {
            return line[0][1];
        }).
        attr('y2', function(line)
        {
            return line[1][1];
        });
    var minor_line_graph_polygon = d3.select("#minor_line_graph").select("polygon");
    minor_line_graph_polygon.
        attr('points', initial_points).
        transition().
        attr('points', points);
}

function handle_cell_mouse_event(cell_data)
{
}
