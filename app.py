from flask import Flask, request, render_template
from flaskext.mysql import MySQL
from head_info import HeaderInfo
import datetime
import difflib

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'plugin_doctor'

mysql.init_app(app)


@app.route('/post_header', methods=['POST'])
def post_header():
    # Get the request data
    hdr_json = request.get_data()
    hdr_info = HeaderInfo(js=hdr_json)

    # Insert into table
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO header_info (state_machine_id, hook_id, timestamps, tag, sequence,
                      client_request, server_request, server_response, client_response)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''', (hdr_info.state_machine_id, hdr_info.hook_id,
                                                                       hdr_info.timestamps, hdr_info.tag,
                                                                       hdr_info.sequence, hdr_info.client_request,
                                                                       hdr_info.server_request, hdr_info.server_response,
                                                                       hdr_info.client_response))
    conn.commit()
    return "Done"


@app.route('/', methods=['GET'])
def get_header_list():
    hook_id, tag = get_hook_id_tag_query()

    conn = mysql.connect()
    cursor = conn.cursor()
    execute_sql_based_on_query(hook_id=hook_id, tag=tag, cursor=cursor)

    header_list = cursor.fetchall()
    return render_template('header_list.html', header_dict_list=generate_header_dict_list(header_list=header_list))


@app.route('/settings', methods=['GET'])
def debug_setting():
    return render_template('settings.html')


def execute_sql_based_on_query(hook_id, tag, cursor):
    if hook_id != 'ALL':
        cursor.execute('''SELECT id, state_machine_id, hook_id, timestamps, tag, sequence,
                          client_request, server_request, server_response, client_response
                          FROM header_info
                          WHERE state_machine_id = (SELECT MAX(state_machine_id) FROM header_info) AND hook_id = %s
                          ORDER BY state_machine_id DESC, sequence ASC ''', hook_id)
    elif tag:
        cursor.execute('''SELECT id, state_machine_id, hook_id, timestamps, tag, sequence,
                          client_request, server_request, server_response, client_response
                          FROM header_info
                          WHERE state_machine_id = (SELECT MAX(state_machine_id) FROM header_info) AND tag = %s
                          ORDER BY state_machine_id DESC, sequence ASC ''', tag)
    else:
        cursor.execute('''SELECT id, state_machine_id, hook_id, timestamps, tag, sequence,
                          client_request, server_request, server_response, client_response
                          FROM header_info
                          WHERE state_machine_id = (SELECT MAX(state_machine_id) FROM header_info)
                          ORDER BY state_machine_id DESC, sequence ASC ''')


def get_hook_id_tag_query():
    valid_hook_id = set(['ALL', 'TS_HTTP_READ_REQUEST_HDR_HOOK', 'TS_HTTP_PRE_REMAP_HOOK',
                         'TS_HTTP_SEND_REQUEST_HDR_HOOK', 'TS_HTTP_READ_RESPONSE_HDR_HOOK',
                         'TS_HTTP_SEND_RESPONSE_HDR_HOOK'])
    valid_tag = set(['Before plugin', 'After plugin'])

    # get query parameters
    hook_id = request.args.get('hook_id')
    if hook_id not in valid_hook_id:
        hook_id = 'ALL'

    tag = request.args.get('tag')
    if tag not in valid_tag:
        tag = None

    return hook_id, tag


def generate_header_dict_list(header_list):
    # return a dict list of every item.
    header_dict_list = []
    # remember the previous header dict, to generate diff
    pre_header_dict = {}

    for header in header_list:

        header_dict = dict()

        header_dict['id'] = header[0]
        header_dict['state_machine_id'] = header[1]
        header_dict['hook_id'] = header[2]
        header_dict['time'] = datetime.datetime.fromtimestamp(header[3])
        header_dict['tag'] = header[4]
        header_dict['sequence'] = header[5]

        # header list
        client_request_hdr = header[6].splitlines()
        server_request_hdr = header[7].splitlines()
        server_response_hdr = header[8].splitlines()
        client_response_hdr = header[9].splitlines()
        header_dict['header_list'] = [{'name': 'Client Request', 'hdr_info': client_request_hdr},
                                      {'name': 'Server Request', 'hdr_info': server_request_hdr},
                                      {'name': 'Server Response', 'hdr_info': server_response_hdr},
                                      {'name': 'Client Response', 'hdr_info': client_response_hdr}]
        # header diff list
        header_dict['header_diff_list'] = generate_header_diff_list(pre_header_dict, header_dict)

        # Got a dict, append to the dict list
        header_dict_list.append(header_dict)

        # Remember the pre header info, used for diff
        pre_header_dict = header_dict

    return header_dict_list


def generate_header_diff_list(pre_header_dict, header_dict):
    # return result list
    header_diff_list = []

    # diff origin data
    client_request_hdr_pre = []
    server_request_hdr_pre = []
    server_response_hdr_pre = []
    client_response_hdr_pre = []

    # based on pre_header_dict, init origin data
    if pre_header_dict and pre_header_dict['state_machine_id'] == header_dict['state_machine_id']:
        client_request_hdr_pre = pre_header_dict['header_list'][0]['hdr_info']
        server_request_hdr_pre = pre_header_dict['header_list'][1]['hdr_info']
        server_response_hdr_pre = pre_header_dict['header_list'][2]['hdr_info']
        client_response_hdr_pre = pre_header_dict['header_list'][3]['hdr_info']

    # header_dict could not be null, get the new data
    client_request_hdr = header_dict['header_list'][0]['hdr_info']
    server_request_hdr = header_dict['header_list'][1]['hdr_info']
    server_response_hdr = header_dict['header_list'][2]['hdr_info']
    client_response_hdr = header_dict['header_list'][3]['hdr_info']

    # generate diff list
    header_diff_list.append({'name': 'Client Request',
                             'hdr_diff': difflib.unified_diff(client_request_hdr_pre, client_request_hdr, lineterm='')})
    header_diff_list.append({'name': 'Server Request',
                             'hdr_diff': difflib.unified_diff(server_request_hdr_pre, server_request_hdr, lineterm='')})
    header_diff_list.append({'name': 'Server Response',
                             'hdr_diff': difflib.unified_diff(server_response_hdr_pre, server_response_hdr, lineterm='')})
    header_diff_list.append({'name': 'Client Response',
                             'hdr_diff': difflib.unified_diff(client_response_hdr_pre, client_response_hdr, lineterm='')})

    return header_diff_list


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9000)
