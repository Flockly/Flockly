from flask import session, Response, request, redirect
from flockly import app, basefunc
from facebook import GraphAPI
import flockly.authpage
import flockly.blockly
import requests
import json
import time
import config


@app.route('/get_friends')
@basefunc.auth_required
@basefunc.tojson
def get_friends():
    token = flockly.authpage.get_user_access_token(session['uid'])
    graph = GraphAPI(token)
    friends = []
    res = graph.get('/me/friends')
    while res['data']:
        friends = friends + res['data']
        if 'paging' in res and 'next' in res['paging']:
            res = json.loads(requests.get(res['paging']['next']).text)
    return friends


@app.route('/upload_blockly', methods=['POST'])
@basefunc.auth_required
def upload_blockly():
    id = None
    if 'id' in request.form:
        id = request.form['id']
    a_blockly = None
    if id:
        a_blockly = list(flockly.blockly.Blockly.objects(id=id, userid=session['uid']))
        if a_blockly:
            a_blockly = a_blockly[0]
        else:
            return Response('', status=404)
    else:
        a_blockly = flockly.blockly.Blockly()
        a_blockly['userid'] = session['uid']

    a_blockly['content'] = request.form['content']
    a_blockly['name'] = request.form['name']
    a_blockly['lastmodified'] = int(time.time())

    a_blockly.save()
    return str(a_blockly.id)



@app.route('/get_blockly_list')
@basefunc.auth_required
@basefunc.tojson
def get_blockly_list():
    blocklies = []
    for i in flockly.blockly.Blockly.objects(userid=session['uid']):
        blocklies.append({'id': str(i.id), 'name': i.name, 'enabled': i.enabled, 'lastmodified': i.lastmodified})
    return blocklies


@app.route('/get_blockly')
@basefunc.auth_required
@basefunc.tojson
def get_blockly():
    try:
        a_blockly = list(flockly.blockly.Blockly.objects(id=request.args.get('id', ''), userid=session['uid']))
    except:
        return Response('', status=404)
    if a_blockly:
        a_blockly = a_blockly[0]
        return {
                'id': str(a_blockly.id),
                'userid': a_blockly.userid,
                'content': a_blockly.content,
                'name': a_blockly.name,
                'logs': a_blockly.logs,
                'enabled': a_blockly.enabled,
                'lastmodified': a_blockly.lastmodified
                }
    else:
        return Response('', status=404)

@app.route('/enable')
@basefunc.auth_required
def enable_block():
    try:
        for i in flockly.blockly.Blockly.objects(id=request.args.get('id', ''), userid=session['uid']):
            i.enabled = bool(int(request.args.get('enabled', '0')))
            i.save()
        return ''
    except:
        return Response('', status=404)

@app.route('/reset_blockly', methods=['POST'])
@basefunc.auth_required
def reset_block():
    try:
        for i in flockly.blockly.Blockly.objects(id=request.form['id'], userid=session['uid']):
            i.timesexecuted = 0
            i.lastexecution = 0
            i.logs = []
            i.save()
        return ''
    except:
        return Response('', status=404)

@app.route('/delete_blockly', methods=["POST"])
@basefunc.auth_required
def delete_blockly():
    try:
        flockly.blockly.Blockly.objects(id=request.form['id'], userid=session['uid']).delete()
        return ''
    except:
        return Response('', status=404)


@app.route('/share', methods=['POST'])
@basefunc.auth_required
def share_blockly():
    try:
        blo = flockly.blockly.Blockly.objects(id=request.form['id'], userid=session['uid'])[0]
        new_link = config.SITE_URL + "/share_import/" + str(blo.id)
        blo.public = True
        blo.save()
        return new_link
    except:
        return ''

@app.route('/share_import/<id>')
@basefunc.auth_required
def share_import(id):
    try:
        blo = flockly.blockly.Blockly.objects(id=id, public=True)[0]
        new_blo = flockly.blockly.Blockly()
        new_blo.userid = session['uid']
        new_blo.content = blo.content
        new_blo.name = 'Imported Flockly: ' + blo.name
        new_blo.lastmodified = blo.lastmodified
        new_blo.save()
        return redirect('/block?id=' + str(new_blo.id))
    except:
        return redirect('/')



@app.route('/get_profile')
@basefunc.auth_required
@basefunc.tojson
def get_profile():
    token = flockly.authpage.get_user_access_token(session['uid'])
    graph = GraphAPI(token)
    profile = graph.get('/me?fields=id,name,picture.type(large)&access_token=%s&' % (token))
    return profile
