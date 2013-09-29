#!/usr/bin/env python
from _socket import getservbyport
from subprocess import Popen

import optparse, re, os, time, urllib2, ConfigParser, subprocess

domain = None
www_dir = None
git_url = None
do_git_checkout = False
assume_yes = False

if not os.access('/etc/hosts', os.W_OK):
    exit('Cannot write to /etc/hosts, please run this script as root or with sudo')

if not os.access('vhost.tpl', os.W_OK):
    exit('Cannot read vhost template file!')

cfg = ConfigParser.ConfigParser()
configfile = 'create-vhost.ini'

print '--- Create vhost script for Apache2 ---'
print '--- Copyright Stephen Hoogendijk 2013, Licensed under the GPL V2 License ---'
print

if not os.path.exists(configfile):
    exit('Cannot find config file %s' % configfile)

try:
    cfg.read(configfile)
except ConfigParser.ParsingError as exc:
    exit('Parse error: %s' % exc)

try:
    apache_port = int(cfg.get('apache', 'port'))
    vhost_path = cfg.get('apache', 'vhost_path')
    apache_exec = cfg.get('apache', 'apache_exec')
    git_exec = cfg.get('git', 'exec')
except Exception as exc:
    exit('Config file invalid, please check %s' %configfile)



def main():
    global assume_yes, domain, www_dir, git_url

    p = optparse.OptionParser()
    p.add_option('--interactive', '-i', action="store_true", help="Run this script interactively")
    p.add_option('--domain', '-d', default=None, help="Set the domain of this vhost")
    p.add_option('--www_dir', '-w', default=None, help="Set the root directory for this vhost")
    p.add_option('--git_url', '-g', default=None, help="Set the GIT repository URL")
    p.add_option('-y', action="store_true", help="Assume yes to all queries and do not prompt (unless going interactive)")
    options, arguments = p.parse_args()

    if (options.domain is None or options.www_dir is None) and options.interactive is not True:
        p.print_help()
        exit()

    if options.y:
        assume_yes = True

    if options.interactive:
        interactive()
    else:
        # set the options
        domain = options.domain
        www_dir = options.www_dir
        git_url = options.git_url

        # create the vhost (from options)
        create_vhost()



# run interactive mode
def interactive():
    global domain, www_dir, git_url

    domain = raw_input('Please enter the root domain for this vhost: ')
    www_dir = raw_input('Please enter the www directory: ')
    git_url = raw_input('(optional) Clone from GIT url: ')

    #create the vhost
    create_vhost()

# first check the requirements, then create the vhost
def create_vhost():
    _check_vhost()
    _check_apache()

    print '\nCreating new vhost...\n'
    time.sleep(1)

    # create the www dir if it does not exist
    if not os.path.exists(www_dir):
        os.mkdir(www_dir, 0775)


    # read the template and replace the variables
    vhost_tpl = open('vhost.tpl', 'r').read()


    vhost_tpl = vhost_tpl.replace('{APACHE_PORT}', str(apache_port))
    vhost_tpl = vhost_tpl.replace('{DOMAIN}', domain)
    vhost_tpl = vhost_tpl.replace('{WWW_DIR}', www_dir)

    new_vhost = '%s/vhost_%s.conf' % (vhost_path, domain)


    # if the vhost file does not exist, create it
    if not os.path.exists(new_vhost):
        vhost_file = open(new_vhost, 'w')
        vhost_file.write(vhost_tpl)
        vhost_file.close()

    # add the host to /etc/hosts
    _add_host(domain)
    _add_host('www.%s' % domain)


    if do_git_checkout is True:
        subprocess.call('%s clone %s %s' % (git_exec, git_url, www_dir), shell=True)

    # restart apache
    subprocess.call('%s restart' % apache_exec, shell=True)

    #done!
    print '\nFinished creating new vhost %s!' % domain
    return True

# check the vhost requirements
def _check_vhost():
    global do_git_checkout

    if not os.path.exists(www_dir) and not assume_yes:
        sure_dir = raw_input('Your given www-dir does not exist, it will be created automatically ' +
                             'but will be owned by root, continue? [N/y]')

        if str(sure_dir).lower() != 'y':
            exit('Exit due to user input')

    if domain is None or domain == '':
        exit('Domain not set!')

    if www_dir is None or www_dir == '':
        exit('WWW root directory not set!')

    # check if the www_dir already exists, check if the
    if os.path.exists(www_dir):
        if len(os.listdir(www_dir)) != 0 and git_url is not None and git_url != '':
            exit('Cannot clone git repository in a non-empty directory!')

    if not str(apache_port).isdigit():
        exit('The apache port is not valid!')

    # validate the given domain name
    if not re.match("^(([a-zA-Z0-9]+([\-])?[a-zA-Z0-9]+)+(\.)?)+[a-zA-Z]{2,6}$", str(domain)) and 'www' not in domain:
        exit('Domain not valid: %s. Please enter a domain without www' % domain)

    # check the git repo if it has been set
    if git_url is not None and git_url != '':
        _check_git(git_url)
        do_git_checkout = True

# check the apache requirements
def _check_apache():
    try:
        if getservbyport(apache_port) not in ['http', 'www', 'apache2']:
            exit('Apache does not seem to be running on port %d' % apache_port)
    except Exception:
        exit('Error while trying to poll for apache, please check the config setting apache->port')

# this method checks if the given git repository is valid
def _check_git(url):

    if not _which(git_exec):
        exit('Cannot execute local git installation on: %s' % git_exec)

    try:
        urllib2.urlopen(url)
    except Exception as e:
        exit('GIT repo \'%s\' could not be read' % url)


def _which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def _add_host(host):
    host_line = '127.0.0.1    %s' % host

    hosts_file = open('/etc/hosts', 'r')
    host_list = hosts_file.readlines()
    hosts_file.close()
    found = False
    for line in host_list:
        if str(host_line) in line:
            found = True

    if not found:
        hosts_file = open('/etc/hosts', 'a')
        hosts_file.write(str(host_line)+"\n")
        hosts_file.close()

if __name__ == '__main__':
    main()