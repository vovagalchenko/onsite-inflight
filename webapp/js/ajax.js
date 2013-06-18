function make_ajax_request(url, results_process_callback, error_handling_callback)
{
    var request = ajax_request();
    request.onreadystatechange = function()
    {
        if (request.readyState == 4)
        { 
            if (request.status == 200 || window.locationhref.indexOf("http") == -1)
            {
                results_process_callback(request.responseText);
            }
            else
            {
                error_handling_callback();
            }
        }
    }
    request.open("GET", url, true);
    request.send(null);
}
function ajax_request()
{
    var activexmodes=["Msxml2.XMLHTTP", "Microsoft.XMLHTTP"] //activeX versions to check for in IE
    if (window.ActiveXObject) //Test for support for ActiveXObject in IE first (as XMLHttpRequest in IE7 is broken)
    {
        for (var i = 0; i < activexmodes.length; i++)
        {
            try
            {
                return new ActiveXObject(activexmodes[i])
            }
            catch(e)
            {
                alert('Shiiiiit... no AJAX?');
            }
        }
    }
    else if (window.XMLHttpRequest) // if Mozilla, Safari etc
        return new XMLHttpRequest()
    else
        alert('Shiiiiit... no AJAX?');
}
