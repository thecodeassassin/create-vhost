<VirtualHost *:{APACHE_PORT}>
    ServerName {DOMAIN}
    ServerAlias www.{DOMAIN}
    DocumentRoot "{WWW_DIR}"
    <Directory "{WWW_DIR}">
        AllowOverride All
        Order allow,deny
        Allow from all
        Require all granted
    </Directory>
</VirtualHost>
