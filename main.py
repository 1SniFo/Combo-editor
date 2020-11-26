import yaml
from os import rename, path, makedirs
from datetime import datetime
import random
from colorama import Fore
from multiprocessing.dummy import Pool


class main:
    def __init__(self):
        # Logo
        self.first_temp: list = []
        self.second_temp: list = []
        print(Fore.YELLOW + """
        ╭━━━╮     ╭╮          ╭╮╭╮
        ┃╭━╮┃     ┃┃          ┃┣╯╰╮
        ┃┃ ╰╋━━┳╮╭┫╰━┳━━╮╭━━┳━╯┣╮╭╋━━┳━╮
        ┃┃ ╭┫╭╮┃╰╯┃╭╮┃╭╮┃┃┃━┫╭╮┣┫┃┃╭╮┃╭╯
        ┃╰━╯┃╰╯┃┃┃┃╰╯┃╰╯┃┃┃━┫╰╯┃┃╰┫╰╯┃┃
        ╰━━━┻━━┻┻┻┻━━┻━━╯╰━━┻━━┻┻━┻━━┻╯\n""")
        # ------------------------> Load config.yml <------------------------
        try:
            with open("Config.yml", encoding="utf-8") as file:
                config = yaml.full_load(file)['main']
                # ------------------------> main <------------------------
                self.threads = int(config['threads'])
                self.colors = bool(config['color'])
                # ------------------------> Read <------------------------
                self.read_character = str(config['Read']['character'])
                self.read_position = int(config['Read']['position'])
                self.read_encode = str(config['Read']['encode'])
                # ------------------------> Text <------------------------
                self.duplicates = bool(config['Duplicates'])
                self.reverse = bool(config['Reverse'])
                self.isHot = bool(config['Hot'])
                # ------------------------> Length <------------------------
                self.length_enable = bool(config['Length']['enable'])
                self.length_minimum = int(config['Length']['minimum'])
                # ------------------------> Password <------------------------
                self.edit_enable = bool(config['Edit']['enable'])
                self.edit_title = bool(config['Edit']['title'])
                self.edit_chance = int(config['Edit']['chance'])
                self.edit_password = str(config['Edit']['password'])
                self.edit_keywords = list(config['Edit']['keywords'])
                # ------------------------> Whitelist <------------------------
                self.whitelist_enable = bool(config['Whitelist']['enable'])
                self.whitelist_keywords = list(config['Whitelist']['keywords'])
                # ------------------------> Blacklist <------------------------
                self.blacklist_enable = bool(config['Blacklist']['enable'])
                self.blacklist_keywords = list(config['Blacklist']['keywords'])
                file.close()
        except Exception as Error:
            print(self.msg("Error", f"Loading config at {Error}", Fore.RED))
            exit()
        # ------------------------> values & Checking <------------------------
        self.count = 0
        if self.read_position < 0:
            print(self.msg("Config", "Position has to be higher or equal to 0", Fore.YELLOW))
            exit()
        elif not 100 >= self.edit_chance >= 0:
            print(self.msg("Config", "Chance has to be higher or equal to 0", Fore.YELLOW))
            exit()
        elif not self.threads >= 1:
            print(self.msg("Config", "Threads has to be higher or equal to 1", Fore.YELLOW))
            exit()
        # ------------------------> Creating latest.txt <------------------------
        # Loading file
        if path.exists("Output/latest.txt"):
            temp: int = 1
            while True:
                old_path = f"Output/{datetime.now().date()}-{temp}.txt"
                if not path.exists(old_path):
                    rename("Output/latest.txt", str(old_path))
                    break
                else:
                    temp += 1
        else:
            if not path.exists("Output"):
                makedirs(f"Output")
        # ------------------------> Loading combo <------------------------
        with open("Combo.txt", 'r', encoding="utf-8", errors='ignore') as file:
            self.combo: list = [line.strip() for line in file.readlines()]
            file.close()
        print(self.msg("Input", f"{len(self.combo)} line(s)", Fore.RED))
        # ------------------------> Duplicates <------------------------
        if self.duplicates:
            old = len(self.combo)
            self.combo = list(dict.fromkeys(self.combo))
            print(self.msg("Duplicates", f"{old - len(self.combo)} line(s) has been removed", Fore.MAGENTA))
        # ------------------------> Reverse <------------------------
        if self.reverse:
            self.combo.reverse()
            print(self.msg("Reverse", f"Successful", Fore.LIGHTBLUE_EX))
        # ------------------------> threading <-----------------------
        if self.threads > len(self.combo):
            self.threads = len(self.combo)
        self.file = open("Output/latest.txt", "a")
        with Pool(processes=self.threads) as self.pool:
            self.pool.imap(func=self.start, iterable=self.combo)
            self.pool.close()
            self.pool.join()
        self.file.close()
        if self.isHot:
            print(self.msg("Hot", f"{len(self.first_temp)} line(s)", Fore.YELLOW))
            with open("Output/latest.txt", "w") as write:
                write.writelines(["%s\n" % item for item in (self.first_temp + self.second_temp)])
                write.close()
        print(self.msg("Output", f"Finished with {self.count} line(s)", Fore.LIGHTGREEN_EX))

    def start(self, line):
        if account := self.read(line):
            if self.check(account):
                # email & username = splitter[0]
                # password = splitter[-1]
                user = account.split(self.read_character)[0]
                password = account.split(self.read_character)[-1]
                if self.length(password):
                    if self.edit_enable:
                        password = self.edit(password)
                    if self.hot(user, password):
                        self.first_temp.append(user + self.read_character + password)
                    else:
                        if self.isHot:
                            self.second_temp.append(user + self.read_character + password)
                        else:
                            self.file.write("%s\n" % (user + self.read_character + password))
                    self.count += 1

    def hot(self, user: str, password: str):
        if self.isHot:
            if user[0].lower() == password[0].lower():
                return user + self.read_character + password
            else:
                return False
        else:
            return False

    def length(self, password):
        if self.length_enable:
            if len(password) >= self.length_minimum:
                return True
            else:
                return False
        else:
            return True

    def check(self, account: str):
        if self.whitelist_enable:
            if [x for x in self.whitelist_keywords if x in account]:
                return True
        elif self.blacklist_enable:
            if not [x for x in self.blacklist_keywords if x in account]:
                return True
        else:
            if self.whitelist_enable or self.blacklist_enable:
                return False
            else:
                return True

    def msg(self, title, msg, color):
        if self.colors:
            return f"{Fore.WHITE}| {color}{title} {Fore.WHITE}|{Fore.RESET} {msg}"
        else:
            return f"| {color} {title} | {msg}"

    def edit(self, password):
        if random.randint(0, 100) <= self.edit_chance:
            if self.edit_title:
                password = password.title()
            if not [x for x in self.edit_keywords if x in password]:
                password = self.edit_password.replace("{password}", password)
            return password
        else:
            return password

    def read(self, line: str) -> str or bool:
        account = str()
        n = 0
        for i in line.split(" "):
            if self.read_character in i:
                n += 1
                if n == self.read_position or n >= line.count(":"):
                    account = i
                    try:
                        i.encode(self.read_encode)
                    except Exception as error:
                        if not type(error) == UnicodeEncodeError:
                            print(self.msg("Error", f"{error}", Fore.RED))
                            exit()
                        n = 0
                    break
        if n == 0:
            return False
        else:
            return account


if __name__ == "__main__":
    main()
