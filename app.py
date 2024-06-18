from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from function.utils import *

app = Flask(__name__)
app.secret_key = '021104'
socketio = SocketIO(app)

app.config['USERNAME'] = None

@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template('index.html')

@socketio.on('login')
def login(data):
    user_email = data['email']
    user_password = data['password']

    db = Database(db='basicinformation')
    data_processor = DataProcessing(db)

    statu, name = data_processor.password_matching(table_name="user_data",email=user_email, password=user_password)

    if statu:
        session['name'] = name
        app.config['USERNAME'] = name
        if data_processor.check_avatar_by_email(table_name="user_data", email=user_email) != False:
            emit('login_success', {'username': name})
        else:
            emit('complete_information')
    else:
        emit('login_fail')

@socketio.on('register')
def register(data):
    user_name = data['name']
    user_email = data['email']
    user_password = data['password']

    db = Database(db='basicinformation')
    data_processor = DataProcessing(db)

    if data_processor.check_user_exist(table_name="user_data", email=user_email):
        emit('register_fail')
    else:
        auth_code = generate_auth_code()
        send_registration_email(user_email=user_email, auth_code=auth_code)
        #data_processor.insert_data("user_data", ["name", "email", "password", "auth_code"], (user_name, user_email, user_password, auth_code))
        emit('register_success', {'email': user_email, 'name': user_name, 'authcode': auth_code, 'password': user_password})

@socketio.on('verify')
def verify(data):
    auth_code = data['verifyCode']
    email = data['email']
    name = data['name']
    password = data['password']

    db = Database(db='basicinformation')
    data_processor = DataProcessing(db)

    data_processor.insert_data("user_data", ["name", "email", "password", "auth_code"], (name, email, password, auth_code))

    emit('verify_success')
    

    


@app.route('/complete_information')
def complete_information():
    return render_template('complete_information.html')

@socketio.on('user_information')
def user_information(data):
    db = Database(db='basicinformation')
    data_processor = DataProcessing(db)

    user_name = app.config['USERNAME']
    print(user_name)

    avatar_url = data['avatar']
    gender = data['gender']
    age = data['age']
    location = data['location']
    bio = data['bio']

    data_processor.insert_data_by_name(table_name="user_data", name=user_name, column_values={
        "avatar": avatar_url,
        "gender": gender,
        "age": age,
        "location": location,
        "bio": bio})
    
    # 信息完善成功
    emit('complete_information_success', {'username': user_name})

@app.route('/retrieve_password')
def retrieve_password():
    return render_template('retrieve_password.html')

@socketio.on('get_password')
def get_password(data):
    user_name = data['name']
    user_email = data['email']
    auth_code = data['auth_code']

    db = Database(db='basicinformation')
    data_processor = DataProcessing(db)

    if auth_code == data_processor.get_auth_code_by_name_email(table_name="user_data", name=user_name, email=user_email):
        password = data_processor.get_password_by_name_email(table_name="user_data", name=user_name, email=user_email)
        send_password_email(user_email=user_email, password=password)

        emit('get_password_success')
    else:
        emit('get_password_fail')

@app.route('/chat')
def chat():
    name = request.args.get('name')
    db = Database(db='basicinformation')
    data_processor = DataProcessing(db)
    avatar_url=data_processor.check_avatar_by_name(table_name="user_data", name=name)
    
    return render_template('chat.html', username=name, avatar_url=avatar_url)

@socketio.on('get_room_list')
def get_room_list(data):
    db = Database(db="basicinformation")
    data_processor = DataProcessing(db)

    user_name = data['userName']
    user_email = data_processor.get_user_info_by_name(table_name="user_data",name=user_name)['email']
    create_room_list = data_processor.get_room_info_by_email(table_name="create_room",email=user_email)
    join_room_list = data_processor.get_room_info_by_email(table_name="join_room",email=user_email)

    room_list = []
    if create_room_list is not None:
        for room in create_room_list:
            room_list.append(room)
    if join_room_list is not None:
        for room in join_room_list:
            room_list.append(room)

    if room_list:
        emit('get_room_list_success', {'roomList': room_list})
    else:
        emit('room_list_null')

@socketio.on('create_room')
def create_room(data):
    db = Database(db="basicinformation")
    data_processor = DataProcessing(db)

    db_chat = Database(db="storechatinformation")
    data_processor_chat = DataProcessing(db_chat)

    room_name = data['roomName']
    room_password = data['roomPassword']
    user_name = data['userName']
    user_email = data_processor.get_user_info_by_name(table_name="user_data", name=user_name)['email']
    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    if data_processor.check_room_exist(table_name="create_room", room_name=room_name):
        emit('create_room_fail')
    else:
        data_processor.insert_data("create_room", 
                                    ["room_name", "room_password", "name", "email", "created_at"], 
                                    (room_name, room_password, user_name, user_email, now_time))
        data_processor_chat.create_table(table_name=conversion_table_name(room_name),
                                    columns=[('MessageContent', 'VARCHAR(255)'), ('Sender', 'VARCHAR(255)'), ('Time', 'datetime')])
        emit('create_room_success', {'roomName': room_name})

@socketio.on('delete_room')
def delete_room(data):
    db = Database(db="basicinformation")
    data_processor = DataProcessing(db)

    db_chat = Database(db="storechatinformation")
    data_processor_chat = DataProcessing(db_chat)

    room_name = data['roomName']
    user_name = data['userName']

    if data_processor.check_room_exist(table_name="create_room", room_name=room_name) and data_processor.query_table(table_name="create_room", column_name="room_name", value=room_name)[0][2] == user_name:
        table_name = "create_room"
        if data_processor.check_room_exist(table_name="join_room", room_name=room_name):
            if data_processor_chat.drop_table(table_name=conversion_table_name(room_name)):
                if data_processor.delete_row(table_name=table_name, column_name='room_name', value=room_name):
                    if data_processor.delete_row(table_name="join_room", column_name='room_name', value=room_name):
                        emit('delete_room_success')
            else:
                emit('delete_room_fail')
        else:
            if data_processor_chat.drop_table(table_name=conversion_table_name(room_name)):
                if data_processor.delete_row(table_name=table_name, column_name='room_name', value=room_name):
                    emit('delete_room_success')
            else:
                emit('delete_room_fail')
    else:
        table_name = "join_room"
        if data_processor.delete_row(table_name=table_name, column_name='room_name', value=room_name):
            emit('delete_room_success')
        else:
            emit('delete_room_fail')

@socketio.on('search_room')
def search_room(data):
    db = Database(db="basicinformation")
    data_processor = DataProcessing(db)

    searchText = data['searchText']

    result = data_processor.search_in_table(table_name="create_room", column_name='room_name', search_text=searchText)
    emit('search_result', {'room': result})


@socketio.on('get_room_owner')
def get_room_owner(data):
    db = Database(db="basicinformation")
    data_processor = DataProcessing(db)

    room_name = data['roomName']
    owner_name = data_processor.query_table(table_name="create_room", column_name='room_name', value=room_name)[0][2]
    owner_info = data_processor.get_user_info_by_name(table_name="user_data", name=owner_name)

    emit('get_room_owner_success', {'roomOwner': owner_info})

@socketio.on('join_others')
def join_others(data):
    db = Database(db="basicinformation")
    data_processor = DataProcessing(db)

    room_name = data['roomName']
    room_password = data['roomPassword']
    user_name = data['userName']
    user_email = data_processor.get_user_info_by_name(table_name="user_data", name=user_name)['email']

    if room_password == data_processor.query_table(table_name="create_room", column_name='room_name', value=room_name)[0][1]:
        data_processor.insert_data(table_name="join_room", columns=["room_name", "email","name"], values=(room_name, user_email, user_name))
        emit('join_others_success', {'roomName': room_name})
    else:
        emit('join_others_fail')

@socketio.on('get_chat_history')
def get_history_chat(data):
    db = Database(db="basicinformation")
    data_processor = DataProcessing(db)

    db_chat = Database(db="storechatinformation")
    data_processor_chat = DataProcessing(db_chat)

    room_name = data['roomName']
    user_name = data['userName']

    user_email = data_processor.get_user_info_by_name(table_name="user_data", name=user_name)['email']
    chat_data = data_processor_chat.get_chat_info_by_room(room_name=conversion_table_name(room_name))

    if chat_data is not None:
        for message in chat_data:
            sender_name = data_processor.query_table(table_name='user_data', column_name='email', value=message['Sender'])[0][0]
            if message['Sender'] == user_email:
                
                emit('get_chat_history_success', {'message': message['MessageContent'], 'isUser': 'True', 'sender': sender_name})
            else:
                emit('get_chat_history_success', {'message': message['MessageContent'], 'isUser': 'False', 'sender': sender_name})


@socketio.on('join_current_room')
def join_current_room(data):
    room_name = data['roomName']
    user_name = data['userName']
    join_room(room_name)
    print(rooms(),f'用户{user_name}加入房间{room_name}')
    emit('join_current_room_success')


@socketio.on('leave_previous_room')
def leave_previous_room(data):
    room_name = data['roomName']
    user_name = data['userName']
    leave_room(room_name)
    print(rooms(),f'用户 {user_name} 离开房间{room_name}')
    emit('leave_previous_room_success')

@socketio.on('send_message')
def send_message(data):
    db = Database(db="basicinformation")
    data_processor = DataProcessing(db)

    db_chat = Database(db="storechatinformation")
    data_processor_chat = DataProcessing(db_chat)

    room_name = data['currentRoom']
    user_name = data['userName']
    message = data['message']

    print(f'用户{user_name}发送消息{message}到房间{room_name}')

    user_email = data_processor.get_user_info_by_name(table_name="user_data", name=user_name)['email']
    now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    data_processor_chat.insert_data(table_name=conversion_table_name(room_name), columns=['MessageContent', 'Sender', 'Time'], values=[message, user_email, now_time])

    emit('receive_message', {'message': message, 'isUser': user_name == session.get('name'), 'sender': user_name}, room=room_name)

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000)
    