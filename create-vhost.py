#!/usr/bin/env python

import optparse, re, os, time, urllib2

apache_port = 80

class vHost:


    domain = None
    www_dir = None
    use_pub = False
    git_url = None

    def __init__(self):


        if domain is None:
            raise BaseException('Domain not set!')

        if www_dir is None:
            raise BaseException('WWW root directory not set!')

        # check if the www_dir already exists, i
        if os.path.exists(www_dir):


        if not str(apache_port).isdigit():
            raise BaseException('The apache port is not valid!')

        # check the git repo if it has been set
        if git_url is not None:
            self._check_git(git_url)


    def create(self):

        print 'Creating new vhost...'
        time.sleep(1)

        return True

    # this method checks if the given git repository is valid
    def _check_git(self, url):

        try:
            data = urllib2.urlopen(url)
        except Exception as e:
            raise BaseException('GIT repo \'%s\' could not be read' % url)


def main():
    global use_pub, apache_port, domain, www_dir, git_url

    p = optparse.OptionParser()
    p.add_option('--interactive', '-i', default=False, help="Run this script interactively")
    p.add_option('--use_public_dir', '-p', default='yes', help="Use the /public directory as the document root")
    p.add_option('--domain', '-d', default=None, help="Set the domain of this vhost")
    p.add_option('--www_dir', '-w', default=None, help="Set the root directory for this vhost")
    p.add_option('--git_url', '-g', default=None, help="Set the GIT repository URL")
    p.add_option('--apache_port', '-P', default=80, help="Override the apache port")
    options, arguments = p.parse_args()

    if options.use_public_dir != 'yes' and options.use_public_dir != 'no':
        print 'Invalid option --use_public_dir', options.use_public_dir
        p.print_help()
        exit()
    else:
        use_pub = True if options.use_public_dir == 'yes' else False

    # validate the given domain name
    if not re.match("^(([a-zA-Z0-9]+([\-])?[a-zA-Z0-9]+)+(\.)?)+[a-zA-Z]{2,6}$", str(options.domain)):
        print 'Invalid option --domain', options.domain
        p.print_help()
        exit()
    else:
        domain = options.domain


    # set the options
    www_dir = options.www_dir
    git_url = options.git_url
    apache_port = options.apache_port

    if options.interactive:

        interactive()


    # try and create the vhost
    try:
        vHost().create()

    except BaseException as exc:
        print 'The following error occurred: %s' % exc

# run interactive mode
def interactive():
    global domain, www_dir, use_pub

    domain = input('Please enter the root domain for this vhost: ')
    www_dir = input('Please enter the www directory: ')
    use_pub = input('Use public dir? [y/N] ')



if __name__ == '__main__':
    main()