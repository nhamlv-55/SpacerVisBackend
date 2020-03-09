"""Style guide: use underscore for all variable and function names"""

import sys
if sys.version_info.major < 3:
    raise Exception("User error: This application only supports Python 3, so please use python3 instead of python!")
import json
from flask import Flask, request
from flask_cors import CORS
import tempfile
import argparse
from chctools import horndb as H
import io
import os
from settings import DATABASE, MEDIA, options_for_visualization
from subprocess import PIPE, STDOUT, Popen, run
from chctools import horndb as H
from utils.utils import *
import utils.trace_parsing as ms
app = Flask(__name__)
app.config.from_object(__name__)
CORS(app)

parser = argparse.ArgumentParser(description='Run Spacer Server')
parser.add_argument("-z3", "--z3", required=True, action="store", dest="z3_path", help="path to z3 python")
args = parser.parse_args()

def update_status():
    exps_list = []
    for exp in query_db('select * from exp where done is 0'):
        r = {}
        for k in exp.keys():
            r[k] = exp[k]
        exps_list.append(exp["name"])

    for exp in exps_list:
        print("EXP:", exp)
        is_running = check_if_process_running(exp)
        if not is_running:
            get_db().execute('UPDATE exp SET done = 1 WHERE name = ?', (exp,));

    #commit
    get_db().commit()

def pooling():
    update_status()
    return fetch_exps()


def start_spacer():
    request_params = request.get_json()
    file_content = request_params.get('file', '')
    exp_name = request_params.get('name', '')
    new_exp_name = get_new_exp_name(exp_name)
    print(new_exp_name)
    insert_db('INSERT INTO exp(name, done, result, aux, time) VALUES (?,?,?,?,?)',(new_exp_name, 0, "UNK", "NA", 0))


    spacer_user_options = request_params.get("spacerUserOptions", "")
    var_names = request_params.get("varNames", "")
    print("var_names", var_names)
    exp_folder = os.path.join(MEDIA, new_exp_name)
    os.mkdir(exp_folder)

    input_file = open(os.path.join(exp_folder, "input_file.smt2"), "wb")
    input_file.write(str.encode(file_content))
    input_file.flush() # commit file buffer to disk so that Spacer can access it

    stderr_file = open(os.path.join(exp_folder, "stderr"), "w")
    stdout_file = open(os.path.join(exp_folder, "stdout"), "w")

    run_args = [args.z3_path]
    run_args.extend(spacer_user_options.split())
    run_args.extend(options_for_visualization)
    run_args.append(os.path.abspath(os.path.join(exp_folder, 'input_file.smt2')))
    print(run_args)

    with open(os.path.join(exp_folder, "run_cmd"), "w") as f:
        run_cmd = " ".join(run_args)
        f.write(run_cmd)

    #save VarNames
    with open(os.path.join(exp_folder, "var_names"), "w") as f:
        f.write(var_names)

    Popen(run_args, stdin=PIPE, stdout=stdout_file, stderr=stderr_file, cwd = exp_folder)

    return json.dumps({'status': "success", 'spacer_state': "running", 'exp_name': new_exp_name})

def poke():
    #TODO: finish parsing using all the files in the exp_folder (input_file, etc.)
    request_params = request.get_json()
    exp_path = request_params.get('exp_path', '')
    exp_folder = os.path.join(MEDIA, exp_path)
    nodes_list = []
    run_cmd = ""
    stdout = safe_read(os.path.join(exp_folder, "stdout"))
    stderr = safe_read(os.path.join(exp_folder, "stderr"))
    z3_trace = safe_read(os.path.join(exp_folder, ".z3_trace"))
    spacer_log = safe_read(os.path.join(exp_folder, "spacer.log"))
    run_cmd = safe_read(os.path.join(exp_folder, "run_cmd"))[0].strip()
    var_names = safe_read(os.path.join(exp_folder, "var_names"))[0].strip()

    spacer_state = get_spacer_state(stderr, stdout)
    #load the file into db for parsing 
    db = H.load_horn_db_from_file(os.path.join(exp_folder, "input_file.smt2"))
    rels = []
    for rel_name in db._rels:
        rel = db.get_rel(rel_name)
        rels.append(rel)

    #TODO: only read spacer.log when there are no errors
    if spacer_state == 'running' :
        nodes_list = ms.parse(spacer_log)
        #parse expr to json
        for idx in nodes_list:
            node = nodes_list[idx]
            if node["exprID"]>2:
                expr = node["expr"]
                expr_stream = io.StringIO(expr)
                try:
                    ast = rels[0].pysmt_parse_lemma(expr_stream)
                    ast_json = order_node(to_json(ast))
                    node["ast_json"] = ast_json

                except Exception as e:
                    print("Exception when ordering the node:", e)
                    print("Broken Node", node)
                    print("Broken Node exprID:", node["exprID"])
                    node["ast_json"] = {"type": "ERROR", "content": "trace is incomplete"}


    return json.dumps({'status': "success",
                       'spacer_state': spacer_state,
                       'nodes_list': nodes_list,
                       'run_cmd': run_cmd,
                       'var_names': var_names})


@app.route('/spacer/fetch_exps', methods=['POST'])
def handle_fetch_exps():
    return pooling()
@app.route('/spacer/start_iterative', methods=['POST'])
def handle_start_spacer_iterative():
    return start_spacer()
@app.route('/spacer/poke', methods=['POST'])
def handle_poke():
    return poke()
if __name__ == '__main__':
    app.run()
