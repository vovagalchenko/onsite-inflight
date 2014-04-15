window.mobilecheck = function() {
var check = false;
(function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4)))check = true})(navigator.userAgent||navigator.vendor||window.opera);
return check; }

if (window.mobilecheck())
{
    alert("This page doesn't support mobile devices... but here's a random meme.");
    window.location = "http://www.quickmeme.com/random";
}

function clone(obj)
{ 
    return JSON.parse(JSON.stringify(obj));
} 

function find_interviewer_mouseout_func()
{
    var tf = d3.select(".interviewer-textfield");
    var this_event = event || d3.event;
    var currently_moused_over_node = (this_event === null)? null : (this_event.relatedTarget || this_event.toElement);
    if (currently_moused_over_node == d3.select(".mag-glass").node() || currently_moused_over_node == tf.node())
        return;
    var find_interviewer_div = d3.select("#find-interviewer-div");
    if (tf.node().value == "")
    {
        find_interviewer_div.select(".mag-glass").
            classed("transition", true).
            classed("grayscale", true).
            style("left", 0);
        find_interviewer_div.select("#find-interviewer-label").
            attr("hidden", null).
            classed("transition", true).
            style("opacity", 1);
        tf.
            classed("transition", true).
            style("opacity", 0);
        find_interviewer_div.select("#cancel-search").
            classed("transition", true).
            style("opacity", 0);
        tf.node().blur();
    }
}

function filter_interviewers()
{
    var filter_term = d3.select(".interviewer-textfield").node().value;
    var filtered_interviewer_array = [];
    if (filter_term == "")
    {
        filtered_interviewer_array = clone(full_interviewer_array);
        setTimeout(find_interviewer_mouseout_func, 3000);
    }
    else
    {

        for (var i = 0; i < full_interviewer_array.length; i++)
        {
            if (full_interviewer_array[i].name.match(new RegExp(filter_term, "gi")))
            {
                filtered_interviewer_array.push(full_interviewer_array[i]);
            }
        }
    }
    update_interviewer_list(filtered_interviewer_array);
};

function set_up_interviewer_search()
{
    var find_interviewer_animation_duration = 200;
    var mag_glass_right_padding = 5;
    d3.select(".interviewer-textfield").
        on("mouseover", function()
        {
            var tf_div_rect = this.getBoundingClientRect();
            var mag_glass = d3.select(".mag-glass");
            var mag_glass_rect = mag_glass.node().getBoundingClientRect();
            mag_glass.
                classed("transition", true).
                classed("grayscale", false).
                style("left", 22 + tf_div_rect.width - mag_glass_rect.width - mag_glass_right_padding + "px");
            d3.select(this).select("#find-interviewer-label").
                classed("transition", true).
                style("opacity", 0);
            d3.select(".leaderboard-header").select(".interviewer-textfield").
                classed("transition", true).
                style("opacity", 1);
            d3.select("#cancel-search").
                classed("transition", true).
                style("opacity", 1);

        }).
        on("mouseout", find_interviewer_mouseout_func);
    d3.select("#cancel-search").
        on("click", function()
        {
            find_interviewer_mouseout_func();
            filter_interviewers();
        });
    d3.select(".interviewer-textfield").
        on("input", filter_interviewers);
}

function interviewer_array_has_interviews(interviewer_array)
{
    return interviewer_array.length > 0 && interviewer_array[0].interviews != null;
}

function minutes_to_human_readable_string(minutes)
{
    var scalar = minutes;
    var unit = 'm';
    if (minutes > 60)
    {
        scalar = Math.round((minutes/60)*100)/100;
        unit = 'h';
    }
    return [scalar, unit];
}

function update_interviewer_list(interviewer_array)
{
    var max_num_interviews = -1;
    if (interviewer_array_has_interviews(interviewer_array))
    {
        for (var i = 0; i < interviewer_array.length; i++)
        {
            if (max_num_interviews < interviewer_array[i].interviews.length)
            {
                max_num_interviews = interviewer_array[i].interviews.length;
            }
        }
    }
    var tableview = d3.select("#interviewer-list-tableview");
    var tableview_cells = tableview.selectAll(".tableview-cell").data(interviewer_array);
    var inner_tableviewcell_div = tableview_cells.enter().
        append("div").
            classed("tableview-cell", true).
            classed("non_selectable", true).
            style("cursor", "default");
    tableview_cells.
        on("mouseover", function(data)
        {
            d3.select(this).classed("highlighted", true);
            handle_cell_mouse_event(data);
        }).
        on("mouseout", function(data)
        {
            d3.select(this).classed("highlighted", false);
            handle_cell_mouse_event(null);
        });
    if (should_draw_bars)
    {
        max_value_of_interest = -1;
        for (var i = 0; i < interviewer_array.length; i++)
        {
            if (interviewer_array[i].value_of_interest > max_value_of_interest)
            {
                max_value_of_interest = interviewer_array[i].value_of_interest;
            }
        }
        inner_tableviewcell_div.append("div").
            classed("bar", true).
            style("width", "0%");
        tableview_width= tableview[0][0].getBoundingClientRect().width;
        bars = tableview.selectAll(".bar").data(interviewer_array);
        bars.transition().duration(1000).
            styleTween("width", function(interviewer, i, a)
            {
                var starting_pt_in_percents = (parseInt(a)/tableview_width)*100 + "%";
                return d3.interpolate(starting_pt_in_percents, (interviewer.value_of_interest/max_value_of_interest)*100 + "%");
            });
    }
    inner_tableviewcell_div.append("div").
        classed("interviewer_rank", true);
    tableview.selectAll(".interviewer_rank").data(interviewer_array).
        text(function(data)
        {
            return data.rank + 1;
        });
    inner_tableviewcell_div.append("div").
        classed("interviewer_avatar_frame", true).
        style("position", "relative").
        append("div").
            style("color", "rgb(255, 255, 255)").
            style("text-align", "center").
            style("line-height", "35px");
    tableview.selectAll(".interviewer_avatar_frame").data(interviewer_array).select("div").
            style("background-image", function(data)
            {
                var background_image = "";
                if (data.avatar_url)
                {
                    background_image = "url('" + data.avatar_url + "')";
                }
                return background_image;
            }).
            style("background-color", function(data)
            {
                var background_color = "";
                if (!data.avatar_url)
                {
                    background_color = "rgb(72, 195, 252)";
                }
                return background_color;
            }).
            text(function(data)
            {
                var initials = "";
                if (!data.avatar_url)
                {
                    initials = (data.name.charAt(0) + data.name.split(/\s/).pop().charAt(0)).toUpperCase();
                }
                return initials;
            });
    inner_tableviewcell_div.append("div").
        classed("interviewer_name", true).
        style("position", "relative");
    tableview.selectAll(".interviewer_name").data(interviewer_array).
        text(function(data, i)
        {
            return data.name;
        });
    inner_tableviewcell_div.append("div").
        classed("average-response-time-label", true).
        append("p");
    tableview.selectAll(".average-response-time-label").data(interviewer_array).select("p").
        html(function(data)
        {
            var value_of_interest = "<STRONG>N/A</STRONG>";
            if (data.value_of_interest)
            {
                var human_readable_value_of_interest = minutes_to_human_readable_string(data.value_of_interest);
                value_of_interest = "<STRONG>" + human_readable_value_of_interest[0].toString() + "</STRONG> " + human_readable_value_of_interest[1];
            }
            return value_of_interest;
        });
    if (interviewer_array_has_interviews(interviewer_array))
    {
        inner_tableviewcell_div.append("div").
            classed("dots-container", true).
                append("svg").
                attr("width", "100%").
                attr("height", "100%").
                attr("viewBox", "0 0 388 44");
        tableview.selectAll(".dots-container").data(interviewer_array).select("svg").
            attr("id", function(data)
            {
                return "interview-dots-" + data.username;
            });
    }
    tableview_cells.exit().remove();

    if (interviewer_array_has_interviews(interviewer_array))
    {
        num_interview_dots_per_row = Math.min(max_num_interview_dots_per_row, max_num_interviews);
        num_interview_dot_rows = Math.ceil(max_num_interviews/num_interview_dots_per_row);
    
        for (var i = 0; i < interviewer_array.length; i++)
        {
            var interview_dots_svg = d3.select("#interview-dots-" + interviewer_array[i].username)
            var viewBox_width = interview_dots_svg.attr('viewBox').split(/\s+/)[2];
            var viewBox_height = interview_dots_svg.attr('viewBox').split(/\s+/)[3];
            interview_dot_vertical_padding = (viewBox_height - 2*interview_dot_radius*num_interview_dot_rows - (num_interview_dot_rows-1)*padding_between_dot_rows)/2;
            var right_padding_per_dot = ((viewBox_width - (interview_dot_horizontal_padding*2)) - (2*interview_dot_radius*num_interview_dots_per_row))/(num_interview_dots_per_row+1);
            var circles = interview_dots_svg.selectAll('circle').data(interviewer_array[i].interviews)
            var cx_function = function(data, i)
            {
                var column  = i%num_interview_dots_per_row;
                return interview_dot_horizontal_padding + column*right_padding_per_dot + (1 + 2*column)*interview_dot_radius + "px";
            };
            var cy_function = function(data, i)
            {
                var row = Math.floor(i/num_interview_dots_per_row);
                return interview_dot_vertical_padding + row*padding_between_dot_rows + (1 + 2*row)*interview_dot_radius + "px";
            };
            var circle_animation_duration = 1000;
            circles.enter().append('circle').
                attr('r', 0).
                attr('cx', cx_function).
                attr('cy', cy_function).
                on('mouseout', function(d, i)
                {
                    d3.selectAll(".interview-dot-popover").style('opacity', 0).remove();
                    d3.select("#progress_indicator").attr('hidden', '');
                });
            var circle_animation_delay_function = function(data, i)
            {
                return i*100;
            };
            circles.
                on('mouseover', function(d, i)
                {
                    var circle_rect = this.getBoundingClientRect();
                    var popover_div = d3.select("body").append("div").style('opacity', 0);
                    var pointer_height = 10;
                    var popover_border_width = 1;
                    var popover_bottom_padding = 4;
                    popover_div.
                        classed("interview-dot-popover", true).
                        attr("id", "interview_" + d.id).
                        html(d3.select("#progress_indicator").
                            attr('hidden', null).
                            style("margin-top", null).
                            style("margin-left", 166 + "px").
                            node().outerHTML).
                        style('top', function(d)
                        {
                            return circle_rect.top - pointer_height - this.getBoundingClientRect().height - popover_bottom_padding + "px";
                        }).
                        style('left', function(d)
                        {
                            return circle_rect.left - this.getBoundingClientRect().width/2 - popover_border_width*2 + "px";
                        }).
                        style('opacity', 0).
                        transition().
                        duration(500).
                        style('opacity', 1).each("end", function()
                        {
                            make_ajax_request("/api/candidate_detail?candidate_name=" + encodeURIComponent(d.candidate_name) + "&show_scores=false&date=" + (new Date(d.end_time).getTime()/1000).toString(), update_interview_popover, null);
                        })
    
                }).
                transition().
                attr('r', interview_dot_radius).
                attr('cx', cx_function).
                attr('cy', cy_function).
                attr('fill', function(interview)
                {
                    var time_it_took = time_to_response(interview);
                    var color = ranges[ranges.length - 1].color;
                    for (var j = 0; j < ranges.length; j++)
                    {
                        if (time_it_took <= ranges[j].range[1])
                        {
                            color = ranges[j].color;
                            break;
                        }
                    }
                    return color;
                }).
                delay(circle_animation_delay_function).
                duration(circle_animation_duration);
            circles.exit().
                transition().
                attr('r', 0).
                delay(circle_animation_delay_function).
                duration(circle_animation_duration).
                remove();
        }
    }
}
