from flask import Flask, request, render_template
from flaskext.mysql import MySQL
from head_info import HeaderInfo

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
                      client_request, server_request, server_response, client_response FROM header_info''')

    header_list = cursor.fetchall()

    header_dict_list = []
    for header in header_list:
        header_dict = {
            'id': header[0],
            'state_machine_id': header[1],
            'hook_id': header[2],
            'timestamps': header[3],
            'tag': header[4],
            'sequence': header[5],
            'client_request': header[6],
            'server_request': header[7],
            'server_response': header[8],
            'client_response': header[9]
        }
        header_dict_list.append(header_dict)

    return render_template('header_list.html', header_dict_list=header_dict_list)

if __name__ == "__main__":
    app.run(port=9000)
