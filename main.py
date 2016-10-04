import vlc
import vk
import requests
import json
import time 
import urllib
import tty
import sys
import termios
import turtle
import threading

from tkinter import *

#internal files
from authorization import *
from dbg import dbg

appWin = Tk();

save_input_user_password = IntVar();

search_str = StringVar();
user_str   = StringVar();
pwd_str    = StringVar();

user     = '';
password = '';
player_state='Active';

def get_credentials(in_user, in_pwd):
    #check default
    dbg('Default credentials are used');
    user, password = get_def_user_password_pair();

    if in_user == '' or in_pwd == '':
        return user, password;

    if user == '' or password == '':
        return in_user, in_pwd;

    if in_user != user and in_pwd != password:
        if save_input_user_password.get():  
            dbg('Store credentials option was entered');
            store_user_password_pair(in_user, in_pwd);

    return in_user, in_pwd;

def process_playlist():
#downloading
#for song in music_response[1:]:
#    urllib.request.urlretrieve(song['url'], song['artist'] + '-' + song['title'] + '.mp3');
    global PlayListBox;
    global music_list;
    global player_state;

    print('reached...');
    playlist = [ url['url'] for url in music_list]
    limit = len(music_list)
    i = 0;

    vlc_inst = vlc.Instance();
    player = vlc_inst.media_player_new();

    while (i < limit):
        player_state = 'Active';
        PlayListBox.activate(i);
        mp = playlist[i];
        try:
            media = vlc_inst.media_new(mp);
        except Exception as e:
            dbg('Exception : ', e);
            i += 1;
            continue;

        media.get_mrl();
        player.set_media(media);

        player.play();
        playing = set([1,2,3,4]);

        time.sleep(1);
        
        while True:
            state = player.get_state();
            if state not in playing:
                    break;
            if player_state == 'Stop':
                player.stop();
                return 0;
            elif player_state == 'Download':
                urllib.request.urlretrieve(mp, music_list[i]['artist'] + '-' +
                        music_list[i]['title'] + '.mp3');
                player_state = 'Active';
            elif player_state == 'Next':
                break;
            continue;
        i += 1;
    return 1;


PlayListBox = None;
music_list = None;

def vk_music_main(a=None):
    global PlayListBox;
    global player_state;
    global music_list;

    if player_state == 'Active':
        player_state = 'Stop';
        time.sleep(1);
    player_state='Active'; 
    #get Credentials window
    user = user_str.get();
    password = pwd_str.get();

    user, password = get_credentials(user, password);
    if not user or not password:
        print("No credentials. Good buy!");
        return 0;

    #get access_token to use VK API
    access_token = get_token(user, password);
    if access_token == 0:
        return 0;

    session = vk.Session()
    api = vk.API(session, access_token=access_token)

#music_response=api.audio.get(owner_id=my_id, count=10, access_token=access_token);
    music_response = api.audio.search(count=15, access_token=access_token, q=search_str.get());
#music_response = api.audio.getCount(owner_id=26529194, count=2, access_token=access_token);
     
    if not PlayListBox:
        PlayListBox = Listbox(appWin, selectmode=SINGLE, width=50);
    PlayListBox.delete(0, PlayListBox.size());

    music_list = music_response[1:];

    for i in range(0, len(music_list)):
        PlayListBox.insert(i + 1, 
                music_list[i]['artist'] + ' - ' + music_list[i]['title']);

    PlayListBox.pack(side=BOTTOM);
   # PlayListBox.after(1);

    Process = threading.Thread(target=process_playlist);
    Process.start();


def stop():
    global player_state;
    player_state = 'Stop';

def pnext():
    global player_state;
    player_state = 'Next';

def download():
    global player_state;
    player_state = 'Download';



save_credentials = Checkbutton(appWin, text='Save credentials', variable=save_input_user_password,
                            onvalue=1, offvalue=0);
save_credentials.pack(side=BOTTOM);

login_label = Label(appWin, text='User ');
login_label.pack(side=LEFT);
login_entry = Entry(appWin, bd=4, textvariable=user_str);
login_entry.pack(side=LEFT);

pwd_label = Label(appWin, text='Password ');
pwd_label.pack(side=LEFT);
pwd_entry = Entry(appWin, bd=4, textvariable=pwd_str, show="*");
pwd_entry.pack(side=LEFT);

search_label = Label(appWin, text='Search ');
search_label.pack(side=LEFT);
search_entry = Entry(appWin, bd=4, textvariable=search_str);
search_entry.pack(side=LEFT);

start_button = Button(appWin, command=vk_music_main, text='Start'); 
stop_button = Button(appWin, command=stop, text='Stop'); 
next_button = Button(appWin, command=pnext, text='Next'); 
download_button = Button(appWin, command=download, text='Download'); 

start_button.pack();
stop_button.pack();
next_button.pack();
download_button.pack();
appWin.mainloop();


