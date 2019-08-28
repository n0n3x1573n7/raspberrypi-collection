from os.path import join

#server secret path
SERV_SECRET=join(*("server_secret".split('/')))

#certificate
CERT_FILE="server.crt"
KEY_FILE="server.key"
CERT_NAME="FTP server for raspberrypi 4"

#file
FILE_FOLDER="files"
PASS_FILE="passwd"
FILE_EXT=".enc"
