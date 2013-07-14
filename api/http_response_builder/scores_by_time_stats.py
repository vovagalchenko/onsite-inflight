from http_response_builder import HTTP_Response_Builder
from param_definition.parameter import Parameter, Date_Time_Parameter_Type, Boolean_Parameter_Type
from datetime import datetime, timedelta

from model.db_session import DB_Session_Factory
from model.interview import Interview
from model.interviewer import Interviewer
from sqlalchemy import func
import json

class Scores_By_Time_Stats_HTTP_Response_Builder(HTTP_Response_Builder):
    requires_authn = False
    earliest_ts = Parameter('earliest_ts', required = False, default = datetime.now() - timedelta(days=30), parameter_type = Date_Time_Parameter_Type)
    latest_ts = Parameter('latest_ts', required = False, default = datetime.now(), parameter_type = Date_Time_Parameter_Type)
    days = {
        1 : 'Sun',
        2 : 'Mon',
        3 : 'Tue',
        4 : 'Wed',
        5 : 'Thu',
        6 : 'Fri',
        7 : 'Sat'
    }
    

    def print_body(self):
        stats = []
        for stats_for_hour in DB_Session_Factory.get_db_session().query(func.dayofweek(Interview.end_time), func.hour(Interview.end_time), func.avg(Interview.technical_score), func.avg(Interview.cultural_score), func.count(1)).group_by(func.dayofweek(Interview.end_time), func.hour(Interview.end_time)).filter(Interview.start_time > self.earliest_ts, Interview.end_time < self.latest_ts):
            stats.append({
                'Day' : self.days[stats_for_hour[0]],
                'Hour' : stats_for_hour[1],
                'Avg_Technical_Score' : stats_for_hour[2],
                'Avg_Cultural_Score' : stats_for_hour[3],
                'Sample_Size' : stats_for_hour[4],
            })
        print json.dumps(stats)
