from datetime import datetime
import base64
import xml.etree.ElementTree as ET

class Parameter_Type(object):
    @classmethod
    def get_value_from_raw(cls, raw_value):
        raise NotImplementedError, 'Must override get_value_from_raw'

class String_Parameter_Type(Parameter_Type):
    @classmethod
    def get_value_from_raw(cls, raw_value):
        return raw_value

class Base_64_Encoded_String_Parameter_Type(Parameter_Type):
    @classmethod
    def get_value_from_raw(cls, raw_value):
        return base64.b64decode(raw_value)

class Base_64_Encoded_XML_Parameter_Type(Base_64_Encoded_String_Parameter_Type):
    @classmethod
    def get_value_from_raw(cls, raw_value):
        decoded_string = super(Base_64_Encoded_XML_Parameter_Type, cls).get_value_from_raw(raw_value)
        return ET.fromstring(decoded_string)

class Date_Time_Parameter_Type(Parameter_Type):
    @classmethod
    def get_value_from_raw(cls, raw_value):
        return datetime.fromtimestamp(float(raw_value))

class Boolean_Parameter_Type(object):
    @classmethod
    def get_value_from_raw(cls, raw_value):
        ret_value = None
        if raw_value == 'true':
            ret_value = True
        elif raw_value == 'false':
            ret_value = False
        else:
            raise ValueError, "Only \"true\" and \"false\" are acceptable values for a boolean. You passed in " + raw_value
        return ret_value

class Parameter(object):
    name = None
    default = None
    required = False
    parameter_type = Parameter_Type
    
    def __init__(self, name = None, default = None, required = True, parameter_type = String_Parameter_Type):
        self.name = name
        if self.name is None:
            raise ValueError, "Must pass in name when creating a parameter definition"
        self.default = default
        self.required = required
        self.parameter_type = parameter_type

    def get_value(self, passed_in_value):
        param_value = self.default
        if passed_in_value is not None:
            param_value = self.parameter_type.get_value_from_raw(passed_in_value)
        if self.required is True and param_value is None:
            raise ValueError, self.name + " is a required parameter"
        return param_value
