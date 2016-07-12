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
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('''SELECT id, state_machine_id, hook_id, timestamps, tag, sequence,
                      client_request, server_request, server_response, client_response FROM header_info
                      ORDER BY state_machine_id DESC, sequence ASC ''')

    header_list = cursor.fetchall()

    return render_template('header_list.html', header_dict_list=generate_header_dict_list(header_list=header_list))


def generate_header_dict_list(header_list):
    # return a dict list of every item.
    header_dict_list = []

    client_request_hdr_pre = []
    server_request_hdr_pre = []
    server_response_hdr_pre = []
    client_response_hdr_pre = []

    for header in header_list:
        client_request_hdr = header[6].splitlines()
        server_request_hdr = header[7].splitlines()
        server_response_hdr = header[8].splitlines()
        client_response_hdr = header[9].splitlines()
        header_dict = {
            'id': header[0],
            'state_machine_id': header[1],
            'hook_id': header[2],
            'time': datetime.datetime.fromtimestamp(header[3]),
            'tag': header[4],
            'sequence': header[5],
            'header_list': [{'name': 'Client Request', 'hdr_info': client_request_hdr},
                            {'name': 'Server Request', 'hdr_info': server_request_hdr},
                            {'name': 'Server Response', 'hdr_info': server_response_hdr},
                            {'name': 'Client Response', 'hdr_info': client_response_hdr}],
            'header_diff_list': [
                            {'name': 'Client Request',
                             'hdr_diff': difflib.unified_diff(client_request_hdr_pre, client_request_hdr, lineterm='')},
                            {'name': 'Server Request',
                             'hdr_diff': difflib.unified_diff(server_request_hdr_pre, server_request_hdr, lineterm='')},
                            {'name': 'Server Response',
                             'hdr_diff': difflib.unified_diff(server_response_hdr_pre, server_response_hdr, lineterm='')},
                            {'name': 'Client Response',
                             'hdr_diff': difflib.unified_diff(client_response_hdr_pre, client_response_hdr, lineterm='')}],

        }

        # Get a dict, append to the dict list
        header_dict_list.append(header_dict)

        # Remember the pre header info, used for diff
        client_request_hdr_pre = client_request_hdr
        server_request_hdr_pre = server_request_hdr
        server_response_hdr_pre = server_response_hdr
        client_response_hdr_pre = client_response_hdr

    return header_dict_list

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9000)
