function need_to_authenticate(data)
{
    if (data["error"] == "authn_needed")
    {   
        var authn_form = document.getElementById("authn_form");
        document.getElementById('saml_response_input').value = data["authn_request"];
        var relay_state = window.location.pathname + window.location.search + window.location.hash;
        document.getElementById('saml_relay_state_input').value = (relay_state == null || relay_state.length == 0)? document.getElementById('saml_relay_state_input').value : relay_state; 
        authn_form.submit();
        return true;
    }   
    return false;
}

function make_ajax_request(url, results_process_callback, error_handling_callback, method)
{
    if (typeof method === "undefined")
    {
        method = "GET";
    }
    var request = ajax_request();
    request.onreadystatechange = function()
    {
        if (request.readyState == 4)
        { 
            if (request.status == 200 || request.status == 403 || window.location.href.indexOf("http") == -1)
            {
                var parsed_data = JSON.parse(request.responseText);
                if (!need_to_authenticate(parsed_data))
                {
                    results_process_callback(parsed_data);
                }
            }
            else if(error_handling_callback != null && request.status > 0)
            {
                error_handling_callback("Request failed.");
            }
        }
    }
    request.open(method, url, true);
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
