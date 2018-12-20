# from calendar_rest_flask_help import Appointment, Calendar, AppointmentList
from flask import Flask, jsonify, make_response, request

# !/usr/bin/env python2

"""
Sample code for the "RESTful Calendar Service in Flask" assignment.
"""

__author__ = 'Maarten Wijnants'

import json  # https://docs.python.org/2/library/json.html
import \
    xml.etree.ElementTree as ET  # https://docs.python.org/2.7/library/xml.etree.elementtree.html#module-xml.etree.ElementTree
from datetime import datetime

###############################################################################
# Constants
###############################################################################

ID_RANGE_LOWER = 0
ID_RANGE_UPPER = 9999

FORMAT_JSON = 'json'
FORMAT_XML = 'xml'

XML_ROOT_TAG_APPOINTMENT = 'Appointment'
XML_ROOT_TAG_APPOINTMENT_LIST = 'Appointments'

PRINT_DEBUG_OUTPUT = True


###############################################################################
# Class definitions
###############################################################################

class Appointment:
    def __init__(self,
                 id=None,
                 title='',
                 location='',
                 description='',
                 start=None, stop=None):
        """id must be of type String (i.e., NOT a number).

        :type id: str
        :type title: str
        :type description: str
        :type start: datetime
        :type stop: datetime
        """

        self.id = id
        self.title = title
        self.location = location
        self.description = description
        self.start = start
        self.stop = stop

    def to_json(self):
        """Converts the appointment to a JSON representation.

        :rtype: str
        """

        return json.dumps(self.__dict__, default=json_serializer_custom)

    def to_xml(self):
        """Converts the appointment to an XML representation.

        :rtype: str
        """

        root = ET.Element(XML_ROOT_TAG_APPOINTMENT)
        for key, value in self.__dict__.items():
            tag = ET.SubElement(root, key)
            if key == 'start' or key == 'stop':
                try:
                    tag.text = json_serializer_custom(value)
                except Exception as e:
                    # Leave tag text empty in case datetime serialization
                    # fails (which is likely to indicate a "None" datetime
                    # value)
                    pass
            else:
                tag.text = value
        return ET.tostring(root)

    def from_json(self, str_json):
        """Instantiates an appointment from a JSON representation.

        :type str_json: str
        """

        self = json.loads(str_json, object_hook=self.__dict_to_appointment)
        return

    def from_xml(self, str_xml):
        """Instantiates an appointment from an XML representation.

        :type str_xml: str
        """
        root = ET.fromstring(str_xml)

        dict = {}
        for child in root:
            dict[child.tag] = child.text
        self.__dict_to_appointment(dict)
        return

    def __dict_to_appointment(self, dict):
        self.id = dict['id'] if ('id' in dict) else None
        self.title = dict['title'] if ('title' in dict) else ''
        self.location = dict['location'] if ('location' in dict) else ''
        self.description = dict['description'] if ('description' in dict) else ''
        self.start = dict['start'] if ('start' in dict) else None
        self.stop = dict['stop'] if ('stop' in dict) else None

        try:
            self.start = json_deserializer_datetime_utc(self.start, trim_quotes=False)
        except (ValueError, AttributeError, IndexError) as e:
            print('WARNING: Could not convert JSON-serialized \"start\" string %s to a Python datetime instance: %s' % (
                self.start, e))
        try:
            self.stop = json_deserializer_datetime_utc(self.stop, trim_quotes=False)
        except (ValueError, AttributeError, IndexError) as e:
            print('WARNING: Could not convert JSON-serialized \"stop\" string %s to a Python datetime instance: %s' % (
                self.stop, e))


class AppointmentList:
    def __init__(self):
        pass

    @staticmethod
    def to_json(list_appointments):
        """Converts a list of appointments to a JSON representation.

        :rtype: str
        """

        str_json = '[ '
        for appointment in list_appointments:
            str_json += appointment.to_json()
            str_json += ', '
        if len(str_json) > 2:
            str_json = str_json[:-2]  # drop trailing ', '
        str_json += ' ]'

        return str_json

    @staticmethod
    def to_xml(list_appointments):
        """Converts a list of appointments to an XML representation.

        :rtype: str
        """

        str_xml = '<' + XML_ROOT_TAG_APPOINTMENT_LIST + '>'
        # FIXME: TODO: Insert newline here?
        for appointment in list_appointments:
            str_xml += appointment.to_xml()
            # FIXME: TODO: Insert newline here?
        str_xml += '</' + XML_ROOT_TAG_APPOINTMENT_LIST + '>'

        return str_xml


class Calendar:
    def __init__(self):
        self.__dict_appointments = {}

    def add_appointment(self, id, appointment):
        """Returns the inserted appointment upon success, or None if an
        appointment with the specified id already exists."""

        appointment_new = None

        if not (self.__id_appointment_exists(id)):
            appointment_new = appointment
            self.__dict_appointments[id] = appointment

        return appointment_new

    def delete_appointment(self, id):
        """Returns the deleted appointment upon success, or None if no
        such appointment exists."""

        appointment = None

        if self.__id_appointment_exists(id):
            appointment = self.__dict_appointments[id]
            del self.__dict_appointments[id]

        return appointment

    def get_appointment(self, id):
        """Returns the appointment with the specified id, or None if no
        such appointment exists."""
        print(len(self.__dict_appointments))
        return self.__dict_appointments[id] if (self.__id_appointment_exists(id)) else None

    def update_appointment(self, id, appointment):
        """Returns the old version of the appointment upon success, or
        None if no such appointment exists."""

        appointment_old = None

        if self.__id_appointment_exists(id):
            appointment_old = self.__dict_appointments[id]
            self.__dict_appointments[id] = appointment

        return appointment_old

    def get_appointments_in_time_range(self, start, stop):
        """Returns a list with all appointments whose starting datetime
        lie within the specified (inclusive) time interval."""

        list_appointments = []

        for id in self.__dict_appointments:
            appointment = self.__dict_appointments[id]

            if datetimes_are_equal(appointment.start, start) or appointment.start > start:
                if appointment.start < stop:
                    list_appointments.append(appointment)

        return list_appointments

    def __id_appointment_exists(self, id):
        return (id in self.__dict_appointments)


class UnsupportedFormatException(Exception):
    pass


###############################################################################
# Ancillary methods
###############################################################################

def debug(str):
    if PRINT_DEBUG_OUTPUT:
        print('DBG: %s' % str)


def id_to_formatted_string(id):
    return ('%04d' % (id,))


def id_generate():
    """Generates and returns a (unique) integer-based Appointment ID."""
    global id_gen_appointment

    id = id_gen_appointment

    id_gen_appointment += 1
    if (id_gen_appointment > ID_RANGE_UPPER):
        id_gen_appointment = ID_RANGE_LOWER

    return id


def id_generate_as_formatted_string():
    """Generates and returns a (unique) string-based Appointment ID."""
    return id_to_formatted_string(id_generate())


def json_serializer_custom(x):
    """JSON serializer for objects not serializable by Python json module
    by default.

    In particular, this function converts Python datetime instances to a
    RFC3339-compliant representation, excluding fractional seconds time
    information. Note that such datetime representations are also useful
    when using XML as representation format."""

    if isinstance(x, datetime):
        str = x.isoformat()
        str_tz = ''

        #        # Strip and record timezone metadata from string representation
        #        if x.utcoffset is None:
        #            str_tz = 'Z'
        #        else:
        #            str_tz = str[-6:]
        #            str = str[:-6]
        # NOTE: "naive" Python datetime objects are timezone-agnostic (see
        #       https://docs.python.org/3/library/datetime.html#module-datetime),
        #       so simply assume UTC time here.
        str_tz = 'Z'

        # Trim away sub-second precision
        if x.microsecond != 0:
            str = str[:-7]

        return (str + str_tz)

    raise TypeError('Type "%s" is not serializable' % type(x))


def json_deserializer_datetime_utc(str_json, trim_quotes=True):
    """Parser for Python datetime instances that have been serialized
    by the json_serializer_custom function. Will return a datetime
    instance upon success, and will raise a ValueError, AttributeError
    or IndexError exception on error."""

    debug('datetime_utc string = \"%s\"' % str_json)

    # Trim enclosing quotes; could raise an IndexError
    if trim_quotes:
        str_json = str_json[1:-1]
    # Replace T delimiter by a whitespace to facilitate parsing
    str_json = str_json.replace('T', ' ', 1)
    # Trim UTC timezone suffix (i.e., 'Z')
    str_json = str_json[:-1]
    return datetime.strptime(str_json, '%Y-%m-%d %H:%M:%S')


def deserialize_appointment_from_http_payload(format, payload, generate_id=True):
    """Raises an UnsupportedFormatException in case the specified payload
    format (e.g., JSON, XML) is not recognized. Can raise numerous other
    types of exceptions in case of deserialization issues."""

    appointment = Appointment()

    # Populate Appointment instance with payload data
    if (format == FORMAT_JSON):
        appointment.from_json(payload)
    elif (format == FORMAT_XML):
        appointment.from_xml(payload)
    else:
        raise UnsupportedFormatException()

    # Set appointment ID
    if generate_id:
        appointment.id = id_generate_as_formatted_string()

    return appointment


def datetimes_are_equal(x, y):
    return (not (x < y) and not (y < x))


###############################################################################
# Global variables
###############################################################################

id_gen_appointment = ID_RANGE_LOWER

app = Flask(__name__)

calendar = Calendar()


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# http://127.0.0.1:5000/appointments/
@app.route('/appointments/',
           methods=['POST'])
def create_appointment():
    if len(request.args) < 1 or request.args['format'] == u'json':
        new_json_appo = deserialize_appointment_from_http_payload(
            format=FORMAT_JSON,
            payload=request.data)
        new_json_appo.to_json()
        calendar.add_appointment(new_json_appo.id, new_json_appo)
        return jsonify({'id': new_json_appo.id}), 201
    elif request.args['format'] == u'xml':
        new_xml_appo = deserialize_appointment_from_http_payload(
            format=FORMAT_XML,
            payload=request.data)
        new_xml_appo.to_xml()
        calendar.add_appointment(new_xml_appo.id, new_xml_appo)
        response = make_response("<id>" + new_xml_appo.id + "</id>")
        response.mimetype = 'application/xml'
        response.status_code = 201
        return response


# http://127.0.0.1:5000/appointments/0003
@app.route('/appointments/<appointment_id>/', methods=['GET'])
def get_appointment_by_id(appointment_id):
    appo = calendar.get_appointment(appointment_id)

    if appo is not None:
        if len(request.args) < 1 or request.args['format'] == u'json':
            return appo.to_json()
        elif request.args['format'] == u'xml':
            return appo.to_xml()
    else:
        return make_response(jsonify({'error': 'No record found of this id.'}), 404)


# http://127.0.0.1:5000/appointments?start=2018-12-09 10:00:00&stop=2018-12-09 12:00:00&format=json
@app.route('/appointments', methods=['GET'])
def get_appointment_by_timerange():
    if len(request.args) > 0:
        appointments = []
        start = json_deserializer_datetime_utc(request.args['start'], False)
        stop = json_deserializer_datetime_utc(request.args['stop'], False)
        appointments = calendar.get_appointments_in_time_range(start=start, stop=stop)
        if len(appointments) > 0:
            if len(request.args) < 1 or request.args['format'] == u'json':
                return AppointmentList.to_json(appointments)
            elif request.args['format'] == u'xml':
                return AppointmentList.to_xml(appointments)
        else:
            # beter een 200 een lege array terug steuren
            return make_response(jsonify({'error': 'No record found in this timerange.'}), 404)


# http://127.0.0.1:5000/appointments/0002/
@app.route('/appointments/<appointment_id>/', methods=['DELETE'])
def delete_appointment(appointment_id):
    deleted_apo = calendar.delete_appointment(id=appointment_id)
    if deleted_apo is not None:
        response = make_response()
        response.status_code = 204  # The server has fulfilled the request but does not need to return an entity-body.
        return response
    else:
        return make_response(jsonify({'error': 'No record found of this id.'}), 404)


# http://127.0.0.1:5000/appointments/0003/?format=xml
@app.route('/appointments/<appointment_id>/', methods=['PUT'])
def update_task(appointment_id):
    if len(request.args) < 1 or request.args['format'] == u'json':
        edited_appointment = deserialize_appointment_from_http_payload(
            format=FORMAT_JSON,
            payload=request.data)
    elif request.args['format'] == u'xml':
        edited_appointment = deserialize_appointment_from_http_payload(
            format=FORMAT_XML,
            payload=request.data)
    appo = calendar.update_appointment(appointment_id, edited_appointment)
    if appo is not None:
        response = make_response()
        response.status_code = 204  # The server has fulfilled the request but does not need to return an entity-body.
        return response
    else:
        return make_response(jsonify({'error': 'No record found of this id.'}), 404)


if __name__ == '__main__':
    app.run(debug=True)

# test data
# <appointment>
# 	<description>Need to find a good yoga tutorial on the web</description>
# 	<start>2018-12-09 10:00:00</start>
# 	<stop>2018-12-09 11:00:00</stop>
# 	<title>Learn yoga</title>
# </appointment>
#
# {
#     "description": "Need to find a good yoga tutorial on the web",
#     "start": "2018-12-09 10:00:00",
#     "stop": "2018-12-09 11:00:00",
#     "title": "Learn yoga"
#   }
