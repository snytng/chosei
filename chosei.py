# coding: utf-8
from bottle import route, run, request, response, redirect
import random, string
import base64

@route('/')
@route('/new')
@route('/new/<name>')
def new(name = "event_name", comment=""):
    if "comment" in request.query:
        comment = request.query.comment

    response.set_header('Content-Type', 'text/html; charset=utf-8')
    html_header = f"<head><title>chosei new</title></head>"
    html_body = "<body>{}</body>"
    page_header = f"<h1>chosei 新規イベント作成</h1><hr>"
    page_footer = ""

    
    dates = f"""
    2022/11/19 10:00-11:00
    2022/11/20 13:30-14:30
    """
    
    page_body = f"""
    <form method='POST' action='/confirm'>
    イベント名:<br>
    <input type="text" name="name" value="{name}" pattern="[\S]+" placeholder="name"/><br>
    候補日時:<br>
    <textarea name="dates" rows="10" cols="40" value="{dates}" placeholder="input dates"></textarea><br>
    コメント(任意):<br>
    <textarea name="comment" rows="3" cols="40" placeholder="コメント">{comment}</textarea><br>
    <input type='submit' value='新規作成'/>
    </form>
    """

    return html_header + html_body.format(page_header + page_body + page_footer);

@route('/confirm', method="POST")
def do_confirm():
    name = request.forms.name
    comment = request.forms.comment
    dates = request.forms.dates.split("\r\n")
    dates = [s for s in dates if s.strip() != ''] # 空白は除去

    message =""
    submit_type = "submit"

    if len(dates) == 0:
        message="候補日時を１つ以上入力してください"
        submit_type = "hidden"


    response.set_header('Content-Type', 'text/html; charset=utf-8')
    html_header = f"<head><title>chosei new</title></head>"
    html_body = "<body>{}</body>"
    page_header = f"<h1>chosei 新規イベント作成 確認</h1><font color='red'>{message}</font><hr>"
    page_footer = ""

    page_body = f"""
    <form method='POST' action='/new'>
    イベント名:<br>
    <input type="text" name="name" value="{name}" readonly/><br>
    候補日時:<br>
    <textarea name="dates" rows="10" cols="40" readonly>{request.forms.dates}</textarea>
    <br>
    コメント:<br>
    <textarea name="comment" rows="3" cols="40" readonly>{comment}</textarea><br>
    <input type='{submit_type}' value='新規作成'/>
    <button type="button" onclick="history.back()">戻る</button>
    </form>
    """

    return html_header + html_body.format(page_header + page_body + page_footer);

@route('/new', method="POST")
def do_new():
    name = request.forms.name
    comment = request.forms.comment
    dates = request.forms.dates.split("\r\n")
    dates = [s for s in dates if s.strip() != ''] # 空白を除去

    choseiId = randomname(10)
    db_create(choseiId, name, dates, comment)

    return redirect(f"/get/{choseiId}")

@route('/get/<choseiId>')
def get(choseiId):
    (name, comment, n, dates, users) = get_data(choseiId)

    response.set_header('Content-Type', 'text/html; charset=utf-8')
    html_header = f"<head><title>chosei {name}</title></head>"
    html_body = "<body>{}</body>"

    (scheme, host, path, query_string, fragment) = request.urlparts
    geturl = f"{scheme}://{host}/get/{choseiId}";
    page_header = f"""
    <h1>chosei {name}</h1>
    コメント: <table boarder='1'><tr><td><pre>{comment}</pre></td></tr></table><br>
    リンク: <a href="{geturl}">{geturl}</a>
    <hr>"""
    page_footer = "<hr><a href='/new'>新規イベント作成</a>"

    page_table = get_table(choseiId)
    page_input = ""

    page_body = page_table + page_input

    return html_header + html_body.format(page_header + page_body + page_footer);

@route('/add/<choseiId>')
def add(choseiId):
    (name, comment, n, dates, users) = get_data(choseiId)
    userId = int(len(users))
    return redirect(f"/add/{choseiId}/{userId}")

@route('/add/<choseiId>/<userId>')
def add_userId(choseiId, userId):
    (name, comment, n, dates, users) = get_data(choseiId)

    response.set_header('Content-Type', 'text/html; charset=utf-8')
    html_header = f"<head><title>chosei {name}</title></head>"
    html_body = "<body>{}</body>"

    (scheme, host, path, query_string, fragment) = request.urlparts
    geturl = f"{scheme}://{host}/get/{choseiId}";
    page_header = f"""
    <h1>chosei {name}</h1>
    コメント: <table boarder='1'><tr><td><pre>{comment}</pre></td></tr></table><br>
    リンク: <a href="{geturl}">{geturl}</a>
    <hr>"""

    page_footer = "<hr><a href='/new'>新規イベント作成</a>"

    (name, comment, n, dates, users) = get_data(choseiId)
    uid = int(userId)

    submit_value = "更新"
    if uid >= len(users):
        users.append(["新規ユーザー"] + ["2"]*n + [""])
        submit_value = "追加"

    page_form  = f"<form method='POST' action='/add/{choseiId}/{userId}'>"
    page_form  += f"""
    ユーザー名:<br>
    <input type="text" name="user_name" value="{users[uid][0]}"pattern="[\S]+"/>（空白なし）<br>
    """
    page_form  += "<table border='1' cellpadding='15'>"
    page_form  += """
    <tr bgcolor='#ddeeee' align='center'>
    <th>候補日時</th><th>○</th><th>△</th><th>✕</th>
    </tr>"""
    for (i, date) in enumerate(dates):
        checked0 = "checked" if users[uid][i+1] == "0" else ""
        checked1 = "checked" if users[uid][i+1] == "1" else ""
        checked2 = "checked" if users[uid][i+1] == "2" else ""
        page_form += f"""
        <tr>
        <td>{date}</td>
        <td><input type="radio" name="date{i}" value="0" {checked0}/></td>
        <td><input type="radio" name="date{i}" value="1" {checked1}/></td>
        <td><input type="radio" name="date{i}" value="2" {checked2}/></td>
        </tr>
        """
    page_form  += "</table>"

    page_form += f"""
    コメント:<br>
    <textarea name="user_comment" rows="5" cols="40">{users[uid][n+1]}</textarea><br>
    <input type="submit" value="{submit_value}"/>
    """
    page_form  += "</form>"
    page_input = ""

    page_body = page_form + page_input

    return html_header + html_body.format(page_header + page_body + page_footer);

@route('/add/<choseiId>/<userId>', method="POST")
def do_add(choseiId, userId):
    (name, comment, n, dates, users) = get_data(choseiId)

    user = [request.forms.user_name]
    for i in range(n):
        dateN = f"date{i}"
        user.append(request.forms[dateN])
    user.append(request.forms.user_comment)

    db_add(choseiId, userId, user)

    return redirect(f"/get/{choseiId}")


# -----
def get_data(choseiId):
    lines = db_load(choseiId)

    name = lines[0]
    encoded_comment = lines[1]
    comment = base64.b64decode(encoded_comment).decode()
    n = int(lines[2])
    dates = lines[3:(n+3)]
    users = [s.split("\t") for s in lines[(n+3):]]
    for user in users:
        encoded_user_comment = user[n+1]
        user[n+1] = base64.b64decode(encoded_user_comment).decode()

    return (name, comment, n, dates, users)

def get_table(choseiId):
    (name, comment, n, dates, users) = get_data(choseiId)

    # table summery
    summery = []
    for (i, date) in enumerate(dates):
        dsummery= [0]*3
        for user in users:
            dsummery[int(user[i+1])] = dsummery[int(user[i+1])] + 1
        summery.append(dsummery)

    # table
    page_table = "<table border='1' cellpadding='15'>"
    # table header
    tr = "<tr bgcolor='#ddeeee' align='center'>"
    tr += "<th>日時</th>"
    tr += "<th bgcolor='#f0eeee'>○</th>"
    tr += "<th bgcolor='#f0eeee'>△</th>"
    tr += "<th bgcolor='#f0eeee'>✕</th>"
    for (i, user) in enumerate(users):
        tr += "<th>"
        tr += f"<a href='/add/{choseiId}/{i}'>{user[0]}</a>" # name
        tr += "</th>"
    tr += f"<th><a href='/add/{choseiId}'>追加</a></th>"
    tr += "</tr>"
    page_table += tr

    # table body dates
    for i in range(n):
        bgcolor = "#ffffff"
        if summery[i][0] == len(users):
            bgcolor = "#ffd0d0"
        elif summery[i][0] >= summery[i][1] and summery[i][2] == 0:
            bgcolor = "#ffe0e0"
        elif summery[i][0] >= 0 and summery[i][2] == 0:
            bgcolor = "#fff5f5"


        tr = f"<tr bgcolor='{bgcolor}' align='center'>"
        # date
        tr += f"<td>{dates[i]}</td>"

        # summery
        for s in summery[i]:
            tr += f"<td>{s}</td>"

        #users
        for user in users:
            userdate = "✕"
            if user[i+1] == "0":
                userdate = "○"
            elif user[i+1] == "1":
                userdate = "△"
            tr += f"<td>{userdate}</td>" # response
        tr += "</tr>"

        page_table += tr

    # table body comment
    tr = "<tr align='left'>"
    tr += "<td bgcolor='#ddddee'>コメント</td>"
    tr += "<td></td>"
    tr += "<td></td>"
    tr += "<td></td>"
    for user in users:
        tr += f"<td width='80'><pre>{user[n+1]}</pre></td>" # comment
    tr += "</tr>"
    page_table += tr

    page_table += "</table>"

    return page_table

def db_create(choseiId, name, dates=[], comment=""):
    encoded_comment = base64.b64encode(request.forms.comment.encode()).decode()

    with open(f"./data/{choseiId}.txt", mode="w", encoding="utf8", newline='\r\n') as f:
        f.write(name+ "\n")
        f.write(encoded_comment+ "\n")
        f.write(str(len(dates)) + "\n")
        for date in dates:
            f.write(date + "\n")

def db_load(choseiId):
    with open(f"./data/{choseiId}.txt", mode="r", encoding="utf8") as f:
        lines = f.readlines()
    return [line.rstrip("\n") for line in lines]

def db_add(choseiId, userId, user):
    (name, comment, n, dates, users) = get_data(choseiId)
    encoded_comment = base64.b64encode(request.forms.comment.encode()).decode()

    uid = int(userId)
    if uid >= len(users):
        users.append(user)
    else:
        users[uid] = user

    with open(f"./data/{choseiId}.txt", mode="w", encoding="utf8", newline='\r\n') as f:
        f.write(name+ "\n")
        f.write(encoded_comment+ "\n")
        f.write(str(len(dates)) + "\n")
        for date in dates:
            f.write(date + "\n")
        for user in users:
            encoded_user_comment = base64.b64encode(user[n+1].encode()).decode()
            user[n+1] = encoded_user_comment
            f.write("\t".join(user) + "\n")

def randomname(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

# -----
if __name__ == "__main__":
    run(host='localhost', port=18101, debug=True, reloader=True)
