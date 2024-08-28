{% macro constants_php(values, es_password) -%}
<?php
    namespace diskover;
    class Constants {
        const TIMEZONE = '{{ values.TZ }}';
        const ES_HOST = '{{ values.consts.elastic_search_container_name }}';
        const ES_PORT = {{ values.consts.elastic_port }};
        const ES_USER = '{{ values.consts.elastic_basic_auth_user }}';
        const ES_PASS = '{{ es_password }}';
        // if your Elasticsearch cluster uses HTTP TLS/SSL, set ES_HTTPS to TRUE
        // override with env var ES_HTTPS
        const ES_HTTPS = FALSE;
        // login auth for diskover-web
        const LOGIN_REQUIRED = TRUE;
        // default username and password to login
        // the password is no longer used after first login, a hashed password gets stored in separate sqlite db
        const USER = '{{ values.diskover_data.username }}';
        const PASS = '{{ values.diskover_data.password }}';
        // default results per search page
        const SEARCH_RESULTS = 50;
        // default size field (size, size_du) to use for sizes on file tree and charts
        const SIZE_FIELD = 'size';
        // default file types, used by quick search (file type) and dashboard file type usage chart
        // additional extensions can be added/removed from each file types list
        const FILE_TYPES = [
            'docs' => ['doc', 'docx', 'odt', 'pdf', 'tex', 'wpd', 'wks', 'txt', 'rtf', 'key', 'odp', 'pps', 'ppt', 'pptx', 'ods', 'xls', 'xlsm', 'xlsx'],
            'images' => ['ai', 'bmp', 'gif', 'ico', 'jpeg', 'jpg', 'png', 'ps', 'psd', 'psp', 'svg', 'tif', 'tiff', 'exr', 'tga'],
            'video' => ['3g2', '3gp', 'avi', 'flv', 'h264', 'm4v', 'mkv', 'qt', 'mov', 'mp4', 'mpg', 'mpeg', 'rm', 'swf', 'vob', 'wmv', 'ogg', 'ogv', 'webm'],
            'audio' => ['au', 'aif', 'aiff', 'cda', 'mid', 'midi', 'mp3', 'm4a', 'mpa', 'ogg', 'wav', 'wma', 'wpl'],
            'apps' => ['apk', 'exe', 'bat', 'bin', 'cgi', 'pl', 'gadget', 'com', 'jar', 'msi', 'py', 'wsf'],
            'programming' => ['c', 'cgi', 'pl', 'class', 'cpp', 'cs', 'h', 'java', 'php', 'py', 'sh', 'swift', 'vb'],
            'internet' => ['asp', 'aspx', 'cer', 'cfm', 'cgi', 'pl', 'css', 'htm', 'html', 'js', 'jsp', 'part', 'php', 'py', 'rss', 'xhtml'],
            'system' => ['bak', 'cab', 'cfg', 'cpl', 'cur', 'dll', 'dmp', 'drv', 'icns', 'ico', 'ini', 'lnk', 'msi', 'sys', 'tmp', 'vdi', 'raw'],
            'data' => ['csv', 'dat', 'db', 'dbf', 'log', 'mdb', 'sav', 'sql', 'tar', 'xml'],
            'disc' => ['bin', 'dmg', 'iso', 'toast', 'vcd', 'img'],
            'compressed' => ['7z', 'arj', 'deb', 'pkg', 'rar', 'rpm', 'tar', 'gz', 'z', 'zip'],
            'trash' => ['old', 'trash', 'tmp', 'temp', 'junk', 'recycle', 'delete', 'deleteme', 'clean', 'remove']
        ];
        // extra fields for search results and view file/dir info pages
        // key is description for field and value is ES field name
        // Example:
        //const EXTRA_FIELDS = [
        //    'Date Changed' => 'ctime'
        //];
        const EXTRA_FIELDS = [];
        // Maximum number of indices to load by default, indices are loaded in order by creation date
        // setting this too high can cause slow logins and other timeout issues
        // This setting can bo overridden on indices page per user and stored in maxindex cookie
        // If MAX_INDEX is set higher than maxindex browser cookie, the cookie will be set to this value
        const MAX_INDEX = 250;
        // time in seconds for index info to be cached, clicking reload indices forces update
        const INDEXINFO_CACHETIME = 600;
        // time in seconds to check Elasticsearch for new index info
        const NEWINDEX_CHECKTIME = 10;
        // sqlite database file path
        const DATABASE = '../diskoverdb.sqlite3';
    }
{% endmacro %}
