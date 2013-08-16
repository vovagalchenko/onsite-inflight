import httplib, urllib, sys, subprocess
from os import remove, listdir, path, makedirs
import os
import hashlib
from shutil import copyfile
from bs4 import BeautifulSoup
from lib.conf import CFG
from re import sub, compile, I

def hash_file(filepath):
    sha1 = hashlib.sha1()
    f = open(filepath, 'rb')
    try:
        sha1.update(f.read())
    finally:
        f.close()
    return sha1.hexdigest()

def exec_git_command(cmd):
    cmd = ['git'] + cmd
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    p.wait()
    return p.stdout.read()

def compile_js_file(js_file_path):
    js_file = open(js_file_path, 'r')
    original_file_contents = js_file.read()
    params = urllib.urlencode([
        ('js_code', original_file_contents),
        ('compilation_level', 'SIMPLE_OPTIMIZATIONS'),
        ('output_format', 'text'),
        ('output_info', 'errors'),
      ])
    
    headers = { "Content-type": "application/x-www-form-urlencoded" }
    conn = httplib.HTTPConnection('closure-compiler.appspot.com')
    conn.request('POST', '/compile', params, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    if len(data) > 1:
        print data
        raise Exception("Warnings found when compiling.")
    else:
        params = urllib.urlencode([
            ('js_code', original_file_contents),
            ('compilation_level', 'SIMPLE_OPTIMIZATIONS'),
            ('output_format', 'text'),
            ('output_info', 'compiled_code'),
          ])
        
        headers = { "Content-type": "application/x-www-form-urlencoded" }
        conn = httplib.HTTPConnection('closure-compiler.appspot.com')
        conn.request('POST', '/compile', params, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        if len(data) <= 1:
            raise Exception("A problem occurred when compiling")
    return data

def open_if_not_there(file_path):
    fd = None
    try:
        fd = os.open(file_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except:
        return None
    return os.fdopen(fd, "w")


ROOT = CFG.get_instance().get('installation', 'root') + '/code/webapp/'
js_compiled_dir = path.join(ROOT, "js/compiled")
if not path.exists(js_compiled_dir):
    makedirs(js_compiled_dir)
css_compiled_dir = path.join(ROOT, "css/compiled")
if not path.exists(css_compiled_dir):
    makedirs(css_compiled_dir)
for file_name in listdir(ROOT):
    html_file_path = path.join(ROOT, file_name)
    if not path.isfile(html_file_path):
        continue
    print "Compiling js for " + file_name
    html_file = open(html_file_path, "r")
    html_file_string = html_file.read()
    soup = BeautifulSoup(html_file_string[:])
    html_file.close()

    scripts = soup.findAll(lambda tag: tag.name.lower() == "script",
                           attrs={'type' : compile("^text\/javascript$", I)})
    for script in scripts:
        js_path = script.get('src', None)
        if js_path is None or js_path.find('js/compiled/') != -1:
            continue
        js_abs_path = ROOT + js_path
        file_hash = hash_file(js_abs_path)
        new_js_path = sub('(\.js)?$', "_" + file_hash + ".js", js_path)
        new_js_path = sub('^\/?js\/', 'js/compiled/', new_js_path)
        new_js_abs_path = ROOT + new_js_path
        new_js_file = open_if_not_there(new_js_abs_path)
        if new_js_file is not None:
            print "\tBuilding " + js_path
            new_js_file.write(compile_js_file(js_abs_path))
            new_js_file.close()
        html_file_string = sub('(?i)src\s*?=\s*?["\']' + js_path + '["\']', 'src="' + new_js_path + '"', html_file_string)

    css = soup.findAll(lambda tag: tag.name.lower() == "link",
                       attrs={'type' : compile("^text\/css$", I)})
    for css_tag in css:
        css_path = css_tag.get('href', None)
        if css_path is None or css_path.find('css/compiled/') != -1:
            continue
        css_abs_path = ROOT + css_path
        file_hash = hash_file(css_abs_path)
        new_css_path = sub('(\.css)?$', '_' + file_hash + '.css', css_path)
        new_css_path = sub('\/?css\/', 'css/compiled/', new_css_path)
        new_css_abs_path = ROOT + new_css_path
        copyfile(css_abs_path, new_css_abs_path)
        html_file_string = sub('(?i)href\s*?=\s*?["\']' + css_path + '["\']', 'href="' + new_css_path + '"', html_file_string)
        

    html_file = open(html_file_path, "w")
    html_file.write(html_file_string)
    html_file.close()
