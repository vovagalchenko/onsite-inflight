var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
var ranges = [ 
    {   
        'range' : [0, 20*60000],
        'color' : 'rgb(151, 215, 255)',
        'label' : "< 20 m", 
        'label_color' : 'rgb(0, 0, 0)'
    },  
    {   
        'range' : [20*60000, 40*60000],
        'color' : 'rgb(1, 59, 102)',
        'label' : "20 < 40 m", 
        'label_color' : 'rgb(255, 255, 255)'
    },  
    {   
        'range' : [40*60000, Number.MAX_VALUE],
        'color' : 'rgb(229, 19, 19)',
        'label' : "> 40 m", 
        'label_color' : 'rgb(255, 255, 255)'
    }
];  
var interview_dot_horizontal_padding = 10; 
var interview_dot_vertical_padding;
var interview_dot_radius = 4;
var padding_between_dot_rows = 5;
var max_num_interview_dots_per_row = 15; 
var num_interview_dots_per_row;
var num_interview_dot_rows;
var full_interviewer_array = null;

window.onhashchange = function()
{   
    var hash = window.location.hash;
    var url = "/api/time_to_respond_stats";
    if (hash == "#include_non_responders")
    {   
        url += "?include_non_responders=true";
    }   
    var progress_indicator = d3.select("#progress_indicator");
    var header_bar = d3.select(".header-bar");
    var progress_indicator_style = getComputedStyle(progress_indicator.node());
    var header_bar_style = getComputedStyle(header_bar.node());
    d3.select("#total-interviews-div").attr("hidden", true);
    header_bar.insert("div", ":first-child").
        style("position", "absolute").
        attr("id", "progress-indicator-container").
        html(progress_indicator.
            attr("hidden", null).
            style("margin-left", (parseInt(header_bar_style.width) - parseInt(progress_indicator_style.width))/2 + "px").
            style("margin-top", (parseInt(header_bar_style.height) - parseInt(progress_indicator_style.height))/2 - parseInt(header_bar_style.paddingTop) + "px").
            node().outerHTML);
    make_ajax_request(url, on_interviewer_data_receipt, null);
}   

window.onload = window.onhashchange;

// In ms
function time_to_response(interview)
{   
    var return_value = Number.MAX_VALUE;
    if (interview.cultural_score_ts !== null)
    {   
        return_value = new Date(interview['cultural_score_ts']).getTime() - (new Date(interview['end_time']).getTime() + 5*60000);
    }   
    return return_value;
}   


function clone(obj)
{   
    return JSON.parse(JSON.stringify(obj));
}   

function get_score(interviewer, max_num_interviews)
{   
    var cutoff = 30*60000;
    var num_interviews = interviewer.interviews.length;
    var num_good = (max_num_interviews - num_interviews)/2
    var num_bad = num_good;
    for (var i = 0; i < num_interviews; i++)
    {   
        if (time_to_response(interviewer.interviews[i]) <= cutoff)
        {   
            num_good += 1;
        }   
        else
        {   
            num_bad += 1;
        }   
    }   
    return num_good/(num_bad + num_good);
}   

function get_buckets(interviewers)
{   
    var buckets = clone(ranges);
    for (var i = 0; i < interviewers.length; i++)
    {   
        for (var j = 0; j < interviewers[i].interviews.length; j++)
        {   
            var time_to_respond = time_to_response(interviewers[i].interviews[j]);
            for (var k = 0; k < buckets.length; k++)
            {   
                if (!buckets[k].interviews)
                {   
                    buckets[k].interviews = []; 
                }   
                if (time_to_respond <= buckets[k].range[1])
                {   
                    buckets[k].interviews.push(interviewers[i].interviews[j]);
                    break;
                }   
            }   
        }   
    }   
    return buckets;
}   

function percentage_to_coordinate(percentage, center, radius)
{   
    var angle = percentage*Math.PI*2;
    return {
        'x' : center.x + Math.cos(angle)*radius,
        'y' : center.y + Math.sin(angle)*radius
    };  
}   

function coordinate_to_percentage(coordinate, center, radius)
{   
    var angle = Math.acos((coordinate.x - center.x)/radius);
    if (coordinate.y < center.y)
    {   
        angle = 2*Math.PI - angle;
    }   
    var percentage = angle/(Math.PI*2);
    return percentage;
}   


function coordinate_to_percentage(coordinate, center, radius)
{
    var angle = Math.acos((coordinate.x - center.x)/radius);
    if (coordinate.y < center.y)
    {
        angle = 2*Math.PI - angle;
    }
    var percentage = angle/(Math.PI*2);
    return percentage;
}

function update_interview_popover(candidate)
{
    var popover = d3.select('.interview-dot-popover');
    if (popover.node() === null)
        return;
    var interview_id = parseInt(popover.attr('id').replace('interview_', ''));
    var received_interviews = candidate.interviews;
    var found = false;
    for (var i = 0; i < received_interviews.length; i++)
    {
        if (received_interviews[i].id === interview_id)
        {
            found = true;
            break;
        }
    }
    if (!found)
    {
        return;
    }
    var candidate_detail_div = popover.append('div').classed('measure', true);
    candidate_detail_div.append('strong').style('font-size', 20).text(candidate.candidate_name);
    candidate_detail_div.append('br');
    candidate_detail_div.append('p').text(candidate.position);
    candidate_detail_div.append('br');
    var start_time = new Date(candidate.interviews[0].start_time);
    candidate_detail_div.append('strong').text(months[start_time.getMonth()] + " " + start_time.getDate() + ", " + start_time.getFullYear());
    candidate_detail_div.append('br');
    candidate_detail_div.append('br');
    candidate_detail_div.append('br');
    var interview_sessions_enter = candidate_detail_div.selectAll('.interview-session-details').data(candidate.interviews).enter();
    var interview_sessions = interview_sessions_enter.append('div').style("height", "37px");
    interview_sessions.append('div').style("float", "left").style("padding-right", "10px").append('p').style("line-height", "37px").html(function (d)
    {
        var result = d.interviewer.name;
        if (d.id === interview_id)
        {
            result = "<strong>" + result + "</strong>";
        }
        return result;
    });
    interview_sessions.append('p').style('float', 'right').style('text-align', 'left').style('width', '50px').style("line-height", "37px").html(function (d)
    {
        var result = null;
        if (d.cultural_score_ts === null)
        {
            result = "<strong>&infin;</strong>";
        }
        else
        {
            result = "<strong>" + Math.round(time_to_response(d)/60000).toString() + "</strong>" + " m";
        }
        return result;
    });
    interview_sessions.append('div').classed("interview-detail-color-indicator", true).
        style('background-color', function(d)
    {
        var color = "rgb(0, 0, 0)";
        if (d.cultural_score_ts === null)
        {
            color = ranges[ranges.length - 1].color;
        }
        else
        {
            for (var i = 0; i < ranges.length; i++)
            {
                if (time_to_response(d) <= ranges[i].range[1])
                {
                    color = ranges[i].color;
                    break;
                }
            }
        }
        return color;
    });
    interview_sessions.append('div').classed("interview-details-spacer", true).append("hr");
    
    var old_computed_style = getComputedStyle(popover.node())
    var expanded_popover_height = parseInt(getComputedStyle(candidate_detail_div.node()).height);
    popover.transition().style('top', parseInt(old_computed_style.top) - (expanded_popover_height - parseInt(old_computed_style.height))).style('height', expanded_popover_height).each("end", function()
    {
        popover.select('#progress_indicator').transition().style('opacity', 0).remove().each("end", function()
        {
            candidate_detail_div.style("opacity", 0).classed('measure', false).transition().style("opacity", 1);
        });
    });
}

function on_interviewer_data_receipt(interviewers_data)
{
    var interviewer_array = [];
    var max_num_interviews = -1;
    for (var interviewer_email in interviewers_data)
    {
        var interviewer = interviewers_data[interviewer_email];
        if (max_num_interviews < interviewer.interviews.length)
        {
            max_num_interviews = interviewer.interviews.length;
        }
        var total_interview_response_time = 0;
        var total_num_responses = 0;
        var interview_index = interviewer.interviews.length;
        while(interview_index--)
        {
            if (interviewer.interviews[interview_index].cultural_score_ts)
            {
                total_num_responses++;
                total_interview_response_time += time_to_response(interviewer.interviews[interview_index]);
            }
        }
        interviewer['avg_response_time'] = (total_num_responses > 0)? Math.round((total_interview_response_time/total_num_responses)/60000) : null;
        interviewer['username'] = interviewer['email'].replace(/@box.com$/, '');
        interviewer_array.push(interviewer);
    }
    interviewer_array.sort(function (interviewer_a, interviewer_b)
    {
        result = get_score(interviewer_b, max_num_interviews) - get_score(interviewer_a, max_num_interviews);
        var a_avg_response_time = Number.MAX_VALUE;
        var b_avg_response_time = Number.MAX_VALUE;
        if (interviewer_a.avg_response_time !== null)
        {
            a_avg_response_time = interviewer_a.avg_response_time;
        }
        if (interviewer_b.avg_response_time !== null)
        {
            b_avg_response_time = interviewer_b.avg_response_time;
        }
        if (result === 0)
        {
            result = a_avg_response_time - b_avg_response_time;
        }
        return result;
    });
    full_interviewer_array = interviewer_array;

    d3.select("#progress-indicator-container").remove();
    d3.select("#total-interviews-div").attr("hidden", null);

    update_interviewer_list(interviewer_array);
    set_up_interviewer_search();
    update_piechart(interviewer_array);

    var total_interviews_label = d3.select('#total-interviews-label');
    var total_interviews_div = total_interviews_label.select("#total-interviews-div");
    var total_interviews_content_rect = total_interviews_div.node().getBoundingClientRect();
    total_interviews_div.style("padding-top", (parseInt(total_interviews_label.attr("height")) - total_interviews_content_rect.height)/2 + "px");
}

function set_up_interviewer_search()
{
    var find_interviewer_animation_duration = 200;
    var find_interviewer_mouseout_func = function()
    {
        var find_interviewer_div = d3.select("#find-interviewer-div");
        var tf = find_interviewer_div.select(".interviewer-textfield");
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
    };
    var mag_glass_right_padding = 5;
    d3.select("#find-interviewer-div").
        on("mouseover", function()
        {
            var tf_div_rect = this.getBoundingClientRect();
            var mag_glass = d3.select(this).select(".mag-glass");
            var mag_glass_rect = mag_glass.node().getBoundingClientRect();
            mag_glass.
                classed("transition", true).
                classed("grayscale", false).
                style("left", tf_div_rect.width - mag_glass_rect.width - mag_glass_right_padding + "px").
                style("right", 0);
            d3.select(this).select("#find-interviewer-label").
                classed("transition", true).
                style("opacity", 0);
            d3.select(this).select(".interviewer-textfield").
                classed("transition", true).
                style("opacity", 1);
            d3.select(this).select("#cancel-search").
                classed("transition", true).
                style("opacity", 1);
        
        }).
        on("mouseout", find_interviewer_mouseout_func);
    var filter_interviewers = function()
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
    d3.select("#cancel-search").
        on("click", function()
        {
            d3.select(".interviewer-textfield").node().value = "";
            find_interviewer_mouseout_func();
            filter_interviewers();
        });
    d3.select(".interviewer-textfield").
        on("input", filter_interviewers);
}
    
function update_piechart(interviewer_array)
{
    var buckets = get_buckets(interviewer_array);
    var total_num_interviews = 0;
    for (var i = 0; i < buckets.length; i++)
    {
        if (buckets[i].interviews)
        {
            total_num_interviews += buckets[i].interviews.length;
        }
    }
    var slices_group = d3.select("#slices").selectAll("path").data(buckets);
    var pie_chart = d3.select("#pie-chart");
    var viewBox_width = pie_chart.attr('viewBox').split(/\s+/)[2];
    var viewBox_height = pie_chart.attr('viewBox').split(/\s+/)[3];
    var center = {};
    var piechart_animation_duration = 1000;
    center['x'] = viewBox_width/2;
    center['y'] = viewBox_height/2;

    var legend_box_width = 75;
    var legend_box_height = 20;
    var legend_label_height = 8;
    var legend_box_padding = 0;
    var num_legend_boxes = buckets.length;
    var legend_y_origin = (viewBox_height - (num_legend_boxes*(legend_box_height + legend_box_padding) - legend_box_padding))/2;
    var legend_box_y_func = function(data, i)
    {   
        return legend_y_origin + i*(legend_box_height + legend_box_padding) - legend_box_padding;
    };
    pie_chart.selectAll("rect").data(buckets).enter().append("rect").
        attr("width", legend_box_width).
        attr("height", legend_box_height).
        attr("x", 0).
        attr("y", legend_box_y_func).
        attr("fill", function(data, i)
        {
            return data.color;
        }).
        style("opacity", 0).
        transition().
        duration(piechart_animation_duration).
        style("opacity", 1);
    var legend_label_y_func = function(data, i)
    {
        return legend_box_y_func(data, i) + (legend_box_height + legend_label_height)/2;
    };
    pie_chart.selectAll(".legend-label").data(buckets).enter().append("text").
        classed("legend-label", true).
        attr("width", legend_box_width).
        attr("height", legend_label_height).
        attr("x", legend_box_width/2).
        attr("y", legend_label_y_func).
        attr("fill", function(data)
        {
            return data.label_color;
        }).
        text(function(data)
        {
            return data.label;
        }).
        style("opacity", 0).
        transition().
        duration(piechart_animation_duration).
        style("opacity", 1);
    var legend_percentage = pie_chart.selectAll(".legend-percentage").data(buckets);
    legend_percentage.enter().append("text").
        classed("legend-percentage", true).
        attr("width", legend_box_width).
        attr("height", legend_label_height).
        attr("x", legend_box_width + 10).
        attr("y", legend_label_y_func).
        attr("fill", "black").
        style("opacity", 0);
    legend_percentage.
        transition().
        duration(piechart_animation_duration).
        style("opacity", 1).
        tween("text", function(data, i)
        {
            var start_text = (d3.select(this).text() === "")? "0%" : d3.select(this).text();
            var percentage_regex = /^(\d+)%$/;
            var match = percentage_regex.exec(start_text);
            var start_percentage = 0;
            if (match != null && match.length == 2)
            {
                start_percentage = parseInt(match[1]);
            }
            else
            {
                console.log("bro... i'm confused.");
            }
            var target_percentage = 0;
            if (data.interviews)
            {
                target_percentage = (data.interviews.length/total_num_interviews)*100;
            }
            return function(progress)
            {
                this.textContent = Math.round(start_percentage + (target_percentage - start_percentage) * progress).toString() + "%";
            }
        });

    var radius = Math.min(center.x, center.y);
    slices_group.enter().append('path').
        attr('fill', function(bucket)
        {
            return bucket.color;
        }).
        attr('d', "M" + center.x + "," + center.y + " L" + (center.x + radius) + ","  + center.y + " A" + radius + "," + radius + " " + "0 0 1 " + (center.x + radius) + "," + center.y + " z");
    slices_group.transition().
        attrTween('d', function (data, i, start_value)
        {
            var path_d_regex = /^M[^,]*,[^ ]* L([^,]*),([^ ]*) A[^,]*,[^ ]* \d \d 1 ([^,]*),([^ ]*) z$/;
            var match = path_d_regex.exec(start_value);
            var initial_start_percentage = 0;
            var initial_end_percentage = 0;
            if (match != null && match.length == 5)
            {
                var start_coordinate = {"x" : match[1], "y" : match[2]};
                initial_start_percentage = coordinate_to_percentage(start_coordinate, center, radius);
                end_coordinate = {"x" : match[3], "y" : match[4]};
                initial_end_percentage = coordinate_to_percentage(end_coordinate, center, radius);
            }
            else
            {
                initial_start_percentage = 0;
                initial_end_percentage = 1;
                console.log("y u confuse me: " + start_value);
            }
            return function(progress)
            {
                var interviews_already_plotted = 0;
                for (var j = 0; j < i; j++)
                {
                    if (buckets[j].interviews)
                    {
                        interviews_already_plotted += buckets[j].interviews.length;
                    }
                }
                var num_interviews_in_bucket = 0;
                if (data.interviews)
                {
                    num_interviews_in_bucket = data.interviews.length;
                }
                var arc_start_percentage = initial_start_percentage + progress*((interviews_already_plotted/total_num_interviews) - initial_start_percentage);
                var arc_end_percentage = initial_end_percentage + progress*((interviews_already_plotted/total_num_interviews + num_interviews_in_bucket/total_num_interviews) - initial_end_percentage);
                arc_start_percentage = Math.min(.9999, arc_start_percentage);
                arc_end_percentage = Math.min(.9999, arc_end_percentage);
                var start_coordinate = percentage_to_coordinate(arc_start_percentage, center, radius);
                var end_coordinate = percentage_to_coordinate(arc_end_percentage, center, radius);
                var arc_sweep_flags = "0 0";
                if ((arc_end_percentage - arc_start_percentage) >= .5)
                {
                    arc_sweep_flags = "0 1";
                }
                return "M" + center.x + "," + center.y + " " + "L" + start_coordinate.x + ","  + start_coordinate.y + " " + "A" + radius + "," + radius + " " + arc_sweep_flags + " 1 " + end_coordinate.x + "," + end_coordinate.y + " z";
            }
        }).
        duration(piechart_animation_duration);
    slices_group.attr('transform', "rotate(-90 " + center.x + " " + center.y + ")")
    pie_chart.select("#pie-center").
        attr('fill', 'rgb(243, 243, 243)').
        attr('r', radius/2).
        attr('cx', center.x).
        attr('cy', center.y);
    var total_interviews_label = d3.select('#total-interviews-label').
        attr('x', center.x - radius/2).
        attr('y', center.y - radius/2).
        attr('width', radius).
        attr('height', radius);
    var num_interviews_label = d3.select("#num-interviews-label");
    num_interviews_label.data([total_num_interviews]).
        text(function(data)
        {
            return (d3.select(this).text() === "")? "0" : d3.select(this).text();
        }).
        transition().
        tween("text", function(d, i)
        {
            var start_text = (d3.select(this).text() === "")? "0" : d3.select(this).text();
            var start_num = parseInt(start_text);
            return function(progress)
            {
                this.textContent = Math.floor(start_num + progress*(d - start_num)).toString();
            }
        }).
        duration(piechart_animation_duration);
}

function update_interviewer_list(interviewer_array)
{
    var max_num_interviews = -1;
    for (var i = 0; i < interviewer_array.length; i++)
    {
        if (max_num_interviews < interviewer_array[i].interviews.length)
        {
            max_num_interviews = interviewer_array[i].interviews.length;
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
            update_piechart([data]);
        }).
        on("mouseout", function(data)
        {
            d3.select(this).classed("highlighted", false);
            update_piechart(full_interviewer_array);
        }).
        append("div");
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
            var avg_response_time = "<STRONG>N/A</STRONG>";
            if (data.avg_response_time)
            {
                avg_response_time = "<STRONG>" + data.avg_response_time.toString() + "</STRONG> m";
            }
            return avg_response_time;
        });
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
    tableview_cells.exit().remove();

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
            console.log(column + "\t" + i + "\t" + num_interview_dots_per_row + right_padding_per_dot);
            return interview_dot_horizontal_padding + column*right_padding_per_dot + (1 + 2*column)*interview_dot_radius;
        };
        var cy_function = function(data, i)
        {
            var row = Math.floor(i/num_interview_dots_per_row);
            return interview_dot_vertical_padding + row*padding_between_dot_rows + (1 + 2*row)*interview_dot_radius;
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
                        style("margin-left", 166).
                        node().outerHTML).
                    style('top', function(d)
                    {
                        return circle_rect.top - pointer_height - this.getBoundingClientRect().height - popover_bottom_padding;
                    }).
                    style('left', function(d)
                    {
                        return circle_rect.left - this.getBoundingClientRect().width/2 - popover_border_width*2;
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

