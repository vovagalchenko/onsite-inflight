from model.interview import Interview
from twilio.rest import TwilioRestClient
from logger import log_outgoing_sms
 
# The session object makes use of a secret key.
account_sid = "AC7ff9fa3ed7b9477f96f5a113ff8bb18c"
auth_token = "92910305d42bd12e61cb987defcc4fbd"

def send_initial_request_for_scores(interview):
    interviewer = interview.interviewer

    basePhoneNumber = interviewer.phone_number
    targetNumber = "+1" + basePhoneNumber
#    if targetNumber != '+18185194891' and targetNumber != '+14089126890' and targetNumber != '+16504250156' and targetNumber != '6506468732':
#        targetNumber = '+18185194891'
    initialScoreType = 'cultural' if interview.is_coffee_break() else 'technical'
    message = ''.join(["Hi ", interviewer.nickname(), "! What's the ", initialScoreType, " score for ", interview.candidate_name, "?"])
    log_outgoing_sms(targetNumber, message)
    client = TwilioRestClient(account_sid, auth_token)
    client.sms.messages.create(to=targetNumber, from_="+14089403233", body=message)
