function Color(hue, saturation, luminance, opacity)
{
    this.hue = hue;
    this.saturation = saturation;
    this.luminance = luminance;
    this.opacity = opacity === null ? opacity :  1.0;
}

Color.prototype.get_css = function()
{
    return "hsl(" + this.hue.toString() + "," + this.saturation.toString() + "%," + this.luminance + "%)";
}

function get_colors(num_colors)
{
    var base_hue = 190;
    var base_color = new Color(base_hue, 100, 50);
    var hue_step = (240.0/num_colors);
    var colors = [base_color];
    for (var i = 1; i < num_colors; i++)
    {
        var new_color = new Color(0, base_color.saturation, base_color.luminance);
        new_color.hue = (base_hue + hue_step*i)%240;
        colors.push(new_color);
    }
    return shuffle(colors);
}

function shuffle(o){
    for(var j, x, i = o.length; i; j = Math.floor(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x);
    return o;
};
