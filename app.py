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
    cursor.execute('''INSERT INTO header_info (state_machine_id, hook_id, plugin_name, timestamps, tag, sequence,
                      client_request, server_request, server_response, client_response)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                   (hdr_info.state_machine_id, hdr_info.hook_id, hdr_info.plugin_name,
                    hdr_info.timestamps, hdr_info.tag, hdr_info.sequence, hdr_info.client_request,
                    hdr_info.server_request, hdr_info.server_response, hdr_info.client_response))
    conn.commit()
    return "Done"


@app.route('/', methods=['GET'])
def get_header_list():
    hooks, plugins = get_hook_id_tag_query()

    conn = mysql.connect()
    cursor = conn.cursor()

    execute_sql_based_on_query(hook_list=hooks, plugin_list=plugins, cursor=cursor)
    header_list = cursor.fetchall()

    cursor.execute('''SELECT DISTINCT hook_id
                      FROM header_info
                      WHERE state_machine_id = (SELECT MAX(state_machine_id) FROM header_info)''')
    # transfer tuple of tuple to list
    hook_id_list = [hook[0] for hook in cursor.fetchall()]

    cursor.execute('''SELECT DISTINCT plugin_name
                      FROM header_info
                      WHERE state_machine_id = (SELECT MAX(state_machine_id) FROM header_info)''')
    # transfer tuple of tuple to list
    plugin_list = [plugin[0] for plugin in cursor.fetchall()]

    return render_template('header_list.html', header_dict_list=generate_header_dict_list(header_list=header_list),
                           hook_id_list=hook_id_list, plugin_list=plugin_list)


@app.route('/settings', methods=['GET'])
def debug_setting():
    return render_template('settings.html')


def execute_sql_based_on_query(hook_list, plugin_list, cursor):
    if hook_list[0] == 'ALL_HOOKs' and plugin_list[0] == 'ALL_Plugins':
        sql = '''SELECT id, state_machine_id, hook_id, plugin_name, timestamps, tag, sequence,
                 client_request, server_request, server_response, client_response
                 FROM header_info
                 WHERE state_machine_id = (SELECT MAX(state_machine_id) FROM header_info)
                 ORDER BY state_machine_id DESC, sequence ASC '''
        cursor.execute(sql)
    elif hook_list[0] == 'ALL_HOOKs':
        sql = '''SELECT id, state_machine_id, hook_id, plugin_name, timestamps, tag, sequence,
                 client_request, server_request, server_response, client_response
                 FROM header_info
                 WHERE state_machine_id = (SELECT MAX(state_machine_id) FROM header_info) AND plugin_name IN (%s)
                 ORDER BY state_machine_id DESC, sequence ASC '''
        format_strings = ','.join(['%s'] * len(plugin_list))
        sql %= format_strings
        cursor.execute(sql, tuple(plugin_list))
    elif plugin_list[0] == 'ALL_Plugins':
        sql = '''SELECT id, state_machine_id, hook_id, plugin_name, timestamps, tag, sequence,
                 client_request, server_request, server_response, client_response
                 FROM header_info
                 WHERE state_machine_id = (SELECT MAX(state_machine_id) FROM header_info) AND hook_id IN (%s)
                 ORDER BY state_machine_id DESC, sequence ASC '''
        format_strings = ','.join(['%s'] * len(hook_list))
        sql %= format_strings
        cursor.execute(sql, tuple(hook_list))
    else:
        sql = '''SELECT id, state_machine_id, hook_id, plugin_name, timestamps, tag, sequence,
                 client_request, server_request, server_response, client_response
                 FROM header_info
                 WHERE state_machine_id = (SELECT MAX(state_machine_id) FROM header_info) AND hook_id IN (%s)'''

        format_string1 = ','.join(['%s'] * len(hook_list))
        sql %= format_string1

        sql_part2 = ''' AND plugin_name IN (%s) ORDER BY state_machine_id DESC, sequence ASC '''
        format_string2 = ','.join(['%s'] * len(plugin_list))
        sql_part2 %= format_string2

        sql += sql_part2
        cursor.execute(sql, tuple(hook_list + plugin_list))


def get_hook_id_tag_query():
    # get query parameters
    hooks = request.args.get('hooks')
    hook_list = []
    # if we want to see all hooks, make sure all_hooks is at the beginning of the list
    if hooks is None or hooks.find('ALL_HOOKs') != -1:
        hook_list.append('ALL_HOOKs')
    else:
        hook_list = hooks.split(',')

    plugins = request.args.get('plugins')
    plugin_list = []
    # if we want to see all plugins, make sure all plugins is at the beginning of the list
    if plugins is None or plugins.find('ALL_Plugins') != -1:
        plugin_list.append('ALL_Plugins')
    else:
        plugin_list = plugins.split(',')

    return hook_list, plugin_list


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
        header_dict['plugin_name'] = header[3]
        header_dict['time'] = datetime.datetime.fromtimestamp(header[4])
        header_dict['tag'] = header[5]
        header_dict['sequence'] = header[6]

        # header list
        client_request_hdr = header[7].splitlines()
        server_request_hdr = header[8].splitlines()
        server_response_hdr = header[9].splitlines()
        client_response_hdr = header[10].splitlines()
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
