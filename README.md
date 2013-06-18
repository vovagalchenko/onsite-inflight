Onsite InFlight
===============
Software for keeping track of onsite interviews in real time. The system is currently deployed at <http://onsite-inflight.com>, though the access to it is restricted. If you need access, talk to Jeff S. from IT here: <jsutton@box.com>

This tool consists of four roughly independent pieces:
    - *Calendar Scanner*: A cron job that scans interviewers' calendars and persists a representation of interview schedules in the MySQL database that's managed by the tool.
    - *SMS sender*: A cron job that periodically looks at the local representation of interview schedules and solicits interviewers who have just finished interviews for scores via SMS.
    - *API*: A set of API endpoints for reading and writing from the managed MySQL database accessible via HTTP.
    - *WebApp*: A web client of the API endpoints that provides a real-time dashboard of the inflight interviews.

Code Organization
=================
The code is currently organized in six directories.
        cron
Contains all code that is executed by cron. In particular, it contains the *calendar scanner* and the *SMS sender*.
        api
Contains all code that is exposed by Apache to provide access to the managed MySQL database. Apache routes all API calls to *process_api_call.py*, which routes request processing to one of *HTTP_Response_Builder* subclasses defined in *api/http_response_builder/*. So far, three API calls are supported:
    - *candidate_list*: retrieve summary information for all candidates interviewing on a given date.
    - *candidate_detail*: retrieve detailed information for a single candidates interview process.
    - *handle_sms*: process receipt of an SMS message from an interviewer (called by Twilio).
    - *post_sso*: consumes SAML 2.0 assertions post SSO authentication.
        model
A collection of classes that simplify access to the managed MySQL database. Leverages SQLAlchemy ORM.
        webapp
Code that defines a client of the API. The *dashboard* HTML file (and the associated css and javascript) is served statically by Apache. AJAX calls are then used to populate templates.
        lib
Bucket for helpers that are used by various components of the system. Examples of such helpers are the *Google Calendar Python SDK* (from Google) and the *send_sms* Twilio API wrapper (by Boris).
        scripts
Place to put various scripts for one off tasks. Currently includes a single script to refresh the list of interviewers the system knows about.
