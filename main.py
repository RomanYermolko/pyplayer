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
import datetime

from tkinter import *

#internal files
from authorization import *
from dbg import dbg

appWin = Tk();
appWin.title('VK pyplayer v0.0.1');

# disable resizing by user
appWin.resizable(width=False,height=False);
appWin.minsize(width=200, height=550);

save_input_user_password = IntVar();
owner_comp_list = IntVar();
repeat_current = IntVar();

search_str = StringVar();
user_str   = StringVar();
pwd_str    = StringVar();

user     = '';
password = '';
player_state='Active';
curplay_idx = 0;

def download_song(song_data):
    urllib.request.urlretrieve(song_data['url'],
            song_data['artist'] + '-' + song_data['title'] + '.mp3');
    set_player_state('Active');
    

def play_song(song_data, player, vlc_inst):
    try:
        media = vlc_inst.media_new(song_data['url']);
    except Exception as e:
        dbg('Exception : ', e);
        return -1;

# debug template and reserve for future 
#    dbg('Playing : ' + song_data['artist'] + '-' +
#        song_data['duration'] + '   ' + str(song_data['duration'] / 60));

    media.get_mrl();
    player.set_media(media);

    player.play();
    playing = set([1,2,3,4]); #some strange shit. Just copied :)

    time.sleep(1);
 
    while True:
        state = player.get_state();
        if (state not in playing) or \
           (get_player_state() != 'Active' and \
            get_player_state() != 'Download'):
               player.stop();
               break;
        if get_player_state() == 'Download':
            download_song(song_data);
        continue;
    return 0;

def set_player_state(state):
    global player_state;
    player_state = state;

def get_player_state():
    global player_state;
    return player_state;

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
    global music_list;
    global curplay_idx;
    
    playlist = [ url['url'] for url in music_list]
    limit = len(music_list)

    vlc_inst = vlc.Instance();
    player = vlc_inst.media_player_new();

    while (curplay_idx < limit):
        set_player_state('Active');

        play_song(music_list[curplay_idx], player, vlc_inst);

        while True:
            player_state = get_player_state();
            if player_state == 'Stop':
                player.stop();
                return 0;
            elif player_state == 'Next':
                break;
            elif player_state == 'Prev':
                if not repeat_current.get():
                    curplay_idx -= 2;
                break;
            elif player_state == 'Changed':
                break;
            continue;
        if not repeat_current.get():
            curplay_idx += 1;
    return 1;


PlayListBox = None;
music_list = None;

def play_selected(event):
    global PlayListBox;
    global curplay_idx;
    set_player_state('Changed');
    time.sleep(0.5);
    curplay_idx = PlayListBox.curselection()[0] - 1;
    set_player_state('Active');
    return;

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
    access_token, my_id = get_token(user, password);
    if access_token == 0:
        return 0;


    session = vk.Session()
    api = vk.API(session, access_token=access_token)

    if owner_comp_list.get():
        music_response=api.audio.get(owner_id=my_id, count=1000, access_token=access_token);
    else:
        music_response = api.audio.search(count=1000, access_token=access_token, q=search_str.get());
#music_response = api.audio.getCount(owner_id=26529194, count=2, access_token=access_token);
     
    if not PlayListBox:
        PlayListBox = Listbox(appWin, selectmode=SINGLE, width=90, height=25);
        PlayListBox.grid(row=5, column=0,columnspan=5);
        yscroll = Scrollbar(command=PlayListBox.yview, orient=VERTICAL);
        yscroll.grid(row=5, column=5);
        PlayListBox.configure(yscrollcommand=yscroll.set);
        PlayListBox.bind('<Double-Button-1>', play_selected);
    PlayListBox.delete(0, PlayListBox.size());

    music_list = music_response[1:];

    for i in range(0, len(music_list)):
        PlayListBox.insert(i + 1, '[' + '{0: ^5}'.format(i) +'] ' + 
                music_list[i]['artist'] + ' - ' + music_list[i]['title'] + '  ' + 
                str(datetime.timedelta(seconds=music_list[i]['duration'])));


    Process = threading.Thread(target=process_playlist);
    Process.start();


def stop():
    set_player_state('Stop');

def pnext():
    set_player_state('Next');

def pprev():
    set_player_state('Prev');

def download():
    set_player_state('Download');


wrap_around = Checkbutton(appWin, text='Repeat current', variable=repeat_current,
                            onvalue=1, offvalue=0);
wrap_around.grid(row=4, column=1);

owner_compositions = Checkbutton(appWin, text='Owner compositions', variable=owner_comp_list,
                            onvalue=1, offvalue=0);
owner_compositions.grid(row=4, column=2);

#login
login_label = Label(appWin, text='User ');
login_label.grid(row=0, column=0);
login_entry = Entry(appWin, bd=4, textvariable=user_str);
login_entry.grid(row=0, column=1);

#password
pwd_label = Label(appWin, text='Password ');
pwd_label.grid(row=1, column=0);
pwd_entry = Entry(appWin, bd=4, textvariable=pwd_str, show="*");
pwd_entry.grid(row=1, column=1);

#save login + password?
save_credentials = Checkbutton(appWin, text='Save credentials', variable=save_input_user_password,
                            onvalue=1, offvalue=0);
save_credentials.grid(row=0, column=2 );


search_label = Label(appWin, text='Search ');
search_label.grid(row= 2, column=0);
search_entry = Entry(appWin, bd=4, textvariable=search_str);
search_entry.grid(row= 2, column=1);

start_button = Button(appWin, command=vk_music_main, text='Start'); 
stop_button  = Button(appWin, command=stop, text='Stop'); 
next_button  = Button(appWin, command=pnext, text='Next');
prev_button  = Button(appWin, command=pprev, text='Prev'); 
download_button = Button(appWin, command=download, text='Download'); 

start_button.grid(row=3, column=0);
stop_button.grid(row=3, column=1);
prev_button.grid(row=3, column=2);
next_button.grid(row=3, column=3);
download_button.grid(row=4, column=0);
appWin.mainloop();


