#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Library for convenient usage of the Gamma Software within a Python environment
# Copyright 2020 Gamma Remote Sensing, v4.3 25-Jun-2020 cm/clw/aw

from __future__ import print_function
import io
import subprocess
import os
import sys
import ast
if sys.version_info[0] == 2 or sys.version_info[1] < 7:
  print('Python version: %s' % (sys.version))
  print('py_gamma was developed with Python 3.7. While it was tested on Python 2.7 and 3.6, full compatibility')
  print('with older Python versions is not guaranteed. We recommend using the latest Python 3 version.\n')
import webbrowser
import re
import numpy as np
import matplotlib as mpl
import time
if sys.platform == 'win32':
  try:
    import psutil
  except:
    print("ERROR: please install psutil (e.g.: pip install psutil)")
    sys.exit(-1)
try:
  from collections import OrderedDict
  is_ordered = True
except:
  is_ordered = False
from threading import Thread, Event
from collections import deque
#try:
#  from queue import Queue, Empty
#except ImportError:
#  from Queue import Queue, Empty  # python 2.x
if sys.platform == 'win32':
  try:
    from winreg import HKEY_CURRENT_USER, OpenKey, QueryValue
  except:
    from _winreg import HKEY_CURRENT_USER, OpenKey, QueryValue

# global variables definition
# current Matplotlib PyPlot backend
cur_backend = mpl.get_backend()
# environment
gamma_env = os.environ.copy()
# for each program name, path to executable (bin and script)
gamma_exec_dict = {}
# for each program, extension
gamma_ext_dict = {}
# for each script, script language
gamma_script_dict = {}
# list of the scripts to ignore
ignore_list_scripts = ['modest_image.py', 'ColormapText.py', 'prflib.py', 'profile.py', 'colormap_list.py', 'gamma_doc',
  'temp_filt.py', 'temp_filt_ad.py', 'README.scripts', 'multi_S1_TOPS', 'par_RSI', 'par_RSI_RSAT', 'SLC_burst_copy',
  'SLC_burst_corners', 'SLC_cat_S1_TOPS', 'SLC_copy_S1_TOPS', 'SLC_interp_S1_TOPS', 'SLC_ov2.orig', 'SLC_ovr2',
  'PRI_to_MLI', 'interp_cpx', 'interp_real', 'mk_geo', 'SLC_interp_lt_S1_TOPS', 'mk_ASF_CEOS_list', 'dem_import.py',
  'ScanSAR_coreg']
# list of interactive programs
interactive_progs = ['coord_trans', 'create_dem_par', 'create_diff_par', 'create_offset', 'create_sar_par', 'create_proc_par',
  'create_mli_par', 'create_sensor_par', 'disp_plot_pt', 'offset_fit', 'offset_fitm', 'offset_list_fitm', 'offset_pwr',
  'offset_pwrm', 'offset_pwr_list', 'offset_pwr_tracking', 'offset_pwr_tracking2', 'offset_pwr_trackingm', 'offset_pwr_trackingm2',
  'par_ACS_ERS', 'par_ASF_91', 'par_ASF_96', 'par_ASF_PRI', 'par_ASF_RSAT_SS', 'par_ATLSCI_ERS', 'par_EORC_JERS_SLC',
  'par_ESA_ERS', 'par_PRI', 'par_PRI_ESRIN_JERS', 'par_PulSAR', 'par_RSAT_SCW', 'par_RSAT_SGF',
  'par_RSI_ERS', 'ptarg', 'ptarg_cal_MLI', 'ptarg_cal_SLC', 'ptarg_SLC']
# if True, prints debugging outputs
is_verbose = False
# list of lists of binaries
package_bin = []
# bin directory for each package
package_dir_bin = []
# scripts directory for each package
package_dir_scripts = []
# list of available packages
package_list = []
# list of lists of scripts
package_scripts = []
# list of possible packages
possible_packages = ['DISP', 'DIFF', 'IPTA', 'ISP', 'LAT', 'MSP', 'GEO']
# functions of the py_gamma module
python_functions = ['gamma_doc', 'read_image', 'read_point_data', 'read_point_list', 'read_tab', 'run_cmd', 'update_image', 'which', 'write_image', 'write_point_data', 'write_point_list', 'write_tab']
# path of py_gamma.py
script_path = os.path.realpath(__file__)
# directory containing py_gamma.py
script_dir = os.path.dirname(script_path)

# functions definition
def gamma_doc(*arg):
  """Open Gamma Software documentation in the default web browser
  
  **Argument:**
  
  arg can be one of the following possibilities:
  
  1. A program name from the Gamma Software
     (e.g. gamma_doc('disras'))
  2. The Python function for a Gamma Software program
     (e.g. gamma_doc(py_gamma.disras))
  3. The name of a GAMMA software package
     (e.g. gamma_doc('DISP'))
  4. The py_gamma module
     (e.g. gamma_doc(py_gamma) or gamma_doc('py_gamma'))
  5. If no input argument is given the top-level html file
     of the GAMMA software html documentation is opened."""
  
  thismodule = sys.modules[__name__]
  
  if not arg:
    prog = ''
  else:
    if isinstance(arg[0], str):
      if arg[0] in python_functions:
        help(getattr(thismodule, arg[0]))
        return
      if arg[0] in package_list or arg[0] == 'py_gamma':
        prog = arg[0]
      else:
        filename, file_extension = os.path.splitext(arg[0])
        if file_extension == '':
          if not gamma_ext_dict[arg[0]] == '':
            prog = arg[0] + gamma_ext_dict[arg[0]]
          else:
            prog = arg[0]
        else:
          prog = arg[0]
    elif callable(arg[0]):
      if arg[0].__name__ in python_functions:
        help(arg[0])
        return
      if not gamma_ext_dict[arg[0].__name__] == '':
        prog = arg[0].__name__ + gamma_ext_dict[arg[0].__name__]
      else:
        prog = arg[0].__name__
    elif arg[0] == thismodule:
      prog = arg[0]
    else:
      print('WARNING: invalid input for gamma_doc function, opening main documentation page')
      prog = ''
  
  if prog == '': 
    link = os.path.join(script_dir, 'Gamma_documentation_contents_sidebar.html')
  elif prog == 'py_gamma' or prog == thismodule:
    link = os.path.join(script_dir, "Gamma_documentation_contents_sidebar.html#Python integration with the py_gamma module")
  elif prog in package_list:
    link = os.path.join(script_dir, prog, 'html', prog + '_documentation_contents_sidebar.html')
  else:
    found = False
    for package in package_list:
      for prog_bin in package_bin[package_list.index(package)]:
        if prog == prog_bin:
#          link = os.path.join(script_dir, package, 'html', package + '_documentation_contents_sidebar.html#' + prog)
          link = os.path.join(script_dir, 'Gamma_documentation_contents_sidebar.html#' + prog)
          found = True
          break
      if found:
        break
      for prog_script in package_scripts[package_list.index(package)]:
        if prog == prog_script:
#          link = os.path.join(script_dir, package, 'html', package + '_documentation_contents_sidebar.html#' + prog)
          link = os.path.join(script_dir, 'Gamma_documentation_contents_sidebar.html#' + prog)
          found = True
          break
      if found:
        break
    if not found:
      print('WARNING: no package %s found, opening main documentation page' % prog)
      link = os.path.join(script_dir, 'Gamma_documentation_contents_sidebar.html')
  link = 'file:///' + link
  if is_verbose:
    print('\nlink: ' + link + '\n')
  
  if sys.platform == 'win32':
    webbrowser.get('default_browser').open(link)
  else:
    try:
      if sys.platform == 'darwin':
        stat = webbrowser.get('firefox').open(link)
        if not stat:
          raise
      else:
        firefox_path = which('firefox')
        if firefox_path is None:
          raise
        else:
          stat = webbrowser.get('"' + firefox_path + '" -no-remote %s &').open(link)
          if not stat:
            raise
    except:
      try:
        stat = webbrowser.get('safari').open(link)
        if not stat:
          raise
      except:
        try:
          stat = webbrowser.get('google-chrome').open(link)
          if not stat:
            raise
        except:
          try:
            stat = webbrowser.get('chrome').open(link)
            if not stat:
              raise
          except:
            try:
              stat = webbrowser.get('chromium-browser').open(link)
              if not stat:
                raise
            except:
              webbrowser.open(link)
  return

def gamma_program(prog, *gamma_args, **kwargs):
  def enqueue_output(out, deck, stop_event):
    while not stop_event.is_set():
      char = out.read(1)
      if not char == '':
        deck.append(char)
  
  def kill_proc_tree(pid, including_parent=True):
    if psutil.pid_exists(pid):
      parent = psutil.Process(pid)
      children = parent.children(recursive=True)
      for child in children:
        child.kill()
      gone, still_alive = psutil.wait_procs(children, timeout=5)
      if including_parent and parent.is_running():
        parent.kill()
        parent.wait(5)
  
  def read_stdout(line_out):
    p_stdout = ''
    
    while True:
      for elem in list(d_out):
        p_stdout += elem
        d_out.remove(elem)
      
      time.sleep(0.01)
      if len(d_out) == 0:
        break
    
    if p_stdout:
      p_stdout = p_stdout.splitlines()
      for line_out in p_stdout:
        if 'cout' in kwargs:
          kwargs['cout'].append(line_out.rstrip())
        if 'logf' in kwargs:
          logf.write(line_out + '\n')
        text_line = line_out.rstrip()
        if stdout_flag:
          print(text_line)
        sys.stdout.flush()
    
    return line_out
  
  def read_stderr(line_err):
    p_stderr = ''
    
    while True:
      for elem in list(d_err):
        p_stderr += elem
        d_err.remove(elem)
      
      time.sleep(0.01)
      if len(d_err) == 0:
        break
    
    if p_stderr:
      p_stderr = p_stderr.splitlines()
      for line_err in p_stderr:
        if 'cerr' in kwargs:
          kwargs['cerr'].append(line_err.rstrip())
        if 'errf' in kwargs:
          errf.write(line_err + '\n')
        if 'logf' in kwargs:
          logf.write(line_err + '\n')
        text_line = line_err.rstrip()
        if stderr_flag:
          print(text_line)
        sys.stdout.flush()
        
    return line_err
  
  def stop_threads(t_out, t_err, t_out_stop, t_err_stop):
    if t_out.is_alive():
      t_out_stop.set()
      while t_out.is_alive():
        time.sleep(0.001)
    if t_err.is_alive():
      t_err_stop.set()
      while t_err.is_alive():
        time.sleep(0.001)
  
  if '--help' in gamma_args:
    gamma_doc(prog)
    return
  
  if not 'from_run_cmd' in prog:
    if prog in gamma_script_dict:
      cmd_list = [gamma_script_dict[prog], gamma_exec_dict[prog]]
    else:
      cmd_list = [gamma_exec_dict[prog]]
  else:
    cmd_list = []
  
  # handle options in kwargs
  is_interactive = False
  wait_flag = True
  stdout_flag = True
  stderr_flag = True
  if 'wait' in kwargs:
    wait_flag = kwargs['wait']
  if 'is_inter' in kwargs:
    is_interactive = kwargs['is_inter']
  if 'logf' in kwargs:
    logf = open(kwargs['logf'], "a+")
    wait_flag = True
  if 'errf' in kwargs:
    errf = open(kwargs['errf'], "a+")
    wait_flag = True
  if 'stdout_flag' in kwargs:
    stdout_flag = kwargs['stdout_flag']
  if 'stderr_flag' in kwargs:
    stderr_flag = kwargs['stderr_flag']
  
  # generate command from prog and gamma_args
  if gamma_args:
    for arg in gamma_args:
      if isinstance(arg, str):
        arg_split = arg.split()
        if len(arg_split) > 1 and arg_split[0][0] == '-':
          for arg_s in arg_split:
            cmd_list.append(arg_s)
        else:
          cmd_list.append(arg)
      else:
        cmd_list.append(str(arg))
    
    # set backend for Python visualization scripts
    if ('vis' in prog or 'plot' in prog) and gamma_script_dict[prog] == 'python' and not '-k' in cmd_list:
      cmd_list.append('-k')
      cmd_list.append(cur_backend)
  
  # print command
  # if is_verbose and stdout_flag:
    # print('cmd_list: ' + str(cmd_list) + '\n')
  
  cmd = " ".join(cmd_list)
  if is_verbose:
    print('cmd: ' + cmd + '\n')
  sys.stdout.flush()
  if 'logf' in kwargs:
    logf.write('% ' + cmd + '\n\n')
  
  # run command
  try:
    if prog in interactive_progs:
      is_interactive = True
    
    if is_interactive:
      wait_flag = True
    
    if sys.platform == 'win32' or 'from_run_cmd' in prog:
      p=subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True, env=gamma_env)
    else:
      p=subprocess.Popen(cmd_list, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=gamma_env)
    
    if wait_flag:
      if is_interactive and 'cin' in kwargs:
        input_list = []
        for item in kwargs['cin']:
          input_list.append(item)
        for i in range(len(input_list)):
          input_list[i] = str(input_list[i])
          input_list[i] = input_list[i].rstrip()
          input_list[i] = input_list[i] + '\n'
        
      # from https://stackoverflow.com/questions/11457931/running-an-interactive-command-from-within-python
      # and https://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python
      # Queue replaced by deque (faster on Linux)
      
      d_out = deque()
      d_err = deque()
      
      t_out_stop = Event()
      t_err_stop = Event()
      
      t_out = Thread(target=enqueue_output, args=(p.stdout, d_out, t_out_stop))
      t_err = Thread(target=enqueue_output, args=(p.stderr, d_err, t_err_stop))
      
      # thread dies with the program: not needed since we make sure threads are killed at the end of the subprocess
      # t_out.daemon = True
      # t_err.daemon = True
      
      t_out.start()
      t_err.start()
      
      while True:
        
        line_out = ''
        line_err = ''
        
        # Read from p_stdout
        line_out = read_stdout(line_out)
        
        # Read from p_stderr
        line_err = read_stderr(line_err)
        
        p.poll()
        
        if p.returncode == 0:
          
          # empty queue
          time.sleep(0.01)
          line_out = read_stdout(line_out)
          line_err = read_stderr(line_err)
          
          if stdout_flag:
            print('')
          stop_threads(t_out, t_err, t_out_stop, t_err_stop)
          break
        elif not p.returncode == 0 and not p.returncode == None:
          
          # empty queue
          time.sleep(0.01)
          line_out = read_stdout(line_out)
          line_err = read_stderr(line_err)
          
          if stdout_flag:
            print('')
          if 'logf' in kwargs:
            logf.write('\n')
            logf.close()
          if 'errf' in kwargs:
            errf.close()
          stop_threads(t_out, t_err, t_out_stop, t_err_stop)
          return -1
        
        if is_interactive and (line_out.rstrip().endswith(':') or line_err.rstrip().endswith(':')):
          
          # empty queue
          time.sleep(0.01)
          line_out = read_stdout(line_out)
          line_err = read_stderr(line_err)
          
          if line_out.rstrip().endswith(':') or line_err.rstrip().endswith(':'):
            if 'cin' in kwargs and len(input_list) > 0:
              stdin = input_list[0]
              del(input_list[0])
              if stdout_flag:
                print(stdin)
            else:
              if sys.version_info[0] < 3:
                stdin = raw_input('Enter value (type \"exit\" to quit): ') + '\n'
              else:
                stdin = input('Enter value (type \"exit\" to quit): ') + '\n'
              
              if 'exit' in stdin:
                if sys.platform == 'win32':
                  kill_proc_tree(p.pid)
                else:
                  p.terminate()
                if stdout_flag:
                  print('')
                if 'logf' in kwargs:
                  logf.write('\n')
                  logf.close()
                if 'errf' in kwargs:
                  errf.close()
                stop_threads(t_out, t_err, t_out_stop, t_err_stop)
                return -1
              
            p.stdin.write(stdin)
            p.stdin.flush()
            if stdout_flag:
              print('')
            if 'cout' in kwargs:
              kwargs['cout'].append(stdin.rstrip())
            if 'logf' in kwargs:
              logf.write(stdin)
  
      if 'logf' in kwargs:
        logf.write('\n')
        logf.close()
      if 'errf' in kwargs:
        errf.close()
      return 0
  
  except (EOFError, KeyboardInterrupt):
    if sys.platform == 'win32':
      kill_proc_tree(p.pid)
    else:
      p.terminate()
    if wait_flag:
      stop_threads(t_out, t_err, t_out_stop, t_err_stop)
    print('\nProcess interrupted (KeyboardInterrupt)\n')
    if 'logf' in kwargs:
      logf.write('\nProcess interrupted (KeyboardInterrupt)\n')
      logf.close()
    if 'errf' in kwargs:
      errf.write('\nProcess interrupted (KeyboardInterrupt)\n')
      errf.close()
    return -1
  
  except Exception as e:
    if is_verbose:
      print(e)
    try:
      if sys.platform == 'win32':
        kill_proc_tree(p.pid)
      else:
        p.terminate()
      if wait_flag:
        stop_threads(t_out, t_err, t_out_stop, t_err_stop)
    except:
      pass
    print('ERROR: the command could not be executed: ' + cmd + '\n')
    if 'logf' in kwargs:
      logf.write('ERROR: the command could not be executed: ' + cmd + '\n')
      logf.close()
    if 'errf' in kwargs:
      errf.write('ERROR: the command could not be executed: ' + cmd + '\n')
      errf.close()
    return -1

def initialize():
  global package_list
  global package_dir_bin
  global package_dir_scripts
  global package_bin
  global package_scripts
  global gamma_exec_dict
  global gamma_script_dict
  global gamma_ext_dict
  global gamma_env
  
  def create_gamma_function(prog, extension):
    if not extension == '':
      prog_ext = prog + extension
    else:
      prog_ext = prog
    
    @doc("""stat = %s(gamma_arg1, gamma_arg2, ..., cin = None, cout = None, cerr = None, errf = None, logf = None, stdout_flag = True, stderr_flag = True, wait = True)
    
    Run the Gamma Software program \"%s\"
    
    **Arguments:**
    
    Note: entering '--help' as argument will open Gamma Software documentation for %s in the default web browser.
    
    * gamma_args: argument(s) of %s program, enter %s() to get the list of arguments
    
    **Keyword arguments:**
    
    * cin:          list to use as input of an interactive function
    * cout:         list where the stdout will be appended (list, has to be created before calling the function)
    * cerr:         list where the stderr will be appended (list, has to be created before calling the function)
    * errf:         error file where the stderr will be appended (string containing the path to the err file)
    * logf:         log file where the stdout will be appended (string containing the path to the log file)
    * stdout_flag:  print stdout to the console (boolean, default = True)
    * stderr_flag:  print stderr to the console (boolean, default = True)
    * wait:         wait for the subprocess to be finished (boolean, default = True)
    
    **Output:**
    
    * the function returns a status flag: 0: success, -1: failure""" % (prog, prog_ext, prog_ext, prog, prog_ext))
    def _function(*gamma_args, **kwargs):
      value = gamma_program(prog, *gamma_args, **kwargs)
      return value
    
    _function.__name__ = prog
    return _function
  
  def doc(docstring):
    def document(func):
      func.__doc__ = docstring
      return func
    return document

  def get_default_browser_win():
    browser = ''
    try:
      with OpenKey(HKEY_CURRENT_USER, "Software\Classes\http\shell\open\command") as key:
        browser = QueryValue(key, None)
        
      if browser != '':
        browser.rstrip()
        test = re.search('(.+?).exe"', browser)
        if test:
          found = test.group(1)
          browser = found.lstrip('\"') + '.exe'
      return browser
    except:
      browser = r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'
      exists = os.path.isfile(browser)
      if exists:
        return browser
      else:
        browser = r'C:\Program Files\Mozilla Firefox\firefox.exe'
        exists = os.path.isfile(browser)
        if exists:
          return browser
        else:
          browser = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
          exists = os.path.isfile(browser)
          if exists:
            return browser
          else:
            browser = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
            exists = os.path.isfile(browser)
            if exists:
              return browser
            else:
              print('ERROR: No browser found\n')
              return None
  
  def no_package_found():
    print('**********************************************************')
    print('*** WARNING: no Gamma Software package found!          ***')
    print('***          make sure that the file py_gamma.py is in ***')
    print('***          the main directory of the Gamma Software  ***')
    print('**********************************************************')
  
  # default language setting
  gamma_env['LANG'] = 'C'
  
  # initialize missing environment variables
  if not 'HDF5_DISABLE_VERSION_CHECK' in gamma_env.keys() and not sys.platform == 'darwin':
    gamma_env['HDF5_DISABLE_VERSION_CHECK'] = '1'
  if not 'GAMMA_RASTER' in gamma_env.keys():
    gamma_env['GAMMA_RASTER'] = 'BMP'
  if not 'GNUTERM' in gamma_env.keys():
    if sys.platform == 'linux':
      gamma_env['GNUTERM'] = 'qt'
    else:
      gamma_env['GNUTERM'] = 'wxt'
  if not 'GAMMA_HOME' in gamma_env.keys():
      gamma_env['GAMMA_HOME'] = script_dir
  
  if sys.platform == 'win32':
    # add MSYS64 / MINGW64 / GAMMA_LOCAL paths to PATH
    if 'MSYS64' in gamma_env.keys():
      gamma_env['PATH'] = os.path.join(gamma_env['MSYS64'], 'usr', 'bin') + ';' + gamma_env['PATH']
    if 'MINGW64' in gamma_env.keys():
      gamma_env['PATH'] = os.path.join(gamma_env['MINGW64'], 'bin') + ';' + gamma_env['PATH']
      gamma_env['GDAL_DATA'] = os.path.join(gamma_env['MINGW64'], 'share', 'gdal')
      gamma_env['PROJ_LIB'] = os.path.join(gamma_env['MINGW64'], 'share', 'proj')
    if 'GAMMA_LOCAL' in gamma_env.keys():
      gamma_env['PATH'] = os.path.join(gamma_env['GAMMA_LOCAL'], 'bin') + ';' + gamma_env['PATH']
      gamma_env['GDAL_DATA'] = os.path.join(gamma_env['GAMMA_LOCAL'], 'share', 'gdal')
      gamma_env['PROJ_LIB'] = os.path.join(gamma_env['GAMMA_LOCAL'], 'share', 'proj')
    gamma_env['PATH'] = gamma_env['PATH'] + ';' + os.path.join('C:/', 'Program Files', 'gnuplot', 'bin')
    gamma_env['PATH'] = gamma_env['PATH'] + ';' + os.path.join('C:/', 'Program Files  (x86)', 'gnuplot', 'bin')
    gamma_env['PATH'] = os.path.dirname(sys.executable) + ';' + gamma_env['PATH']
  
  for package in possible_packages:
    if os.path.isdir(os.path.join(script_dir, package)):
      package_list.append(package)
  
  # if list empty, throw warning
  if not package_list:
    no_package_found()
  
  # check if GEO in list, if yes move to the end
  GEO_flg = False
  for package in package_list:
    if package == 'GEO':
      GEO_flg = True
      package_list.remove('GEO')
      break

  if GEO_flg:
    package_list.append('GEO')
  
  if is_verbose:
    print('')
    print('package directories:')
  
  # get list of binaries and create a function for each of them
  for package in package_list:
    dir_bin = os.path.join(script_dir, package, 'bin')
    dir_scripts = os.path.join(script_dir, package, 'scripts')
    package_dir_bin.append(dir_bin)
    package_dir_scripts.append(dir_scripts)
    package_home = package + '_HOME'
    if not package_home in gamma_env.keys():
      gamma_env[package_home] = os.path.join(script_dir, package)
    if sys.platform == 'win32':
      gamma_env['PATH'] += ';' + dir_bin + ';' + dir_scripts
    else:
      gamma_env['PATH'] += ':' + dir_bin + ':' + dir_scripts
  
  if is_verbose:
    print(package_dir_bin)
    print(package_dir_scripts)
  
  num = 0
  for package in package_list:
    # binaries
    if is_verbose:
      print('')
      print(package + ':')
      print('bin:')
    
    f = []
    for (dirpath, dirnames, filenames) in os.walk(package_dir_bin[num]):
      f.extend(filenames)
      break
    
    for k in range(len(f)):
      filename, file_extension = os.path.splitext(f[k])
      if (file_extension == '.exe'):
        f[k] = filename
      
      if not filename in gamma_exec_dict:
        gamma_exec_dict[filename] = os.path.join(package_dir_bin[num], filename)
        if not file_extension == '.exe':
          gamma_ext_dict[filename] = file_extension
          globals()[filename] = create_gamma_function(filename, file_extension)
        else:
          gamma_ext_dict[filename] = ''
          globals()[filename] = create_gamma_function(filename, '')
    
    package_bin.append(f)
    package_bin[num] = sorted(package_bin[num], key=str.lower)
    if is_verbose:
      print(f)
    
    # scripts
    if is_verbose:
      print('scripts:')
    f = []
    for (dirpath, dirnames, filenames) in os.walk(package_dir_scripts[num]):
      f.extend(filenames)
      break
    
    for k in range(len(f)-1, -1, -1):
      filename, file_extension = os.path.splitext(f[k])
      if (file_extension == '.dem') or (file_extension == '.dem_par') or (file_extension == '.tif') or (file_extension == '.pyc'):
        del f[k]
        continue
      
      ignore_flag = False
      for script in ignore_list_scripts:
        if (f[k] in script):
          del f[k]
          ignore_flag = True
          break
      
      if not ignore_flag:
        if not filename in gamma_exec_dict:
          gamma_exec_dict[filename] = os.path.join(package_dir_scripts[num], f[k])
          gamma_ext_dict[filename] = file_extension
          globals()[filename] = create_gamma_function(filename, file_extension)
          
          # read shebang
          script_file = io.open(gamma_exec_dict[filename], 'r', encoding="utf8", errors='ignore')
          shebang = script_file.readline()
          
          if ('python' in shebang):
            gamma_script_dict[filename] = 'python'
          elif ('perl' in shebang):
            gamma_script_dict[filename] = 'perl'
          elif ('bash' in shebang):
            gamma_script_dict[filename] = 'bash'
          elif ('tcsh' in shebang):
            gamma_script_dict[filename] = 'tcsh'
          elif ('csh' in shebang):
            gamma_script_dict[filename] = 'csh'
          elif ('sh' in shebang):
            gamma_script_dict[filename] = 'sh'
          
          script_file.close()
    
    package_scripts.append(f)
    package_scripts[num] = sorted(package_scripts[num], key=str.lower)
    if is_verbose:
      print(f)
    num += 1
  
  sys.stdout.flush()
  
  # Get default browser
  if sys.platform == 'win32':
    browser = get_default_browser_win()
    if browser:
      webbrowser.register('default_browser', None, webbrowser.BackgroundBrowser(browser))

def read_image(filename, **kwargs):
  """data = read_image(filename, par = None, width = None, dtype = 'float', x0 = None, nx = None, y0 = None, ny = None)
  
  Read a Gamma Software binary image using NumPy
  
  **Argument:**
  
  * filename: path to the file to read
  
  **Keyword arguments:** 
  
  Note: either par or width are mandatory
  
  * par:    ParFile object or path to the parameter file corresponding to the image
  * width:  image width
  * dtype:  data type ('double', 'fcomplex', 'float', 'scomplex', 'short', 'uchar') (default: either data type from parameter file or 'float' if not available)
  * x0:     offset to the first column (default: 0)
  * nx:     number of columns to read in the image (default: to the last column)
  * y0:     offset to the first row (default: 0)
  * ny:     number of rows to read in the image (default: to the last row)
  
  **Output**
  
  * the function returns a NumPy array containing the data from the image or -1 if not successful"""
  
  # get image width, as well as dtype if available
  par_dtype = ''
  if 'par' in kwargs:
    if isinstance(kwargs['par'], ParFile):
      pf = kwargs['par']
    else:
      pf = ParFile(kwargs['par'])
    for keyword in ['interferogram_width', 'range_samp_1', 'range_samples', 'width']:
      value = pf.get_value(keyword, dtype = int, index = 0)
      if value is not None:
        width = value
        break
    for keyword in ['image_format', 'data_type', 'data_format']:
      value = pf.get_value(keyword, index = 0)
      if value is not None:
        par_dtype = value
        break
  elif 'width' in kwargs:
    width = kwargs['width']
  else:
    print('ERROR: either par or width keyword arguments are mandatory\n')
    return -1
  
  # get boundaries
  x0 = 0
  y0 = 0
  nx = 0
  ny = 0
  if 'x0' in kwargs:
    x0 = int(kwargs['x0'])
  if 'nx' in kwargs:
    nx = int(kwargs['nx'])
  if 'y0' in kwargs:
    y0 = int(kwargs['y0'])
  if 'ny' in kwargs:
    ny = int(kwargs['ny'])
  
  # get data type and associated parameters
  is_scomplex = False
  if par_dtype:
    if par_dtype.lower() == 'double':
      bpp = 8
      dt = '>f8'
    elif par_dtype.lower() == 'fcomplex':
      bpp = 8
      dt = '>c8'
    elif par_dtype.lower() == 'float' or par_dtype.lower() == 'real*4':
      bpp = 4
      dt = '>f4'
    elif par_dtype.lower() == 'scomplex':
      bpp = 4
      dt = '>i2'
      is_scomplex = True
    elif par_dtype.lower() == 'short' or par_dtype.lower() == 'integer*2':
      bpp = 2
      dt = '>i2'
    elif par_dtype.lower() == 'uchar' or par_dtype.lower() == 'byte':
      bpp = 1
      dt = '>u1'
    else:
      print('ERROR: value for dtype not recognized: %s\n' % par_dtype)
      return -1
  else:
    # default: float image
    bpp = 4
    dt = '>f4'
    if 'dtype' in kwargs:
      if kwargs['dtype'].lower() == 'double':
        bpp = 8
        dt = '>f8'
      elif kwargs['dtype'].lower() == 'fcomplex':
        bpp = 8
        dt = '>c8'
      elif kwargs['dtype'].lower() == 'float':
        bpp = 4
        dt = '>f4'
      elif kwargs['dtype'].lower() == 'scomplex':
        bpp = 4
        dt = '>i2'
        is_scomplex = True
      elif kwargs['dtype'].lower() == 'short':
        bpp = 2
        dt = '>i2'
      elif kwargs['dtype'].lower() == 'uchar':
        bpp = 1
        dt = '>u1'
      else:
        print('ERROR: value for dtype not recognized: %s\n' % kwargs['dtype'])
        return -1
  
  # calculate nval and nlines, update image boundaries
  statinfo = os.stat(filename)
  nval = statinfo.st_size//bpp
  nlines = nval//width
  
  if x0 >= width:
    print("ERROR: the first column %d is greater than the number of columns in the file: %d" % (x0, width))
    return -1
  
  if y0 >= nlines:
    print("ERROR: the first line %d is greater than the number of lines in the file: %d" % (y0, nlines))
    return -1
  
  if nx == 0:
    nx = width - x0
  nx = min(nx, width - x0)
  
  if ny == 0:
    ny = nlines - y0
  ny = min(ny, nlines - y0)
  
  # open image file
  try:
    img = open(filename, "rb")
  except:
    print("ERROR: can not open data file: %s" % filename)
    return -1
  
  if y0 > 0:
    img.seek(y0*width*bpp, os.SEEK_SET)
  
  # read data
  cnt = ny*width
  if is_scomplex:
    scpx = np.fromfile(img, dtype=dt, count=2*cnt)
    scpx = np.reshape(scpx, (scpx.size//2, 2))
    data = np.empty((scpx.size//2,), dtype='c8')
    data = 1j*scpx[...,1];  data += scpx[...,0]
    data = data.astype('>c8')
    del(scpx)
  else:
    data = np.fromfile(img, dtype=dt, count=cnt)
  
  # close image file
  img.close()
  
  # crop rows
  data = np.reshape(data, (-1, width))
  data = data[:, x0:x0+nx]

  print("image:")
  print("  width: %d  number of lines: %d" % (width, nlines))
  print("data read from image:")
  print("  column offset (x0): %d  row offset (y0): %d  " % (x0, y0))
  print("  width: %d  number of lines: %d" % (nx, ny))

  return data

def read_point_data(filename, plist, **kwargs):
  """pdata = read_point_data(filename, plist, as_list = False, dim = 1, dtype = 'float', rec_num = None)
  
  Read a Gamma Software point data file as used in the IPTA package
  
  **Arguments:**
  
  * filename: path to the file to read
  * plist:    path to point list or array containing the point list
  
  **Keyword arguments:** 
  
  * as_list:  if True, returns a (nested) list instead of a NumPy array
  * dim:      dimensions of the data values (default: 1)
  * dtype:    data type ('double', 'fcomplex', 'float', 'int', 'scomplex', 'short', 'uchar') (default: 'float')
  * rec_num:  record number in input point data stack (starting with 1, None: read all records)
  
  **Output**
  
  * the function returns an array containing the point data or -1 if not successful"""
  
  # open point data
  try:
    pdata_file = open(filename, "rb")
  except:
    print("ERROR: can not open list of coordinates: %s" % filename)
    return -1
  
  if isinstance(plist, np.ndarray) or isinstance(plist, list):
    plist_arr = plist
  else:
    plist_arr = read_point_list(plist)
  
  shape_plist_arr = np.shape(plist_arr)
  nval = shape_plist_arr[0]
  
  dim = 1
  if 'dim' in kwargs:
    dim = int(kwargs['dim'])
  
  dt = '>f4'
  bpp = 4
  is_scomplex = False
  if 'dtype' in kwargs:
    if kwargs['dtype'].lower() == 'double':
      dt = '>f8'
      bpp = 8
    elif kwargs['dtype'].lower() == 'fcomplex':
      dt = '>c8'
      bpp = 8
    elif kwargs['dtype'].lower() == 'float':
      dt = '>f4'
      bpp = 4
    elif kwargs['dtype'].lower() == 'int':
      dt = '>i4'
      bpp = 4
    elif kwargs['dtype'].lower() == 'scomplex':
      dt = '>i2'
      bpp = 4
      is_scomplex = True
    elif kwargs['dtype'].lower() == 'short':
      dt = '>i2'
      bpp = 2
    elif kwargs['dtype'].lower() == 'uchar':
      dt = '>u1'
      bpp = 1
    else:
      print('ERROR: value for dtype not recognized: %s\n' % kwargs['dtype'])
      return -1
  
  # calculate nrecords
  statinfo = os.stat(filename)
  nval_file = statinfo.st_size//(bpp*dim)
  nrecords = nval_file//nval
  remainder = nval_file%nval
  
  if not remainder == 0:
    print("WARNING: the point data size does not seem to correspond to the point data size")
    print("         point list size: %d" % nval)
    print("         point data size: %d, dim: %d, number of records: %d, remainder: %d" % (nval_file, dim, nrecords, remainder))
  
  rec_num = -1
  if 'rec_num' in kwargs:
    if kwargs['rec_num']:
      rec_num = kwargs['rec_num'] - 1
      pdata_file.seek(rec_num*nval*dim*bpp, os.SEEK_SET)
  
  # read data
  if rec_num < 0 and nrecords > 1:
    if is_scomplex:
      scpx = np.fromfile(pdata_file, dtype=dt, count=2*dim*nval_file)
      scpx = np.reshape(scpx, (scpx.size//2, 2))
      pdata = np.empty((scpx.size//2,), dtype='c8')
      pdata = 1j*scpx[...,1];  pdata += scpx[...,0]
      pdata = pdata.astype('>c8')
    else:
      pdata = np.fromfile(pdata_file, dtype=dt)
    
    if dim == 1:
      pdata = np.reshape(pdata, (nrecords, nval))
    else:
      pdata = np.reshape(pdata, (nrecords, nval, dim))
    
  else:
    if is_scomplex:
      scpx = np.fromfile(pdata_file, dtype=dt, count=2*dim*nval)
      scpx = np.reshape(scpx, (scpx.size//2, 2))
      pdata = np.empty((scpx.size//2,), dtype='c8')
      pdata = 1j*scpx[...,1];  pdata += scpx[...,0]
      pdata = pdata.astype('>c8')
    else:
      pdata = np.fromfile(pdata_file, dtype=dt, count=dim*nval)
    
    if dim > 1:
      pdata = np.reshape(pdata, (nval, dim))
    
  # close point data file
  pdata_file.close()
  
  if 'as_list' in kwargs:
    if kwargs['as_list']:
      list_pdata = pdata.tolist()
      return list_pdata
  
  return pdata

def read_point_list(filename, **kwargs):
  """plist = read_point_list(filename, as_list = False, dtype = 'int')
  
  Read a Gamma Software point list as used in the IPTA package (list of x and y pixel coordinates)
  
  **Argument:**
  
  * filename: path to the file to read
  
  **Keyword arguments:** 
  
  * as_list:  if True, returns a (nested) list instead of a NumPy array
  * dtype:    data type ('double', 'float', 'int', 'short', 'uchar') (default: 'int')
  
  **Output**
  
  * the function returns an array containing the point list or -1 if not successful"""
  
  # open point list
  try:
    plist_file = open(filename, "rb")
  except:
    print("ERROR: can not open point list: %s" % filename)
    return -1
  
  dt = '>i4'
  
  if 'dtype' in kwargs:
    if kwargs['dtype'].lower() == 'double':
      dt = '>f8'
    elif kwargs['dtype'].lower() == 'float':
      dt = '>f4'
    elif kwargs['dtype'].lower() == 'int':
      dt = '>i4'
    elif kwargs['dtype'].lower() == 'short':
      dt = '>i2'
    elif kwargs['dtype'].lower() == 'uchar':
      dt = '>u1'
    else:
      print('ERROR: value for dtype not recognized: %s\n' % kwargs['dtype'])
      return -1
  
  plist = np.fromfile(plist_file, dtype=dt)
  plist = np.reshape(plist, (plist.size//2, 2))
  
  # close point list file
  plist_file.close()
  
  if 'as_list' in kwargs:
    if kwargs['as_list']:
      list_plist = plist.tolist()
      return list_plist
  
  return plist

def read_tab(filename, **kwargs):
  """tab = read_tab(filename, as_list = False, dtype = str, transpose = False)
  
  Read tab file into an array
  
  **Argument:**
  
  * filename: path to the file to read
  
  **Keyword arguments:** 
  
  * as_list:    if True, returns a (nested) list instead of a NumPy array
  * dtype:      output NumPy / Python type of array components (default: str)
  * transpose:  if True, apply a transpose to the array
  
  **Output**
  
  * the function returns an array containing the table or -1 if not successful"""
  
  np_arr = np.genfromtxt(filename, dtype = str)
  
  if 'dtype' in kwargs:
    np_arr = np_arr.astype(kwargs['dtype'])
  
  if 'transpose' in kwargs:
    if kwargs['transpose']:
      if np_arr.ndim == 1:
        np_arr = np.reshape(np_arr, (len(np_arr), -1))
      np_arr = np_arr.transpose()
  
  if 'as_list' in kwargs:
    if kwargs['as_list']:
      tab = np_arr.tolist()
      return tab
  
  return np_arr

def run_cmd(*cmd_args, **kwargs):
  """stat = run_cmd(cmd_arg1, cmd_arg2, ..., is_inter = False, cin = None, cout = None, cerr = None, errf = None, logf = None, stdout_flag = True, stderr_flag = True, wait = True)
  
  Run a shell command. Scripts must include a shebang (e.g. #!/usr/bin/env python) in their first line to run properly.
  
  **Argument:**
  
  * cmd_args: command with comma-separated argument(s) or given as a single string
  
  **Keyword arguments:**
  
  * is_inter:     is interactive program (boolean, default = False)
  * cin:          list to use as input of an interactive function
  * cout:         list where the stdout will be appended (list, has to be created before calling the function)
  * cerr:         list where the stderr will be appended (list, has to be created before calling the function)
  * errf:         error file where the stderr will be appended (string containing the path to the err file)
  * logf:         log file where the stdout will be appended (string containing the path to the log file)
  * stdout_flag:  print stdout to the console (boolean, default = True)
  * stderr_flag:  print stderr to the console (boolean, default = True)
  * wait:         wait for the subprocess to be finished (boolean, default = True)
  
  **Output:**
  
  * the function returns a status flag: 0: success, -1: failure"""
  
  if not cmd_args:
    print(run_cmd.__doc__)
    return -1
  
  prog = cmd_args[0].split(" ", 1)[0]
  
  prog_file = which(prog)
  
  if not prog_file:
    print('ERROR: command not found: %s' % prog)
    return -1
  
  # check if program is a script
  # read shebang
  script_file = io.open(prog_file, 'r', encoding="utf8", errors='ignore')
  shebang = script_file.readline()
  
  if ('python' in shebang):
    script = 'python'
  elif ('perl' in shebang):
    script = 'perl'
  elif ('bash' in shebang):
    script = 'bash'
  elif ('tcsh' in shebang):
    script = 'tcsh'
  elif ('csh' in shebang):
    script = 'csh'
  elif ('sh' in shebang):
    script = 'sh'
  else:
    script = None
  script_file.close()
  
  if script:
    args_list = []
    args_list.append(script)
    args_list.append(cmd_args[0].replace(prog, prog_file, 1))
    num = 0
    for arg in cmd_args:
      if num > 0:
        args_list.append(arg)
      num += 1
    args = tuple(args_list)
  else:
    args = cmd_args
  
  value = gamma_program('from_run_cmd', *args, **kwargs)
  
  return value

def update_image(arr, filename, **kwargs):
  """stat = update_image(arr, filename, par = None, width = None, nlines = None, dtype = None, x0 = None, y0 = None)
  
  Update a Gamma Software binary image using a NumPy array
  
  **Arguments:**
  
  * arr:      array that will be written to the file
  * filename: path to the file-to-be-updated
  
  Note: the file will be created if it does not exist yet
  
  **Keyword arguments:** 
  
  Note: either par or width are mandatory
  
  * par:    ParFile object or path to the parameter file corresponding to the file-to-be-updated
  * width:  image width of the file-to-be-updated
  * nlines: image height of the file-to-be-updated
  * dtype:  data type ('double', 'fcomplex', 'float', 'scomplex', 'short', 'uchar') (default: type from parameter file or current NumPy data type)
  * x0:     offset in the file-to-be-updated to the first column of the array (default: 0)
  * y0:     offset in the file-to-be-updated to the first row of the array (default: 0)
  
  **Output:**
  
  * the function returns a status flag: 0: success, -1: failure"""
  
  # get image width, as well as nlines and dtype if available
  par_dtype = ''
  nlines = 0
  if 'par' in kwargs:
    if isinstance(kwargs['par'], ParFile):
      pf = kwargs['par']
    else:
      pf = ParFile(kwargs['par'])
    for keyword in ['interferogram_width', 'range_samp_1', 'range_samples', 'width']:
      value = pf.get_value(keyword, dtype = int, index = 0)
      if value is not None:
        width = value
        break
    for keyword in ['interferogram_azimuth_lines', 'az_samp_1', 'azimuth_lines', 'nlines']:
      value = pf.get_value(keyword, dtype = int, index = 0)
      if value is not None:
        nlines = value
        break
    for keyword in ['image_format', 'data_type', 'data_format']:
      value = pf.get_value(keyword, index = 0)
      if value is not None:
        par_dtype = value
        break
  elif 'width' in kwargs:
    width = kwargs['width']
  else:
    print('ERROR: either par or width keyword arguments are mandatory\n')
    return -1
  
  # get boundaries
  x0 = 0
  y0 = 0
  if 'x0' in kwargs:
    x0 = int(kwargs['x0'])
  if 'y0' in kwargs:
    y0 = int(kwargs['y0'])
  
  np_arr = np.asarray(arr)
  shape_arr = np.shape(np_arr)
  nx = shape_arr[1]
  ny = shape_arr[0]
  
  # get data type and associated parameters
  is_scomplex = False
  
  np_dt = np_arr.__array_interface__['typestr']
  if is_verbose:
    print('NumPy array data type: %s, system endianness: %s' % (np_dt, sys.byteorder))
  
  if par_dtype:
    if par_dtype.lower() == 'double':
      bpp = 8
      dt = '>f8'
    elif par_dtype.lower() == 'fcomplex':
      bpp = 8
      dt = '>c8'
    elif par_dtype.lower() == 'float' or par_dtype.lower() == 'real*4':
      bpp = 4
      dt = '>f4'
    elif par_dtype.lower() == 'scomplex':
      bpp = 4
      dt = '>i2'
      is_scomplex = True
    elif par_dtype.lower() == 'short' or par_dtype.lower() == 'integer*2':
      bpp = 2
      dt = '>i2'
    elif par_dtype.lower() == 'uchar' or par_dtype.lower() == 'byte':
      bpp = 1
      dt = '>u1'
    else:
      print('ERROR: value for dtype not recognized: %s\n' % par_dtype)
      return -1
  elif 'dtype' in kwargs:
    if kwargs['dtype'].lower() == 'double':
      bpp = 8
      dt = '>f8'
    elif kwargs['dtype'].lower() == 'fcomplex':
      bpp = 8
      dt = '>c8'
    elif kwargs['dtype'].lower() == 'float':
      bpp = 4
      dt = '>f4'
    elif kwargs['dtype'].lower() == 'scomplex':
      bpp = 4
      dt = '>i2'
      is_scomplex = True
    elif kwargs['dtype'].lower() == 'short':
      bpp = 2
      dt = '>i2'
    elif kwargs['dtype'].lower() == 'uchar':
      bpp = 1
      dt = '>u1'
    else:
      print('ERROR: value for dtype not recognized: %s\n' % kwargs['dtype'])
      return -1
  else:
    bpp = np_arr.dtype.itemsize
    dt = np_dt
    if '<' in dt:
      dt = dt.replace('<', '>')
    elif '=' in dt and sys.byteorder == 'little':
      dt = dt.replace('=', '>')
  
  if not 'c' in np_dt and 'c' in dt:
    print("ERROR: array is complex while file type is real")
    return -1
  
  if not 'c' in dt and 'c' in np_dt and not is_scomplex:
    print("ERROR: array is real while file type is complex")
    return -1
  
   # open image file
  if os.path.isfile(filename):
    exists = True
    try:
      img = open(filename, "r+b")
    except:
      print("ERROR: can not open data file: %s" % filename)
      return -1
  else:
    exists = False
    try:
      img = open(filename, "wb")
    except:
      print("ERROR: can not open data file: %s" % filename)
      return -1
  
  # calculate nval and nlines, update image boundaries
  if exists:
    statinfo = os.stat(filename)
    nval = statinfo.st_size//bpp
    nlines = nval//width
  elif 'nlines' in kwargs:
    nlines = kwargs['nlines']
  elif nlines == 0:
    nlines = y0 + ny
  
  if x0 >= width:
    print("ERROR: the first column %d is greater than the number of columns in the file: %d" % (x0, width))
    return -1
  
  if y0 >= nlines:
    print("ERROR: the first line %d is greater than the number of lines in the file: %d" % (y0, nlines))
    return -1
  
  if x0 + nx > width or y0 + ny > nlines:
    print("WARNING: part of the array is outside the file bounds, this part will be cropped")
  
  nx = min(nx, width - x0)
  ny = min(ny, nlines - y0)
  
  # read block if file exists
  if exists:
    if y0 > 0:
      img.seek(y0*width*bpp, os.SEEK_SET)
    
    cnt = ny*width
    if is_scomplex:
      scpx = np.fromfile(img, dtype=dt, count=2*cnt)
      scpx = np.reshape(scpx, (scpx.size//2, 2))
      data = np.empty((scpx.size//2,), dtype='c8')
      data = 1j*scpx[...,1];  data += scpx[...,0]
      data = data.astype('>c8')
      del(scpx)
    else:
      data = np.fromfile(img, dtype=dt, count=cnt)
    data = np.reshape(data, (-1, width))
  else:
    # create array with zeros if file does not exist
    if is_scomplex:
      data = np.zeros((ny, width), dtype=np_dt)
    else:
      data = np.zeros((ny, width), dtype=dt)
  
  # replace existing data by array
  data[:, x0:x0+nx] = np_arr
  
  # prepare output
  if is_scomplex:
    cpx = np.empty(2*data.size, dtype='>f4')
    cpx = np.reshape(cpx, (cpx.size//2, 2))
    data = np.reshape(data, data.size)
    cpx[...,0] = data.real
    cpx[...,1] = data.imag
    data = np.reshape(cpx, (ny, 2*width))
    del(cpx)
  
  if exists:
    if y0 > 0:
      img.seek(y0*width*bpp, os.SEEK_SET)
  else:
    if y0 > 0:
      line = np.zeros((1, np.shape(data)[1]), dtype=dt)
      for y in range(y0):
        line.tofile(img, '')
  
  # update image file
  data = data.astype(dt)
  data.tofile(img, '')
  
  if not exists and nlines > y0 + ny:
    line = np.zeros((1, np.shape(data)[1]), dtype=dt)
    for y in range(nlines - (y0 + ny)):
      line.tofile(img, '')
  
  # close image file
  img.close()
  
  return 0

def which(file):
  """file_path = which(file)
  
  Search if file exists, including in PATH and Gamma Software packages
  
  **Arguments:**
  
  * file: searched file
  
  **Output**

  * the function returns the path to the file when successful, None otherwise"""
  fpath, fname = os.path.split(file)
  if fpath:
    if os.path.isfile(file):
      return file
    if sys.platform == 'win32':
      file_exe = file + '.exe'
      if os.path.isfile(file_exe):
        return file_exe
  else:
    for path in gamma_env["PATH"].split(os.pathsep):
      path_file = os.path.join(path, file)
      if os.path.isfile(path_file):
        return path_file
    if sys.platform == 'win32':
      file_exe = file + '.exe'
      for path in gamma_env["PATH"].split(os.pathsep):
        path_file = os.path.join(path, file_exe)
        if os.path.isfile(path_file):
          return path_file
  return None

def write_image(arr, filename, **kwargs):
  """stat = write_image(arr, filename, dtype = None, x0 = None, nx = None, y0 = None, ny = None)
  
  Write a Gamma Software binary image from a 2D array
  
  **Arguments:**
  
  * arr:      array that will be written to the file (NumPy array or nested list)
  * filename: path to the file to write
  
  **Keyword arguments:** 
  
  * dtype:  data type ('double', 'fcomplex', 'float', 'scomplex', 'short', 'uchar') (default: current NumPy data type)
  * x0:     offset to the first column (default: 0)
  * nx:     number of columns to write in the image (default: to the last column)
  * y0:     offset to the first row (default: 0)
  * ny:     number of rows to write in the image (default: to the last row)
  
  **Output:**
  
  * the function returns a status flag: 0: success, -1: failure"""
  
  # get boundaries
  x0 = 0
  y0 = 0
  nx = 0
  ny = 0
  if 'x0' in kwargs:
    x0 = int(kwargs['x0'])
  if 'nx' in kwargs:
    nx = int(kwargs['nx'])
  if 'y0' in kwargs:
    y0 = int(kwargs['y0'])
  if 'ny' in kwargs:
    ny = int(kwargs['ny'])
  
  # open image file
  try:
    img = open(filename, "wb")
  except:
    print("ERROR: can not open data file: %s" % filename)
    return -1
  
  np_arr = np.asarray(arr)
  shape_arr = np.shape(np_arr)
  width = shape_arr[1]
  nlines = shape_arr[0]

  # crop array
  if x0 >= width:
    print("ERROR: the first column %d is greater than the number of columns in the array: %d" % (x0, width))
    return -1
  
  if y0 >= nlines:
    print("ERROR: the first line %d is greater than the number of lines in the array: %d" % (y0, nlines))
    return -1
  
  if nx == 0:
    nx = width - x0
  nx = min(nx, width - x0)
  
  if ny == 0:
    ny = nlines - y0
  ny = min(ny, nlines - y0)
  
  np_arr = np_arr[y0:y0+ny+1, x0:x0+nx+1]
  
  dt = np_arr.__array_interface__['typestr']
  if is_verbose:
    print('NumPy array data type: %s, system endianness: %s' % (dt, sys.byteorder))
  
  is_scomplex = False
  if '<' in dt:
    dt = dt.replace('<', '>')
  elif '=' in dt and sys.byteorder == 'little':
    dt = dt.replace('=', '>')
  
  if 'dtype' in kwargs:
    if kwargs['dtype'].lower() == 'double':
      dt = '>f8'
    elif kwargs['dtype'].lower() == 'fcomplex':
      dt = '>c8'
    elif kwargs['dtype'].lower() == 'float':
      dt = '>f4'
    elif kwargs['dtype'].lower() == 'scomplex':
      dt = '>i2'
      is_scomplex = True
    elif kwargs['dtype'].lower() == 'short':
      dt = '>i2'
    elif kwargs['dtype'].lower() == 'uchar':
      dt = '>u1'
    else:
      print('ERROR: value for dtype not recognized: %s\n' % kwargs['dtype'])
      return -1
  
  if is_scomplex:
    cpx = np.empty(2*np_arr.size, dtype='>f4')
    cpx = np.reshape(cpx, (cpx.size//2, 2))
    np_arr = np.reshape(np_arr, np_arr.size)
    cpx[...,0] = np_arr.real
    cpx[...,1] = np_arr.imag
    np_arr = np.reshape(cpx, (shape_arr[0], 2*shape_arr[1]))
    del(cpx)
  
  np_arr = np_arr.astype(dt)
  np_arr.tofile(img, '')
  
  img.close()
  return 0

def write_point_data(pdata, plist, filename, **kwargs):
  """stat = write_point_data(pdata, plist, filename, dtype = None, rec_num = None)
  
  Write a Gamma Software binary point data file as used in the IPTA package
  
  **Arguments:**
  
  * pdata:    array containing the point data that will be written to the file
  * plist:    path to point list or array containing the point list
  * filename: path to the file to write
  
  **Keyword arguments:** 
  
  * dtype:    data type ('double', 'fcomplex', 'float', 'int', 'scomplex', 'short', 'uchar') (default: current NumPy data type)
  * rec_num:  record number in output point data file (starting with 1, None: write all records)
  
  **Output:**
  
  * the function returns a status flag: 0: success, -1: failure"""
  
  # open output file
  try:
    pdata_file = open(filename, "wb")
  except:
    print("ERROR: can not open output file: %s" % filename)
    return -1
  
  if isinstance(plist, np.ndarray) or isinstance(plist, list):
    plist_arr = plist
  else:
    plist_arr = read_point_list(plist)
  
  shape_plist_arr = np.shape(plist_arr)
  nval = shape_plist_arr[0]
  
  np_pdata = np.asarray(pdata)
  shape_pdata_arr = np.shape(np_pdata)
  
  nrecords = 1
  if len(shape_pdata_arr) > 1:
    if shape_pdata_arr[1] == nval:
      nrecords = shape_pdata_arr[0]
  
  if nrecords > 1:
    if 'rec_num' in kwargs:
      np_pdata = np_pdata[kwargs['rec_num'] - 1, ...]
  
  dt = np_pdata.__array_interface__['typestr']
  if is_verbose:
    print('NumPy array data type: %s, system endianness: %s' % (dt, sys.byteorder))
  
  is_scomplex = False
  if '<' in dt:
    dt = dt.replace('<', '>')
  elif '=' in dt and sys.byteorder == 'little':
    dt = dt.replace('=', '>')
  
  if 'dtype' in kwargs:
    if kwargs['dtype'].lower() == 'double':
      dt = '>f8'
    elif kwargs['dtype'].lower() == 'fcomplex':
      dt = '>c8'
    elif kwargs['dtype'].lower() == 'float':
      dt = '>f4'
    elif kwargs['dtype'].lower() == 'int':
      dt = '>i4'
    elif kwargs['dtype'].lower() == 'scomplex':
      dt = '>i2'
      is_scomplex = True
    elif kwargs['dtype'].lower() == 'short':
      dt = '>i2'
    elif kwargs['dtype'].lower() == 'uchar':
      dt = '>u1'
    else:
      print('ERROR: value for dtype not recognized: %s\n' % kwargs['dtype'])
      return -1
  
  if is_scomplex:
    cpx = np.empty(2*np_pdata.size, dtype='>f4')
    cpx = np.reshape(cpx, (cpx.size//2, 2))
    np_pdata = np.reshape(np_pdata, np_pdata.size)
    cpx[...,0] = np_pdata.real
    cpx[...,1] = np_pdata.imag
    np_pdata = np.reshape(cpx, cpx.size)
    del(cpx)
  else:
    np_pdata = np.reshape(np_pdata, np_pdata.size)
  
  np_pdata = np_pdata.astype(dt)
  np_pdata.tofile(pdata_file, '')
  
  pdata_file.close()
  return 0

def write_point_list(plist, filename, **kwargs):
  """stat = write_point_list(plist, filename, dtype = None)
  
  Write a Gamma Software point list as used in the IPTA package (list of x and y pixel coordinates) from a two-columns array
  
  **Arguments:**
  
  * plist:    two-columns array that will be written to the point list file
  * filename: path to the file to write
  
  **Keyword argument:** 
  
  * dtype:  data type ('double', 'float', 'int', 'short', 'uchar') (default: current NumPy data type)
  
  **Output:**
  
  * the function returns a status flag: 0: success, -1: failure"""
  
  # open binary file
  try:
    plist_file = open(filename, "wb")
  except:
    print("ERROR: can not open point list file: %s" % filename)
    return -1
  
  np_plist = np.asarray(plist)
  np_plist = np.reshape(np_plist, (np_plist.size, 1))
  
  dt = np_plist.__array_interface__['typestr']
  if is_verbose:
    print('NumPy array data type: %s, system endianness: %s' % (dt, sys.byteorder))
  
  if '<' in dt:
    dt = dt.replace('<', '>')
  elif '=' in dt and sys.byteorder == 'little':
    dt = dt.replace('=', '>')
  
  if 'dtype' in kwargs:
    if kwargs['dtype'].lower() == 'double':
      dt = '>f8'
    elif kwargs['dtype'].lower() == 'float':
      dt = '>f4'
    elif kwargs['dtype'].lower() == 'int':
      dt = '>i4'
    elif kwargs['dtype'].lower() == 'short':
      dt = '>i2'
    elif kwargs['dtype'].lower() == 'uchar':
      dt = '>u1'
    else:
      print('ERROR: value for dtype not recognized: %s\n' % kwargs['dtype'])
      return -1
  
  np_plist = np_plist.astype(dt)
  np_plist.tofile(plist_file, '')
  
  plist_file.close()
  return 0

def write_tab(arr, filename, **kwargs):
  """stat = write_tab(arr, filename, transpose = False)
  
  Write array into tab file (text file)
  
  **Arguments:**
  
  * arr:      array that will be written to the file
  * filename: path to the file to write
  
  **Keyword argument:** 
  
  * transpose:  if True, apply a transpose to the array
  
  **Output:**
  
  * the function returns a status flag: 0: success, -1: failure"""
  
  np_arr = np.asarray(arr)
  
  if np_arr.ndim == 1:
    np_arr = np.reshape(arr, (len(arr), -1))
    np_arr = np_arr.transpose()
  
  if 'transpose' in kwargs:
    if kwargs['transpose']:
      np_arr = np_arr.transpose()
  
  # save tab file
  try:
    np.savetxt(filename, np_arr, fmt = '%s')
  except:
    print("ERROR: can not save file: %s" % filename)
    return -1
  
  return 0

# the following code is executed when importing py_gamma
initialize()

# class definition
class ParFile:
  """Class for reading, manipulating, and writing Gamma Software parameter files
  
  **Initialize object:** open and read parameter file, and store parameter keys and values in "par_dict" and "par_keys"
  
  PF = ParFile(input_file)
  
  Note: if no "input_file" is entered, an empty ParFile object will be initialized
  
  **Methods:**
  
  * dump():                           print all key/value pairs
  * d_out = get_dict(**kwargs)        get item(s) from the ParFile object as an ordered dictionary
  * val = get_value(key, **kwargs):   get value for key
  * set_value(key, value, **kwargs):  set value for key (can be a new key)
  * update_from_dict(d_in):           update ParFile object using item(s) in a dictionary
  * write_par(output_file):           write Gamma Software parameter file with key/value pairs separated by ":"
  
  **Description of the variables:**
  
  * input_file:   input parameter filename or file object
  * output_file:  output parameter filename or file object
  * key:          name of a parameter from the parameter file
  * value:        value(s) for a defined key
  * par_dict:     dict of parameter keys and values
  * par_keys:     ordered list of keys (dict is not keeping sequence)"""
  
  par_dict = {}  # dict of parameter key and value
  par_keys = []  # ordered list of keys (dict is not keeping sequence)

  def __init__(self, *args):
    """Initialize object: open and read parameter file, and store parameter keys and values in "par_dict" and "par_keys" """
    par_dict = {}
    par_keys = []
    
    if len(args) > 0:
      input_file = args[0]
      if isinstance(input_file, str):
        pf = io.open(input_file, 'r', encoding="utf8", errors='ignore')
        file_name = True
      else:
        try:
          if isinstance(input_file, io.TextIOWrapper):
            pf = input_file
            file_name = False
          else:
            print('ERROR: invalid input_file')
            return -1
        except:
          try:
            if isinstance(input_file, file):
              pf = input_file
              file_name = False
            else:
              print('ERROR: invalid input_file')
              return -1
          except:
            print('ERROR: invalid input_file')
            return -1
      kv = []
      pv = []
      line = pf.readline()  # read line
  
      while (line):
        if line[0] == '#' or len(line.strip()) == 0:  # ignore blank lines and lines starting with #
          line = pf.readline()    # read next line
          continue
  
        kv = line.partition(":")  # use partition builtin function split line into a tuple of 3 strings (keyword, sep, value)
        if kv is None or len(kv) < 3 or kv[1] == '':
          line = pf.readline()    # read next line
          continue
  
        key = kv[0].strip()
        par_keys.append(key)              # save keys
        p2 = kv[2].split('#')[0].strip()  # parse only everything in front of a comment and remove leading and trailing whitespace
        if p2 == '':
          line = pf.readline()    # read next line
          continue
          
        if p2[0] == "[":                  # test if data are in list notation
          try:
            pv = ast.literal_eval(p2)     # interpret string as a list and convert to a list
          except:
            print('ERROR: string value cannot be interpreted as a Python list: ', p2, type(p2))
            return -1
        elif p2[0] == "{":                # test if data are in dictionary notation
          try:
            pv = ast.literal_eval(p2)
          except:
            print('ERROR: string value cannot be interpreted as a Python dictionary: ', p2, type(p2))
            return -1
        elif len(p2.split('"')) == 3:     # test if value is in quotes, create a list and add the value
          pv = []
          pv.append(p2)
        else:
          params = p2.replace(',', ' ')   # replace commas with whitespace for compatibility
          pv = params.split()             # split remaining parameters using whitespace as delimiter
          for i in range(len(pv)):
            pv[i] = pv[i].strip()         # remove any whitespace from each parameter
  
        par_dict[key] = pv      # store in dictionary
        line = pf.readline()    # read next line
  
      self.par_dict = par_dict  # store dict
      self.par_keys = par_keys  # store keyword list
      
      if file_name:
        pf.close()

  def dump(self):
    """dump()
    
    Print all key/value pairs to the Python console"""
    
    # print all key/value pairs
    for key in self.par_keys:
      print("%s:\t\t %s" % (key, self.par_dict[key]))
    return
  
  def get_dict(self, **kwargs):
    """d_out = get_dict(key = None, index = None)
    
    Get item(s) from the ParFile object as an ordered dictionary
    
    **Keyword arguments:** 
    
    * key:    string to be searched in the keywords of the Parfile object (default: None)
    * index:  index of the item(s), e.g. for state vectors or burst parameters in tops_par files (0: item(s) without index, default: None, i.e. all indices)
    
    **Output**
    
    * returns an ordered dictionary matching the key and index given as input
    
    Note: for older Python versions, the output is a normal dictionary"""
    
    key_in = ''
    if 'key' in kwargs:
      key_in = kwargs['key']
    
    index_in = ''
    index_num = True
    if 'index' in kwargs:
      if kwargs['index'] != 0 and kwargs['index'] != '0':
        if isinstance(kwargs['index'], str):
          index_in = '_' + kwargs['index']
        else:
          index_in = str(kwargs['index'])
      else:
        index_num = False
    
    if is_ordered:
      d_out = OrderedDict()
    else:
      d_out = {}
      
    for key in self.par_keys:
      if key_in in key:
        if index_in in key[-len(index_in):]:
          d_out[key] = self.par_dict[key]
          if not index_num:
            for num in range(len(self.par_keys)):
              txt = '_' + str(num)
              if txt in key[-len(txt):]:
                d_out.pop(key, None)
    
    return d_out
    
  def get_value(self, key, **kwargs):
    """val = get_value(key, dtype = str, index = None)
  
    Get value for key
    
    **Argument:**
    
    * key: keyword of the dictionary corresponding to the parameter file
    
    **Keyword arguments:** 
    
    * dtype:  output Python type (default: str)
    * index:  get only one item of the output list (default: whole list corresponding to keyword)
    
    **Output**
    
    * returns a value or a list corresponding to the keyword and index"""
    
    # get value for key
    if key in self.par_dict:
      value_list = self.par_dict[key]
      
      if 'dtype' in kwargs:
        for i in range(len(value_list)):
          try:
            value_list[i] = kwargs['dtype'](value_list[i])
          except:
            continue
      
      if 'index' in kwargs:
        output = value_list[kwargs['index']]
        return output
      
      if len(value_list) == 1:
        output = value_list[0]
        return output
      else:
        return value_list
    else:
      return None  # if key does not exist
  
  def update_from_dict(self, d_in):
    """update_from_dict(d_in)
    
    Update ParFile object using item(s) in a dictionary.
    
    **Argument:**
    
    * d_in: dictionary or ordered dictionary used for updating ParFile object"""
    key_not_found = []
    
    for key_in in d_in.keys():
      key_found = False
      for key_pf in self.par_dict.keys():
        if key_in == key_pf:
          self.par_dict[key_pf] = d_in[key_in]
          key_found = True
          break
      if not key_found:
        key_not_found.append(key_in)
    
    if key_not_found:
      print('WARNING: One or several keywords in the input dictionary were not found in the ParFile object and were ignored:')
      print(key_not_found)
    return
  
  def remove_key(self, key):
    """remove_value(key)
  
    Remove key and associated value
    
    **Argument:**
    
    * key: keyword of the dictionary corresponding to the parameter file"""
    
    self.par_dict.pop(key, None)

    try:
      item = self.par_keys.index(key)
      del self.par_keys[item]
    except:
      pass
    return

  def set_value(self, key, value, **kwargs):
    """set_value(key, value, index = None)
    
    Set value for key (can be a new key)
    
    **Arguments:**
    
    * key:    keyword of the dictionary corresponding to the parameter file
    * value:  value corresponding to the keyword
    
    **Keyword argument:** 
    
    * index:  set only one item in the list corresponding to the keyword"""
    
    if not key in self.par_keys:
      self.par_keys.append(key) # append new key to list
      
    if 'index' in kwargs:
      if key in self.par_dict:
        self.par_dict[key][kwargs['index']] = str(value)
      else:
        self.par_dict[key] = [str(value)]
    else:
      if isinstance(value, list):
        self.par_dict[key] = list(map(str, value))
      else:
        self.par_dict[key] = [str(value)]
    return

  def write_par(self, output_file):
    """write_par(output_file)
    
    Write Gamma Software parameter file with key/value pairs separated by ":"
    
    **Argument:**
    
    * output_file:  output parameter filename or file object"""
    
    # write key/value pairs separated by :
    if isinstance(output_file, str):
      pf = io.open(output_file, 'w+', encoding="utf8", errors='ignore')
      file_name = True
    else:
      try:
        if isinstance(output_file, io.TextIOWrapper):
          pf = output_file
          file_name = False
        else:
          print('ERROR: invalid output_file')
          return
      except:
        try:
          if isinstance(output_file, file):
            pf = output_file
            file_name = False
          else:
            print('ERROR: invalid output_file')
            return
        except:
          print('ERROR: invalid output_file')
          return
    tstr = ""
    for key in self.par_keys:
      if (type(self.par_dict[key])) == list:
        for i in range(len(self.par_dict[key])):
          if i == 0:
            tstr = self.par_dict[key][i]
          else:
            tstr = "%s %s" % (tstr, self.par_dict[key][i])
        pf.write("%s: %s\n" % (key, tstr))
      else :
        pf.write("%s: %s\n" % (key, self.par_dict[key]))
    if file_name:
      pf.close()
    return
