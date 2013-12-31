from model.db_session import DB_Session_Factory
from model.interview import Interview
from model.interviewer import Interviewer
from datetime import timedelta, datetime, date
from lib.conf import CFG
from Cheetah.Template import Template
import smtplib

def send_email(to_email_address, email_subject, email_body):
    s = smtplib.SMTP('localhost')
    s.sendmail("cron@onsite-inflight.com", to_email_address, 
"""From: Onsite Inflight <cron@onsite-inflight.com>
Content-Type: text/plain; charset=ISO-8859-1
X-Envelope-From: Onsite Inflight <cron@onsite-inflight.com>
To: %s
Subject: %s

%s
""" % (to_email_address, email_subject, email_body))
    s.quit()

db_session = DB_Session_Factory.get_db_session()
week_ago = datetime.now() - timedelta(days = 7)
template = Template(file = CFG.get_instance().get('installation', 'root') + '/data/email_interview_summary.tmpl')
for interviewer_email in db_session.query(Interview.interviewer_email).distinct().filter(Interview.start_time > week_ago, Interview.end_time < date.today()):
    interviewer_email = interviewer_email[0]
    interviewer = db_session.query(Interviewer).get(interviewer_email)
    interview_count = 0
    responded_interview_count = 0
    avg_response_time = 0
    template.interviewer_first_name = interviewer.nickname()
    for interview in interviewer.interviews.filter(Interview.start_time > week_ago, Interview.end_time < date.today()):
        interview_count += 1
        time_to_feedback = interview.time_to_feedback()
        if time_to_feedback != timedelta.max:
            responded_interview_count += 1
            avg_response_time = (avg_response_time*(interview_count-1) + time_to_feedback.total_seconds())/interview_count
    template.num_interviews = interview_count
    template.avg_time_to_feedback = round(avg_response_time/60)
    template.num_interviews_with_feedback = responded_interview_count
    send_email(interviewer_email, "Onsite Interview Stats", str(template))
