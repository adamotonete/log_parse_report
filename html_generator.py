import os
from bson.json_util import loads, dumps

def generate_main(_body, _destination):
    
    html_head = """<!DOCTYPE html>
    <html>
    <head>"""

    html_table_style = """<style>
    table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
    font-family: verdana;
    }
    h1 { 
    font-family: verdana;
    }
    </style>
    <body>
    """

    html_foot = """</body>
    </html> """
    try:
        f = open(_destination + "/index.html", "x")
        f.write(html_head + html_table_style + _body + html_foot)
        f.close()
        return True
    except:
        return False

def html_generate_table(_header, _values, _topic):
    topic = '<h3 style="background-color:33BBFF;">'+ _topic + ':</h1>'
    table = '<table style="width:100%"><tr>'
    for h in _header:
        table = table + "<th>" + h + "</th>"
    
    line = ""
    for v in _values:    
        line = line + "<tr>"
        for k in v.keys():
            line = line + "<td>" + str(v[k]) + "</td>"
    line = line + "</tr>\n"
    line = line + "</table>"

    return (topic + table + line)


def generate_detail(_document,_hash,_destination):
    html_head = """<!DOCTYPE html>
    <html>
    <head>"""
    
    html_table_style = """<style>
    table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
    font-family: verdana;
    }
    h1 { 
    font-family: verdana;
    }
    body {
        font-family: verdana;
    }
    </style>
    <body>
    """
    hash_id = "Query Hash:" + _hash  + "<br>" 
    
    if "attr" in _document:
        if "durationMillis" in _document["attr"]:
            query_time = "Query Time: "  + str(_document["attr"]["durationMillis"]) + "   -> " + str(round(_document["attr"]["durationMillis"]/1000,2)) + " seconds" + "<br>"
    
    kbRead = ""
    if "attr" in _document:
        if "storage" in _document["attr"]:
            if "data" in _document["attr"]["storage"]:
                if "bytesRead" in _document["attr"]["storage"]["data"]:
                    bytesRead = _document["attr"]["storage"]["data"]["bytesRead"]
                    bytesRead = round(bytesRead/1024/1024,2)
                    kbRead = "Bytes Read: "  + str(bytesRead) + "MB (Megabyte)" + "<br>"
        
    app_name = ""
    if "appName" in _document["attr"] is not None:
        app_name = "App Name: " + str(_document["attr"]["appName"]) + "<br>"
    
    json_text = '''
    <hr> 
    <pre id="myText" ></pre>
    <script>
    var data = ''' + dumps(_document) + '''
    document.getElementById("myText").innerHTML = JSON.stringify(data, null, 4);
    </script>
    '''

    body = hash_id + query_time + kbRead + app_name + json_text

    html_foot = """</body>
    </html> """
    
    #try:
    f = open(_destination + "/" + _hash + ".html", "x")
    f.write(html_head + html_table_style + body + html_foot)
    f.close()
    return True
    #except:
    #    return False


    