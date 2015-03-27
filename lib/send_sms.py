from model.interview import Interview
from twilio.rest import TwilioRestClient
from logger import log_outgoing_sms
from conf import CFG
 
cfg = CFG.get_instance()
account_sid = cfg.get('twilio', 'account_sid')
auth_token = cfg.get('twilio', 'auth_token')

def send_initial_request_for_scores(interview):
    interviewer = interview.interviewer
    if interviewer.does_interviews == 1:
        basePhoneNumber = interviewer.phone_number
        targetNumber = "+1" + basePhoneNumber
#    if targetNumber != '+18185194891' and targetNumber != '+14089126890' and targetNumber != '+16504250156' and targetNumber != '6506468732':
#        targetNumber = '+18185194891'
        initialScoreType = 'cultural' if interview.is_coffee_break() else 'technical'
        message = ''.join(["Hi ", interviewer.nickname(), "! What's the ", initialScoreType, " score for ", interview.candidate_name, "?"])
        send_sms("+1" + interview.phone_number_to_use, targetNumber, message)

def send_sms(from_number, to_number, message):
    log_outgoing_sms(to_number, message)
    client = TwilioRestClient(account_sid, auth_token)
    client.sms.messages.create(to=to_number, from_=from_number, body=message)
