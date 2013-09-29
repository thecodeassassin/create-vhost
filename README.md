create-vhost
============

A creation script for apache2 vhosts written in Python

Setup
============
Configure the script by editing create-vhost.ini and vhost.tpl.

You can execute the script by making it executable:

$ chmod +x create-vhost.py

Then execute the script (with the optional parameters):

$ ./create-vhost.py

Usage: create-vhost.py [options]

Options:
  -h, --help            show this help message and exit
  -i, --interactive     Run this script interactively
  -d DOMAIN, --domain=DOMAIN
                        Set the domain of this vhost
  -w WWW_DIR, --www_dir=WWW_DIR
                        Set the root directory for this vhost
  -g GIT_URL, --git_url=GIT_URL
                        Set the GIT repository URL
  -y                    Assume yes to all queries and do not prompt (unless
                        going interactive)