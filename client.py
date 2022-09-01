import socket
import threading
import tkinter
import  tkinter.scrolledtext
import datetime
import random
from tkinter import simpledialog


Host=socket.gethostbyname(socket.gethostname())
Port=35353

freq = 44100
duration = 5

class Client:

    def __init__(self, host, port):

        self.sock =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host,port))

        self.word=["tiger","worm","dog","cat","bird","lion","monkey","squid"]

        msg=tkinter.Tk()
        msg.withdraw()

        self.nickname=simpledialog.askstring("Nickname","Please choose a nickname",parent=msg)

        self.game_started=False
        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)


        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win=tkinter.Tk()
        self.win.configure(bg="#17202A")
        self.win.title("Chat Window")

        self.chat_label = tkinter.Label(self.win, text="Chat:")
        self.chat_label.config(font=("Arial",12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area=tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state="disabled")

        self.msg_label = tkinter.Label(self.win, text="Chat:", bg="white")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20,pady=5)

        self.send_button = tkinter.Button(self.win,text="Send",command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)

        self.play_button = tkinter.Button(self.win, text="Play", command=self.play)
        self.play_button.config(font=("Arial", 12))
        self.play_button.pack(padx=20, pady=5)


        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def write(self):
        text_time = datetime.datetime.now().strftime(("%H:%M:%S"))
        message= f"{self.nickname} {text_time}: {self.input_area.get('1.0','end')}"+"\n"
        self.sock.send(message.encode("utf-8"))
        self.input_area.delete('1.0','end')


    def stop(self):
        self.running=False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                message=self.sock.recv(1024)
                if message == 'NICK':
                    self.sock.send(self.nickname.encode('utf-8'))
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end',message)
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')
            except ConnectionAbortedError:
                break
            except:
                print("Error")
                self.sock.close()
                break

    def play(self):
        self.stop_gui()
        self.turn=3

        self.win2 = tkinter.Tk()
        self.win2.configure(bg="#17202A")
        self.win2.title("Game Window")


        self.text_area = tkinter.scrolledtext.ScrolledText(self.win2)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state="disabled")

        self.start_button = tkinter.Button(self.win2, text="Start Game", command=self.start_game)
        self.start_button.config(font=("Arial", 12))
        self.start_button.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win2, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.guess_button = tkinter.Button(self.win2, text="Guess", command=self.guess)
        self.guess_button.config(font=("Arial", 12))
        self.guess_button.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win2, text="Send", command=self.write)
        self.send_button.config(font=("Arial", 12))
        self.send_button.pack(padx=20, pady=5)

        self.win2.protocol("WM_DELETE_WINDOW", self.stop_game)

        self.win2.mainloop()

    def start_game(self):

        self.game_started=True

        self.turn=3

        self.chosen=self.word[random.randint(0,len(self.word)-1)]

        self.secret=["-" if each != " " else " " for each in self.chosen]

        self.text_area.config(state='normal')
        self.text_area.insert('end','Get ready for playing HANGMAN!!!\nYou have 3 chance to find correct word\nYour word is:(Words are animal species)\n')
        self.text_area.insert('end',self.secret)
        self.text_area.yview('end')
        self.text_area.config(state='disabled')

    def stop_gui(self):
        self.win.destroy()

    def stop_game(self):

        self.win2.destroy()
        self.gui_loop()



    def guess(self):

        if self.game_started:
            guess = self.input_area.get('1.0', 'end')
            guess=guess[0]

            if self.turn==0:
                self.turn=self.turn-1
                self.text_area.config(state='normal')
                self.text_area.insert('end', self.chosen+"\nYou are out of turns!\nIf you want to continue playing press START GAME\nIf you want to quit press GUESS or CROSS\n")
                self.text_area.yview('end')
                self.text_area.config(state='disabled')

                #self.stop_game()


            elif self.turn>0:
                self.control=0

                for j in range(len(self.chosen)):
                    if self.chosen[j]==guess:
                        self.control=1
                        self.secret[j]=guess

                if self.control==0:
                    self.turn = self.turn - 1
                    self.text_area.config(state='normal')
                    self.text_area.insert('end', '\nWrong choice!\nYou have ' + str(self.turn) + ' turns left\n'+guess+'\n')
                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')
                else:

                    self.text_area.config(state='normal')
                    self.text_area.insert('end', "Good choice!\n"+str(self.secret)+"\n")
                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')

                self.count=0
                for i in self.secret:
                    if i=="-":
                        self.count+=1
                if self.count==0:
                    self.text_area.config(state='normal')
                    self.text_area.insert('end', "You have beaten me!\nNOOOOOOOOOOOOOOOOOOOO!\nIf you want to continue playing press START GAME\nIf you want to quit press GUESS or CROSS\n")
                    self.text_area.yview('end')
                    self.text_area.config(state='disabled')
                    self.turn=-1

            else:
                self.stop_game()

        else:
            self.text_area.config(state='normal')
            self.text_area.insert('end',
                                  "Press Start Game!\n")
            self.text_area.yview('end')
            self.text_area.config(state='disabled')
            self.turn = -1

        self.input_area.delete('1.0', 'end')








client = Client(Host, Port)
