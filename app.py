# coding: utf-8
from bottle import route, run, request, response, redirect, static_file, template
import random, string
import base64

@route('/images/<filename>')
def images(filename):
    return static_file(filename, "./images")

@route('/')
def root():
    return redirect("/index.html")
    
@route('/index.html')
def index():
    return template("index")

@route('/new')
@route('/new/<name>')
def new(name="", comment="", dates=""):
    if name == "":
        if "name" in request.query:
            name = request.query.name
        else:
            name = "〇〇会議/□□懇親会/△△激励会"

    if comment == "" and "comment" in request.query:
        comment = request.query.comment

    if dates == "" and dates in request.query:
        dates = request.query.dates
    else:
        dates = f"""
2022/11/19（土） 10:00-11:00
2022/11/20（日） 12:30-13:30
2022/11/21（月） 14:00-15:30
2022/11/22（火） 16:30-17:00
2022/11/23（水） 09:00-09:30
2022/11/24（木） 09:30-11:30
2022/11/25（金） 17:30-18:30"""

    return template("new", name=name, comment=comment, dates=dates)

@route('/new_confirm', method="POST")
def do_new_confirm():
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
    html_header = f"""
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html>
    <head>
    <title>chosei new</title>
    <style>
    .readonly{{
        background: #EEE;
    }}
    </style>
    </head>"""
    html_body = "<body>{}</body>"
    html_footer = f"</html>"
    page_header = f"<h1>chosei 新規イベント作成 確認</h1><font color='red'>{message}</font><hr>"
    page_footer = ""

    page_body = f"""
    <h2>この内容で新規イベントを作成していいですか？</h2>
    <form method='POST' action='/new'>
    イベント名:<br>
    <input type="text" name="name" value="{name}" class="readonly" readonly/><br>
    候補日時:<br>
    <textarea name="dates" rows="10" cols="40" class="readonly" readonly>{request.forms.dates}</textarea><br>
    コメント:<br>
    <textarea name="comment" rows="3" cols="40" class="readonly" readonly>{comment}</textarea><br>
    <input type='{submit_type}' value='新規作成'/>
    </form>
    <hr>
    <div align="right">
    <button type="button" onclick="history.back()">戻る</button>
    </div>
    """

    return html_header + html_body.format(page_header + page_body + page_footer) + html_footer;

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
    html_header = f"""
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html>
    <head><title>chosei {name}</title></head>
    """
    html_body = "<body>{}</body>"
    html_footer = f"</html>"

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

    return html_header + html_body.format(page_header + page_body + page_footer) + html_footer;

@route('/add/<choseiId>')
@route('/add/<choseiId>/<userId>')
def add_userId(choseiId, userId=None):
    (name, comment, n, dates, users) = get_data(choseiId)

    # 新規 userId == None
    update = False if userId == None else True

    # 新規でなければuserIdのuserを取得、新規ならデフォルト値を設定
    if update:
        userIdlist = [i for i, u in enumerate(users) if u[0] == userId]
        user = users[userIdlist[0]]
    else:
        userId = randomname(10)
        user = [userId] +  ["新規ユーザー"] + ["2"]*n + [""]

    response.set_header('Content-Type', 'text/html; charset=utf-8')
    html_header = f"""
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html>
    <head>
    <title>chosei {name}</title>
    <style>
    input[type="radio"] {{
        display: none;
    }}
    label img {{
        margin: 1px;
        padding: 1px;
    }}
    input[type="radio"] + label img {{
        opacity:0.1;
    }}
    input[type="radio"]:checked + label img {{
        opacity:1;
    }}
    .readonly{{
        background: #EEE;
    }}
    select[readonly],
        input[type="radio"][readonly],
        input[type="checkbox"][readonly]{{
            pointer-events:none;
    }}
    [readonly] + label{{
        pointer-events:none;
    }}
    </style>
    </head>
    """
    html_body = "<body>{}</body>"
    html_footer = f"</html>"

    (scheme, host, path, query_string, fragment) = request.urlparts
    geturl = f"{scheme}://{host}/get/{choseiId}";
    page_header = f"""
    <h1>chosei {name}</h1>
    コメント: <table boarder='1'><tr><td><pre>{comment}</pre></td></tr></table><br>
    リンク: <a href="{geturl}">{geturl}</a>
    <hr>"""

    page_footer = "<hr><a href='/new'>新規イベント作成</a>"

    page_form = f"<form method='POST' action='/add/{choseiId}/{userId}'>"
    page_form  += f"""
    <input type="hidden" name="userId" value="{user[0]}"/>
    ユーザー名:<br>
    <input type="text" name="user_name" value="{user[1]}" pattern="[\S]+"/>（空白なし）<br>
    """
    page_form  += "<table border='1' cellpadding='15'>"
    page_form  += """
    <tr bgcolor='#ddeeee' align='center'>
    <th>候補日時</th>
    <th bgcolor='#f0eeee'><img src="/images/image0.png" with="20" height="20"/></th>
    <th bgcolor='#f0eeee'><img src="/images/image1.png" with="20" height="20"/></th>
    <th bgcolor='#f0eeee'><img src="/images/image2.png" with="20" height="20"/></th>
    </tr>
    """
    for (i, date) in enumerate(dates):
        checked0 = "checked" if user[i+2] == "0" else ""
        checked1 = "checked" if user[i+2] == "1" else ""
        checked2 = "checked" if user[i+2] == "2" else ""
        page_form += f"""
        <tr>
        <td>{date}</td>
        <td>
        <input type="radio" name="date{i}" value="0" id="image0{i}" {checked0}/>
        <label for="image0{i}"><img src="/images/image0.png" with="20" height="20"></label>
        </td>
        <td>
        <input type="radio" name="date{i}" value="1" id="image1{i}" {checked1}/>
        <label for="image1{i}"><img src="/images/image1.png" with="20" height="20"></label>
        </td>
        <td>
        <input type="radio" name="date{i}" value="2" id="image2{i}" {checked2}/>
        <label for="image2{i}"><img src="/images/image2.png" with="20" height="20"></label>
        </td>
        </tr>
        """
    page_form  += "</table>"

    submit_value = "登録更新" if update else "登録追加"
    page_form += f"""
    コメント:<br>
    <textarea name="user_comment" rows="5" cols="40">{user[n+2]}</textarea><br>
    <input type="submit" value="{submit_value}"/>
    """
    page_form  += "</form>"

    page_form_delete = ""
    if update:
        page_form_delete += f"""
        <hr>
        <div align="right">
        <form method='POST' action='/delete_confirm/{choseiId}/{userId}'>
        <input type="submit" value="登録解除"/>
        </form>
        </div>
        """

    page_body = page_form + page_form_delete

    return html_header + html_body.format(page_header + page_body + page_footer) + html_footer;

@route('/add/<choseiId>/<userId>', method="POST")
def do_add(choseiId, userId=None):
    (name, comment, n, dates, users) = get_data(choseiId)

    user = [request.forms.userId, request.forms.user_name]
    for i in range(n):
        dateN = f"date{i}"
        user.append(request.forms[dateN])
    user.append(request.forms.user_comment)

    db_add(choseiId, userId, user)

    return redirect(f"/get/{choseiId}")

@route('/delete_confirm/<choseiId>/<userId>', method="POST")
def do_delete_confirm(choseiId, userId):
    (name, comment, n, dates, users) = get_data(choseiId)

    update = True

    response.set_header('Content-Type', 'text/html; charset=utf-8')
    html_header = f"""
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html>
    <head>
    <title>chosei {name}</title>
    <style>
    input[type="radio"] {{
        display: none;
    }}
    label img {{
        margin: 1px;
        padding: 1px;
    }}
    input[type="radio"] + label img {{
        opacity:0.1;
    }}
    input[type="radio"]:checked + label img {{
        opacity:1;
    }}
    .readonly{{
        background: #EEE;
    }}
    select[readonly],
        input[type="radio"][readonly],
        input[type="checkbox"][readonly]{{
            pointer-events:none;
    }}
    [readonly] + label{{
        pointer-events:none;
    }}
    </style>
    </head>
    """
    html_body = "<body>{}</body>"
    html_footer = f"</html>"

    (scheme, host, path, query_string, fragment) = request.urlparts
    geturl = f"{scheme}://{host}/get/{choseiId}";
    page_header = f"""
    <h1>chosei {name}</h1>
    コメント: <table boarder='1'><tr><td><pre>{comment}</pre></td></tr></table><br>
    リンク: <a href="{geturl}">{geturl}</a>
    <hr>
    """
    page_body = """
    <h2><font color="red">この登録を解除していいですか？</font></h2>
    """
    page_footer = "<hr><a href='/new'>新規イベント作成</a>"

    (name, comment, n, dates, users) = get_data(choseiId)
    userIdlist = [i for i, u in enumerate(users) if u[0] == userId]
    user = users[userIdlist[0]]

    page_form  = f"<form method='POST' action='/add/{choseiId}/{userId}'>"
    page_form  += f"""
    <input type="hidden" name="userId" value="{user[0]}"/>
    ユーザー名:<br>
    <input type="text" name="user_name" value="{user[1]}" pattern="[\S]+" class="readonly" readonly/>（空白なし）<br>
    """
    page_form  += "<table border='1' cellpadding='15'>"
    page_form  += """
    <tr bgcolor='#ddeeee' align='center'>
    <th>候補日時</th>
    <th bgcolor='#f0eeee'><img src="/images/image0.png" with="20" height="20"/></th>
    <th bgcolor='#f0eeee'><img src="/images/image1.png" with="20" height="20"/></th>
    <th bgcolor='#f0eeee'><img src="/images/image2.png" with="20" height="20"/></th>
    </tr>
    """
    for (i, date) in enumerate(dates):
        checked0 = "checked" if user[i+2] == "0" else ""
        checked1 = "checked" if user[i+2] == "1" else ""
        checked2 = "checked" if user[i+2] == "2" else ""
        page_form += f"""
        <tr>
        <td>{date}</td>
        <td>
        <input type="radio" name="date{i}" value="0" id="image0{i}" {checked0} readonly/>
        <label for="image0{i}"><img src="/images/image0.png" with="20" height="20"></label>
        </td>
        <td>
        <input type="radio" name="date{i}" value="1" id="image1{i}" {checked1} readonly/>
        <label for="image1{i}"><img src="/images/image1.png" with="20" height="20"></label>
        </td>
        <td>
        <input type="radio" name="date{i}" value="2" id="image2{i}" {checked2} readonly/>
        <label for="image2{i}"><img src="/images/image2.png" with="20" height="20"></label>
        </td>
        </tr>
        """
    page_form  += "</table>"

    submit_value = "登録更新" if update else "登録追加"
    page_form += f"""
    コメント:<br>
    <textarea name="user_comment" rows="5" cols="40" class="readonly" readonly>{user[n+2]}</textarea><br>
    <input type="hidden" value="{submit_value}"/>
    """
    page_form  += "</form>"

    page_form_delete = ""
    if update:
        page_form_delete += f"""
        <form method='POST' action='/delete/{choseiId}/{userId}'>
        <input type="submit" value="登録解除"/>
        </form>
        <hr>
        <div align="right">
        <button type="button" onclick="history.back()">戻る</button>
        </div>
        """

    page_body += page_form + page_form_delete

    return html_header + html_body.format(page_header + page_body + page_footer) + html_footer;

@route('/delete/<choseiId>/<userId>', method="POST")
def do_delete(choseiId, userId):
    db_delete(choseiId, userId)
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
            dsummery[int(user[i+2])] = dsummery[int(user[i+2])] + 1
        summery.append(dsummery)

    # table
    page_table = "<table border='1' cellpadding='15'>"
    # table header
    tr = """
    <tr bgcolor='#ddeeee' align='center'>"
    <th>日時</th>
    <th bgcolor='#f0eeee'><img src="/images/image0.png" with="20" height="20"/></th>
    <th bgcolor='#f0eeee'><img src="/images/image1.png" with="20" height="20"/></th>
    <th bgcolor='#f0eeee'><img src="/images/image2.png" with="20" height="20"/></th>
    """
    for (i, user) in enumerate(users):
        tr += "<th>"
        tr += f"<a href='/add/{choseiId}/{user[0]}'>{user[1]}</a>" # name
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
            userdate = '<img src="/images/image2.png" with="20" height="20"/>'
            if user[i+2] == "0":
                userdate = '<img src="/images/image0.png" with="20" height="20"/>'
            elif user[i+2] == "1":
                userdate = '<img src="/images/image1.png" with="20" height="20"/>'
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
        tr += f"<td width='80'><pre>{user[n+2]}</pre></td>" # comment
    tr += "</tr>"
    page_table += tr

    page_table += "</table>"

    return page_table

def db_create(choseiId, name, dates=[], comment=""):
    encoded_comment = base64.b64encode(comment.encode()).decode()

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
    encoded_comment = base64.b64encode(comment.encode()).decode()

    userIdlist = [i for i, u in enumerate(users) if u[0] == userId]
    if not userIdlist:
        users.append(user)
    else:
        users[userIdlist[0]] = user

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

def db_delete(choseiId, userId):
    (name, comment, n, dates, users) = get_data(choseiId)
    encoded_comment = base64.b64encode(comment.encode()).decode()

    userIdlist = [i for i, u in enumerate(users) if u[0] == userId]
    if not userIdlist:
        return

    uid = userIdlist[0]
    users.pop(uid)

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
    run(host='0.0.0.0', port=18101, debug=True, reloader=True)
